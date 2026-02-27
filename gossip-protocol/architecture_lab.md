# Cassandra Chaos Engineering Lab Architecture

## Executive Architecture Summary
This laboratory provides a deterministic, local-only distributed systems experimentation framework based on Apache Cassandra 5.0. Designed to fit within a 16GB memory footprint, it utilizes Docker Compose to orchestrate a 3-node homogeneous cluster. The architecture employs Python as the orchestration plane, bridging the DataStax Cassandra Driver (`cassandra-driver==3.29.0`) with Docker SDK for programmatic chaos injection. The lab explicitly isolates client-side measurement from server-side behavior to validate consistency models (ONE vs QUORUM) and evaluate the Phi Accrual Failure Detector during enforced network partitions and node crashes.

## Cluster Topology Diagram
```text
      [ Docker Bridge Network: cassandra-net (172.x.x.x) ]
                               │
       ┌───────────────────────┼───────────────────────┐
       │                       │                       │
 ┌─────┴─────┐           ┌─────┴─────┐           ┌─────┴─────┐
 │ Node 1    │           │ Node 2    │           │ Node 3    │
 │ (Seed)    │◄─Gossip──►│ (Seed)    │◄─Gossip──►│ (Peer)    │
 │ Port 9042 │           │ Port 9043 │           │ Port 9044 │
 └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
       │                       │                       │
       └──────────┬────────────┴──────────┬────────────┘
                  │                       │
      [ Python Load Generator ]  [ Python Chaos Injector ]
      (Writes/Reads/Validation)  (Docker API/net delay)
```

## Docker Compose Configuration
See `docker-compose.yml` for the full deployment specification. The topology strictly limits the JVM Heap (`MAX_HEAP_SIZE=1G`, `HEAP_NEWSIZE=256M`) on each node to ensure memory limits do not trigger host OOM killer on a 16GB laptop. It assigns fixed node IPs implicitly via host forwarding on ports `9042`, `9043`, and `9044`.

## Cassandra Configuration Notes
We utilize environmental overrides rather than custom `cassandra.yaml` files for deterministic portability.
1. **`CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch`**: Required for proper IP-based routing and rack awareness even in local setups, heavily utilized by the Python driver's load balancing policies.
2. **Cluster & Seeds**: `CASSANDRA_CLUSTER_NAME` must match across all nodes. Seeds are explicitly mapped to Node 1 and Node 2. Node 3 will bootstrap by contacting them.
3. No vnodes overrides needed for local testing, though vnodes (`num_tokens=16`) are standard in v5.0.
4. **Deprecated configs avoided**: The V5 Native Protocol replaces `<numfailures>` error payloads with `<reasonmap>`, modifying how the driver parses Read/Write failures. 

## Python Experiment Framework
The lab uses `experiment_runner.py` (provided separately) that implements context managers for the Cassandra sessions, utilizing `DCAwareRoundRobinPolicy`. The core tests explicitly toggle `ConsistencyLevel.ONE` and `ConsistencyLevel.QUORUM`.

## Failure Injection Module
The lab utilizes `chaos_injector.py` leveraging the Python `docker` SDK to dynamically execute:
1. `docker stop cassandra-node2` (Process Crash).
2. `docker network disconnect cassandra-net cassandra-node3` (Partition).
3. `docker exec cassandra-node1 tc qdisc add dev eth0 root netem delay 200ms` (Latency Injection).

## Metrics & Logging Design
The framework instruments the Python driver's `ResponseFuture` to log execution metrics asynchronously into a pandas-compatible CSV format:
* `timestamp` (UTC ISO 8601, client-generated)
* `operation` (READ/WRITE)
* `consistency_level` (ONE/QUORUM/ALL)
* `latency_ms` (Time to receive driver acknowledgment)
* `status` (SUCCESS/TIMEOUT/UNAVAILABLE)
* `coordinator_ip` (Node that serviced the request)
* `client_timestamp` (explicit internal Cassandra tracking)

## Experiment Phases
1. **Phase 1: Baseline Convergence**
   - **Action:** `docker-compose up -d`. Wait for Gossip stabilization. Issue 1,000 QUORUM writes. Read uniformly.
   - **Metric:** P99 write/read latency (Expected < 5ms).
2. **Phase 2: Single Node Crash & Quorum Geometry**
   - **Action:** Kill Node 3. Write QUORUM. Read QUORUM.
   - **Metric:** Verify 100% availability. Measure time until Phi Accrual Failure Detector flags node implicitly by observing coordinator shift in metrics logs.
3. **Phase 3: The Split Brain (Network Partition)**
   - **Action:** Isolate Node 2 from Cass-Net. Write ONE to Node 1. Write ONE to Node 2 (same row). Rejoin network. Read QUORUM.
   - **Metric:** Observe Timestamp conflict resolution. Calculate percentage of inconsistent reads prior to Read Repair.
4. **Phase 4: Hinted Handoff Observation**
   - **Action:** Pause Node 1 for 2 minutes. Write ONE to Node 2. Unpause Node 1. Read ONE from Node 1.
   - **Metric:** Measure time for Hinted Handoff playback to Node 1 via driver mismatch tracking.

## Expected Outcomes Table

| Scenario | RF | Write CL | Read CL | Availability | Consistency | Recovery Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Healthy | 3 | QUORUM | QUORUM | 100% | Strong | N/A |
| 1 Node Crash | 3 | QUORUM | QUORUM | 100% | Strong | Hinted Handoff / Read Repair |
| 2 Node Crash | 3 | QUORUM | QUORUM | 0% | N/A | Manual Bootstrap |
| 1 Node Crash | 3 | ONE | ONE | 100% | Eventual (Stale Reads possible) | Hinted Handoff |
| Net Partition | 3 | ONE | ONE | 100% (Divergent) | None | Last-Write-Wins (LWW) |
| CPU Constrained | 3 | QUORUM | QUORUM | Degraded (Timeouts) | Strong | Phi Accrual Adjustment |

## Risk & Edge Case Analysis
* **Clock Skew (LWW Hazard):** Cassandra relies on Last Write Wins (LWW) using client-provided or coordinator-provided timestamps. If the Python script instances run on different machines with untethered NTP, writes will probabilistically fail to overwrite older geographic data. (Tested via explicit `LIMIT` clock overriding in Python).
* **Phantom Reads:** If Hinted Handoffs exceed the `max_hint_window_in_ms` (default 3 hours), dropped nodes permanently lose updates unless a manual Anti-Entropy Repair (`nodetool repair`) is triggered.

## What the User Missed (Critical Additions)
1. **Coordinator Bottlenecking Awareness:** A query requires a coordinator. If you test "Node crash" by killing the node your Python script is currently attached to, the query *fails* immediately unless your driver connection policy retries on an alternate coordinator. I've explicitly coded `RetryPolicy` injections into the lab framework to combat test bias.
2. **Docker JVM Kill Traps:** 3 Cassandra instances inherently require a massive JVM memory mapping. Without exact `MAX_HEAP_SIZE` caps in local Docker, your laptop will hard-lock through swap pressure during Phase 5 (Heavy Load/Chaos).
3. **Missing Read Repair Triggers:** Consistency divergence doesn't fix itself silently. It requires explicit read paths (Read Repair) or Anti-Entropy repair. The tests now include explicit "Verification Read Sweeps" to trigger and time Read Repair.
4. **JMX/Nodetool Blindness:** You focused strictly on Python metrics. True chaotic behavior (like Hinted Handoff queue depth) cannot be measured client-side, it must be polled via `docker exec node1 nodetool statushandoff`.

## Future Expansion Path
1. **Vector Clocks / CRDTs:** Implementing external vector clock arrays inside the Cassandra `value` column to manually detect LWW overriding vs True Merge.
2. **Multi-DC Topologies:** Using `NetworkTopologyStrategy` in keyspaces to test LOCAL_QUORUM vs EACH_QUORUM consistency drops.
3. **Dynamic Snitch Testing:** Simulating disk-I/O degradation to observe Cassandra's Dynamic Endpoint Snitch artificially down-ranking the slow node before Gossip explicitly marks it dead.
