import docker
import time
import subprocess

client = docker.from_env()

class ChaosInjector:
    def __init__(self):
        self.network_name = "cassandra-net"

    def stop_node(self, node_name="cassandra-node3"):
        print(f"Injecting Fault: Stopping {node_name}")
        container = client.containers.get(node_name)
        container.stop()
        print(f"{node_name} stopped.")

    def start_node(self, node_name="cassandra-node3"):
        print(f"Healing: Starting {node_name}")
        container = client.containers.get(node_name)
        container.start()
        print(f"{node_name} started.")

    def partition_network(self, node_name="cassandra-node2"):
        print(f"Injecting Fault: Disconnecting {node_name} from {self.network_name}")
        network = client.networks.list(names=[self.network_name])[0]
        try:
            network.disconnect(node_name)
            print(f"{node_name} partitioned.")
        except Exception as e:
            print(f"Failed to disconnect: {e}")

    def heal_network(self, node_name="cassandra-node2"):
        print(f"Healing: Reconnecting {node_name} to {self.network_name}")
        network = client.networks.list(names=[self.network_name])[0]
        try:
            network.connect(node_name)
            print(f"{node_name} reconnected.")
        except Exception as e:
            print(f"Failed to connect: {e}")

    def inject_latency(self, node_name="cassandra-node1", delay="200ms"):
        print(f"Injecting Fault: Adding {delay} latency to {node_name}")
        cmd = f"docker exec -u root {node_name} apt-get update && apt-get install -y iproute2"
        subprocess.run(cmd, shell=True)
        cmd_delay = f"docker exec -u root {node_name} tc qdisc add dev eth0 root netem delay {delay}"
        subprocess.run(cmd_delay, shell=True)
        print(f"Latency injected.")

    def heal_latency(self, node_name="cassandra-node1"):
        print(f"Healing: Removing latency from {node_name}")
        cmd = f"docker exec -u root {node_name} tc qdisc del dev eth0 root netem"
        subprocess.run(cmd, shell=True)
        print(f"Latency removed.")

if __name__ == "__main__":
    injector = ChaosInjector()
    
    # Phase 2 Example - Node Crash
    print("--- Phase 2: Node Crash Example ---")
    injector.stop_node("cassandra-node3")
    time.sleep(10)
    injector.start_node("cassandra-node3")

    # Phase 3 Example - Network Partition
    print("\n--- Phase 3: Network Partition Example ---")
    injector.partition_network("cassandra-node2")
    time.sleep(10)
    injector.heal_network("cassandra-node2")
