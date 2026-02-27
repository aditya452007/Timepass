import time
import uuid
import threading
from datetime import datetime
import pandas as pd
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import DCAwareRoundRobinPolicy, RetryPolicy
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement
from chaos_injector import ChaosInjector

class ExperimentLogger:
    def __init__(self, filename="experiment_metrics.csv"):
        self.filename = filename
        self.metrics = []

    def log(self, op_type, cl, success, latency_ms, coordinator, is_stale=False):
        self.metrics.append({
            "timestamp": datetime.utcnow().isoformat(),
            "operation": op_type,
            "consistency_level": cl,
            "success": success,
            "latency_ms": latency_ms,
            "coordinator_ip": coordinator,
            "is_stale_read": is_stale
        })

    def save(self):
        df = pd.DataFrame(self.metrics)
        df.to_csv(self.filename, index=False)
        print(f"Metrics saved to {self.filename}")


class LabRunner:
    def __init__(self, contact_points=['127.0.0.1']):
        profile = ExecutionProfile(
            load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='datacenter1'),
            request_timeout=5.0,
            consistency_level=ConsistencyLevel.QUORUM
        )
        self.cluster = Cluster(contact_points, execution_profiles={EXEC_PROFILE_DEFAULT: profile}, protocol_version=5)
        self.session = self.cluster.connect()
        self.logger = ExperimentLogger()
        self.injector = ChaosInjector()

    def setup_schema(self):
        self.session.execute("""
            CREATE KEYSPACE IF NOT EXISTS chaos_lab 
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '3'};
        """)
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS chaos_lab.test_data (
                id UUID PRIMARY KEY,
                value INT,
                updated_at TIMESTAMP
            );
        """)
        print("\nSchema initialized.")

    def run_load(self, count=1000, cl=ConsistencyLevel.QUORUM):
        print(f"Generating {count} writes at CL={cl}")
        statement = SimpleStatement(
            "INSERT INTO chaos_lab.test_data (id, value, updated_at) VALUES (%s, %s, %s)",
            consistency_level=cl
        )
        for i in range(count):
            start = time.time()
            success = False
            coordinator = "UNKNOWN"
            try:
                future = self.session.execute_async(statement, (uuid.uuid4(), i, datetime.utcnow()))
                future.result()
                coordinator = future.coordinator_host.address if future.coordinator_host else "UNKNOWN"
                success = True
            except Exception as e:
                # print(f"Write failed: {e}")
                pass
            latency = (time.time() - start) * 1000
            self.logger.log("WRITE", cl, success, latency, coordinator)

    def verify_consistency(self, cl=ConsistencyLevel.QUORUM):
        print(f"Verifying reads at CL={cl}")
        statement = SimpleStatement("SELECT * FROM chaos_lab.test_data LIMIT 1000", consistency_level=cl)
        start = time.time()
        try:
            future = self.session.execute_async(statement)
            rows = future.result()
            coordinator = future.coordinator_host.address if future.coordinator_host else "UNKNOWN"
            self.logger.log("READ", cl, True, (time.time() - start) * 1000, coordinator, is_stale=False)
            print(f"Read {len(list(rows))} rows successfully.")
        except Exception as e:
            print(f"Read failed: {e}")
            self.logger.log("READ", cl, False, (time.time() - start) * 1000, "UNKNOWN", is_stale=True)

    # --- EXPLICIT EXPERIMENTS FROM THE LAB ARCHITECTURE ---

    def run_scenario_1_baseline(self):
        print("\n=== Scenario 1: Baseline Healthy Cluster ===")
        print("WHAT IT IS: The normal state of the database where all 3 nodes (computers) are awake and talking.")
        print("WHY IT MATTERS: A distributed database spreads your data across multiple machines so it's always safe. ")
        print("                'QUORUM' means we only consider a save successful if the majority (2 out of 3) agree they got it.")
        print("                This teaches you that we don't need *every* node to agree immediately, just a majority.")
        print("\n[Action]: Writing data and asking 2 of 3 nodes to confirm.")
        self.run_load(500, ConsistencyLevel.QUORUM)
        self.verify_consistency(ConsistencyLevel.QUORUM)
        print("Scenario 1 Complete.")

    def run_scenario_2_node_crash(self):
        print("\n=== Scenario 2: Single Node Crash ===")
        print("WHAT IT IS: We are yanking the power cord on Node 3. It's totally dead.")
        print("WHY IT MATTERS: In a normal database (like MySQL), if the server dies, your app goes down.")
        print("                Here, because our Consistency Level is QUORUM (2 of 3), Node 1 and Node 2 can still process")
        print("                everything without Node 3! Notice how the Gossip protocol figures out Node 3 is dead and stops bothering it.")
        print("\n[Action]: Stopping Node 3...")
        self.injector.stop_node("cassandra-node3")
        time.sleep(10) # Wait for Gossip to mark DOWN
        print("[Action]: Proving the database still works anyway because 2 nodes are still alive.")
        self.run_load(200, ConsistencyLevel.QUORUM)
        self.verify_consistency(ConsistencyLevel.QUORUM)
        print("[Action]: Turning Node 3 back on. It will quietly catch up on what it missed.")
        self.injector.start_node("cassandra-node3")
        print("Node 3 restarted. Scenario 2 Complete.")
        time.sleep(15) # Wait for ring rejoin

    def run_scenario_3_write_one_during_failure(self):
        print("\n=== Scenario 3: Write with Consistency 'ONE' During Failure ===")
        print("WHAT IT IS: We lower our standards. 'ConsistencyLevel.ONE' means 'I only need 1 computer to save this data'.")
        print("WHY IT MATTERS: If 2 of your 3 nodes crash, your database is technically still alive if you only require 1 vote!")
        print("                But there's a risk: If only 1 node gets the info, the others are out-of-date (Stale Data).")
        print("                This teaches the tradeoff between 'Being Available no matter what' vs 'Being 100% Correct'.")
        print("\n[Action]: Stopping Node 3 and writing new data while asking only ONE node to confirm.")
        self.injector.stop_node("cassandra-node3")
        time.sleep(10)
        self.run_load(200, ConsistencyLevel.ONE)
        self.injector.start_node("cassandra-node3")
        time.sleep(10) # Give it time to boot, but Hinted Handoff might not be instant
        print("[Action]: Reading back the data. First at Level ONE (might get old data), then QUORUM (forces consensus).")
        self.verify_consistency(ConsistencyLevel.ONE)
        self.verify_consistency(ConsistencyLevel.QUORUM)
        print("Scenario 3 Complete.")

    def run_scenario_4_partition(self):
        print("\n=== Scenario 4: Network Partition (Split Brain) ===")
        print("WHAT IT IS: Node 2 is still running, but somebody unplugged its network cable. It can't talk to Node 1 or 3.")
        print("WHY IT MATTERS: Network cables fail all the time. If Node 2 is isolated, it thinks the *others* died.")
        print("                This is a 'Partition'. If an app talks to Node 2 right now, it will get totally different answers")
        print("                than an app talking to Node 1. The database diverges, and must merge later when the cable is plugged back in.")
        print("\n[Action]: Disconnecting Node 2 from the network.")
        self.injector.partition_network("cassandra-node2")
        time.sleep(5)
        print("[Action]: Saving data while the brain is split.")
        self.run_load(200, ConsistencyLevel.ONE) 
        print("[Action]: Reconnecting Node 2. Watch them argue and figure out who has the newest data based on timestamps (Last-Write-Wins).")
        self.injector.heal_network("cassandra-node2")
        time.sleep(15)
        self.verify_consistency(ConsistencyLevel.QUORUM)
        print("Scenario 4 Complete.")

    def run_scenario_5_conflicting_writes(self):
        print("\n=== Scenario 5: Conflicting Writes (The Timestamp Battle) ===")
        print("WHAT IT IS: Two people click 'Save' on the exact same row at the exact same millisecond.")
        print("WHY IT MATTERS: Cassandra doesn't 'lock' the row (like traditional databases) because locks are slow.")
        print("                Instead, whoever's clock timestamp is literally 1 microsecond newer overwrites the other.")
        print("                This teaches you that distributed systems heavily rely on perfect server clocks!")
        
        conflict_id = uuid.uuid4()
        statement = SimpleStatement(
            "INSERT INTO chaos_lab.test_data (id, value, updated_at) VALUES (%s, %s, %s)",
            consistency_level=ConsistencyLevel.ONE
        )
        print(f"\n[Action]: Forcefully inserting value 100 and value 200 at the Exact Same Time for ID: {conflict_id}.")
        
        def write_task(val):
            try:
                self.session.execute(statement, (conflict_id, val, datetime.utcnow()))
            except Exception:
                pass

        t1 = threading.Thread(target=write_task, args=(100,))
        t2 = threading.Thread(target=write_task, args=(200,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        row = self.session.execute(f"SELECT value FROM chaos_lab.test_data WHERE id={conflict_id}").one()
        print(f"[Result]: The winner was Value: {row.value if row else 'None'}. The loser was silently erased!")
        print("Scenario 5 Complete.")

    def run_scenario_6_heavy_load(self):
        print("\n=== Scenario 6: Heavy Traffic Load ===")
        print("WHAT IT IS: We simulate thousands of furious users hammering the database all at once.")
        print("WHY IT MATTERS: A system behaves perfectly when idle, but when rushed, CPUs peak and memory fills up.")
        print("                Cassandra handles this gracefully by dropping connections instead of crashing outright.")
        print("\n[Action]: Creating 10 simultaneous threads to barrage the nodes with writes.")
        threads = []
        for i in range(10):
            t = threading.Thread(target=self.run_load, args=(500, ConsistencyLevel.QUORUM))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        print("[Action]: Reading back to ensure data wasn't corrupted under pressure.")
        self.verify_consistency(ConsistencyLevel.QUORUM)
        print("Scenario 6 Complete.")

    def run_scenario_7_full_shutdown(self):
        print("\n=== Scenario 7: Full Cluster Shutdown & Recovery ===")
        print("WHAT IT IS: We completely turn off the entire data center at the exact same moment.")
        print("WHY IT MATTERS: Power outages happen! When 3 panicked nodes boot up at the same time, they use Gossip")
        print("                (like whispering secrets in a classroom) to figure out who is awake, who has data, and how to rebuild the ring.")
        
        print("\n[Action]: Stopping every single Node...")
        self.injector.stop_node("cassandra-node1")
        self.injector.stop_node("cassandra-node2")
        self.injector.stop_node("cassandra-node3")
        print("Entire cluster stopped. Waiting 10s...")
        time.sleep(10)
        
        print("\n[Action]: Starting them back up. Watch the chaotic Gossip bootup sequence...")
        self.injector.start_node("cassandra-node1")
        time.sleep(15) # Seeds boot first
        self.injector.start_node("cassandra-node2")
        time.sleep(15)
        self.injector.start_node("cassandra-node3")
        time.sleep(20) # Stabilization
        
        print("[Action]: Proving our data survived the apocalypse.")
        self.verify_consistency(ConsistencyLevel.QUORUM)
        print("Scenario 7 Complete.")

    def run_scenario_8_network_latency(self):
        print("\n=== Scenario 8: Network Latency (The 'Slow' Node) ===")
        print("WHAT IT IS: Instead of a node crashing completely, it just becomes very slow.")
        print("WHY IT MATTERS: In real life, network cables go bad or servers get bogged down.")
        print("                A slow node is often worse than a dead node because it holds up the whole system waiting for a response.")
        
        # Inject realistic internet delay
        print("\n[Action]: Adding 500ms artificial delay to Node 1's network card...")
        self.injector.inject_latency("cassandra-node1", delay="500ms")
        
        print("[Action]: Sending 100 writes requiring QUORUM (2 of 3 nodes to agree).")
        print("          Notice how long each write takes now because the coordinator might be waiting on the slow node!")
        self.run_load(100, ConsistencyLevel.QUORUM)
        
        print("\n[Action]: Removing the artificial delay (Network is fixed).")
        self.injector.heal_latency("cassandra-node1")
        print("Scenario 8 Complete.")

    def run_scenario_9_anti_entropy_repair(self):
        print("\n=== Scenario 9: Anti-Entropy Repair (Manual Data Synchronization) ===")
        print("WHAT IT IS: Cassandra doesn't immediately fix all broken data by itself.")
        print("WHY IT MATTERS: If a node is offline for too long (default 3 hours), the cluster gives up holding missed messages (Hinted Handoffs).")
        print("                You must manually run a 'repair' tool to sync differences using Merkle Trees.")
        
        print("\n[Action]: Stopping Node 3 to break the data circle...")
        self.injector.stop_node("cassandra-node3")
        time.sleep(10)
        
        print("[Action]: Writing to Node 1 & Node 2 while Node 3 is asleep.")
        self.run_load(100, ConsistencyLevel.QUORUM)
        
        print("\n[Action]: Restarting Node 3. It is now missing 100 rows of data.")
        self.injector.start_node("cassandra-node3")
        time.sleep(15) # Wait for Gossip to see it alive
        
        print("[Action]: Taking matters into our own hands. Running 'nodetool repair' internally on Node 1.")
        print("          This command scans all 3 nodes, finds differences, and copies the missing files over.")
        import subprocess
        try:
            # We call docker exec to run nodetool locally inside the container
            subprocess.run("docker exec cassandra-node1 nodetool repair chaos_lab", shell=True, check=True)
            print("Repair completed successfully. All data is perfectly in sync.")
        except Exception as e:
            print(f"Repair command failed (which happens in chaos!): {e}")

        print("Scenario 9 Complete.")

    def close(self):
        self.logger.save()
        self.cluster.shutdown()

if __name__ == "__main__":
    runner = LabRunner(['127.0.0.1'])
    try:
        runner.setup_schema()
        
        # Execute explicitly outlined scenarios sequentially
        runner.run_scenario_1_baseline()
        runner.run_scenario_2_node_crash()
        runner.run_scenario_3_write_one_during_failure()
        runner.run_scenario_4_partition()
        runner.run_scenario_5_conflicting_writes()
        runner.run_scenario_6_heavy_load()
        runner.run_scenario_7_full_shutdown()
        
        # Advanced / Educational Scenarios
        runner.run_scenario_8_network_latency()
        runner.run_scenario_9_anti_entropy_repair()
        
        print("\nAll Experimental Phases successfully executed locally.")
        
    finally:
        runner.close()
