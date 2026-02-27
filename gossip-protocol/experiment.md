I. Experimental Objective

We will empirically test:

Gossip-based membership & failure detection

Replication & consistency tradeoffs

Node crash recovery

Network partitions

Write conflicts

Eventual convergence

Availability under stress

We are not just “running Cassandra.”
We are simulating real production failure modes.

II. Lab Architecture (Local, No Cloud)
Cluster Topology

We will simulate:

3 Cassandra nodes

Replication factor = 3

Consistency levels: ONE, QUORUM, ALL

Logical View
          Node A
         /      \
    Node B ---- Node C

All nodes:

Independent containers

Gossip enabled (default in Cassandra)

Same cluster name

Different seeds configuration

III. Why Terminal > React Initially

React visualization is nice, but:

Adds complexity

Distracts from system behavior

Introduces client-side bias

For distributed experiments:
✔ Logs
✔ Metrics
✔ Deterministic timestamps
✔ Structured output

A Python terminal dashboard is better.

Later, we can add a web UI.

IV. Cassandra Concepts We Will Explicitly Test
1️⃣ Gossip Protocol

In Apache Cassandra:

Every node exchanges state every second

Maintains cluster membership

Detects failure using Phi Accrual Failure Detector

We will observe:

Time until node marked DOWN

Time until cluster stabilizes

2️⃣ Replication & Consistency

Cassandra uses:

Consistent hashing ring

Tunable consistency

Read/Write consistency options:

Level	Meaning
ONE	1 replica
QUORUM	majority
ALL	all replicas

Quorum rule:

R + W > RF

Ensures strong consistency.

V. Comprehensive Real-World Scenarios We Will Simulate

This is the core of your experiment.

Scenario 1: Baseline Healthy Cluster
Setup:

3 nodes running

RF = 3

Write consistency = QUORUM

Read consistency = QUORUM

Test:

Insert 10,000 records

Random updates

Random reads

Measure:

Write latency

Read latency

Consistency mismatches (should be 0)

Expected:

No data loss

Full consistency

Balanced token distribution

Scenario 2: Single Node Crash
Inject:
docker stop cassandra-node2
Observe:

Gossip marks node DOWN

Writes still succeed (QUORUM works)

Reads still succeed

Measure:

Time until node detected DOWN

Latency increase

Any failed writes?

Real-world analogy:

EC2 instance crash in production.

Expected:
✔ High availability
✔ No single point of failure

Scenario 3: Write with Consistency ONE During Failure

Change write consistency to ONE.

Now:

Kill 1 node

Continue writes

Later:

Restart node

Observe:

Does restarted node have missing data?

Does hinted handoff repair?

How long until convergence?

Expected:
⚠ Temporary inconsistency
✔ Eventual repair

Scenario 4: Network Partition

Simulate:

docker network disconnect

Partition:
Node A isolated from B & C.

Now:

Writes on A

Writes on B+C

After reconnection:

Which data wins?

Timestamp-based conflict resolution?

Data loss?

This simulates:

Cross-AZ network split

Real-world cloud failure

Scenario 5: Conflicting Writes

Simultaneously:

Node A writes key=42 value=100

Node B writes key=42 value=200

Same timestamp window.

Cassandra uses:

Last write wins (timestamp-based)

Observe:

Which value survives?

Is data logically correct?

Why vector clocks are superior?

Scenario 6: Heavy Load

Simulate:

100k writes

100k reads

Concurrent threads

Measure:

CPU

Memory

Write latency

Timeout errors

This simulates:

Traffic spike

Flash sale

Viral event

Scenario 7: Full Cluster Shutdown & Recovery

Stop all nodes.

Restart sequentially.

Observe:

Gossip bootstrap

Rejoining ring

Data integrity

VI. Metrics We Will Track

You must log:

Timestamp

Operation type

Consistency level

Success/Failure

Latency (ms)

Returned value

Expected value

Then calculate:

% inconsistent reads

Convergence time

Repair time

Availability rate

VII. Data Model for Testing

Simple table:

CREATE TABLE test_data (
    id UUID PRIMARY KEY,
    value INT,
    updated_at TIMESTAMP
);

We will:

Insert

Update randomly

Read repeatedly

VIII. Failure Injection Strategy

From Python:

Random node kill

Random consistency change

Artificial delay

Burst traffic

We will design it like chaos engineering (Netflix style).

Reference:
Netflix pioneered Chaos Engineering.

IX. Expected System Behaviors (What You Should See)
Scenario	Availability	Consistency	Recovery
Healthy	100%	Strong (QUORUM)	N/A
Node crash	High	Strong	Fast
Write ONE + crash	High	Weak	Eventual
Partition	Medium	Divergent	Conflict merge
Heavy load	Degrades	Depends	Stable
X. What This Teaches You Deeply

You will understand:

Why distributed systems are probabilistic

Why strong consistency is expensive

Why gossip scales O(log n)

Why quorum math matters

Why timestamp-based conflict resolution is dangerous

XI. Experimental Phases Plan

Phase 1 → Setup & healthy baseline
Phase 2 → Controlled node failure
Phase 3 → Consistency tuning
Phase 4 → Network partition
Phase 5 → Load & chaos

XII. Critical Warning

Gossip protocol:

Does NOT:

Replicate user data directly

Guarantee instant consistency

It:

Synchronizes cluster state

Detects failures

Helps repair

XIII. Next Step

Before writing code, we must finalize:

Cluster topology (3 nodes or 5?)

Replication factor

Python driver choice

Logging format

Failure injection automation level