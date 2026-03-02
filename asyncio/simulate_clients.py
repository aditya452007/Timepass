import socket
import time
import threading

SERVER_ADDRESS = ('127.0.0.1', 8000)

def simulate_normal_request(client_id):
    """Scenario 1: A normal quick HTTP request"""
    print(f"[Client {client_id}] Starting Normal Request...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(SERVER_ADDRESS)
        request = f"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\nClient {client_id}"
        sock.sendall(request.encode('utf-8'))
        
        response = sock.recv(1024)
        print(f"[Client {client_id}] Received: {response.decode('utf-8').splitlines()[0]}")
        sock.close()
        print(f"[Client {client_id}] Finished Normal Request.")
    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")

def simulate_slow_client(client_id):
    """Scenario 2: A client that connects but sends data very slowly (Slowloris style)"""
    print(f"[Client {client_id}] Starting Slow Request...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(SERVER_ADDRESS)
        
        # Send first part
        sock.sendall(b"GET / HTTP/1.1\r\n")
        print(f"[Client {client_id}] Sent part 1, sleeping for 2 seconds...")
        time.sleep(2) # The server event loop is NOT blocked during this time!
        
        # Send second part
        sock.sendall(b"Host: 127.0.0.1\r\n\r\n")
        print(f"[Client {client_id}] Sent part 2, waiting for response...")
        
        response = sock.recv(1024)
        print(f"[Client {client_id}] Received: {response.decode('utf-8').splitlines()[0]}")
        sock.close()
        print(f"[Client {client_id}] Finished Slow Request.")
    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")

def simulate_abrupt_disconnect(client_id):
    """Scenario 3: A client connects and immediately closes the connection without sending data"""
    print(f"[Client {client_id}] Starting Abrupt Disconnect...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(SERVER_ADDRESS)
        print(f"[Client {client_id}] Connected. Now immediately closing...")
        sock.close() # Close without sending anything
        print(f"[Client {client_id}] Finished Abrupt Disconnect.")
    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")

def simulate_connection_reset(client_id):
    """Scenario 4: A client forcefully resets the connection (RST packet)"""
    print(f"[Client {client_id}] Starting Connection Reset...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set SO_LINGER to 0 to send a TCP RST instead of a graceful FIN when closing
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        sock.connect(SERVER_ADDRESS)
        print(f"[Client {client_id}] Connected. Now forcing RST...")
        sock.close()
        print(f"[Client {client_id}] Finished Connection Reset.")
    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")
        
import struct

if __name__ == "__main__":
    print("--- Starting Event Loop Simulations ---")
    
    # 1. Normal Request
    simulate_normal_request(1)
    time.sleep(1)
    print("-" * 40)
    
    # 2. Slow Client (To show the server doesn't block)
    # We start the slow client in a thread, and immediately fire off a normal request
    # to show the normal request is handled WHILE the slow client is sleeping
    t_slow = threading.Thread(target=simulate_slow_client, args=(2,))
    t_slow.start()
    
    time.sleep(0.5) # Let the slow client connect and sleep
    
    print("--- Firing off a normal request WHILE the slow client is sleeping ---")
    simulate_normal_request(3) # This should succeed instantly
    
    t_slow.join() # Wait for slow client to finish
    print("-" * 40)
    
    # 3. Abrupt Disconnect
    simulate_abrupt_disconnect(4)
    time.sleep(1)
    print("-" * 40)
    
    # 4. Connection Reset
    simulate_connection_reset(5)
    time.sleep(1)
    print("--- Simulations Complete ---")
