import socket
import select

# Create a TCP server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow port reuse so we don't get "Address already in use" errors during dev
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to an IP address and a specific port
server_socket.bind(('127.0.0.1', 8000))

# Start listening for incoming connections
server_socket.listen()

# **CRITICAL**: Make the server socket non-blocking. 
# It will return immediately rather than waiting (blocking) if there's nothing to do.
server_socket.setblocking(False)

# Store connections in a list. The event loop will ask the OS to monitor these.
sockets = [server_socket]

print("Server running on http://127.0.0.1:8000")

# The Infinite Event Loop
while True:
    # Ask the Operating System: "Which of these sockets are ready for me to read?"
    # select.select() blocks the loop here until at least ONE socket is ready.
    readable, writable, exceptional = select.select(sockets, [], [])

    # Process every socket that the OS says is ready
    for sock in readable:
        
        # Case 1: The ready socket is our main server. This means a NEW CLIENT is knocking.
        if sock == server_socket:
            # Accept the new connection
            client_socket, client_address = server_socket.accept()
            
            # Make the new client socket non-blocking too
            client_socket.setblocking(False)
            
            # Add the new client to our list so the loop monitors it next time
            sockets.append(client_socket)
            print(f"Accepted connection from {client_address}")
            
        # Case 2: The ready socket is a client. This means they sent HTTP data.
        else:
            try:
                # Read up to 1024 bytes of data from the client
                request_data = sock.recv(1024)
                
                if request_data:
                    # We received a request! Let's send a basic HTTP response back.
                    http_response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                        "Hello from the event loop!"
                    )
                    sock.sendall(http_response.encode('utf-8'))
                    
                    # Since we are done responding, remove the socket and close it
                    sockets.remove(sock)
                    sock.close()
                    print("Handled request and disconnected client.")
                    
                else:
                    # recv() returned empty bytes. The client gracefully disconnected.
                    print("Client disconnected automatically.")
                    sockets.remove(sock)
                    sock.close()
            
            except ConnectionResetError:
                # The client forcefully aborted the connection
                print("Client abruptly dropped the connection.")
                sockets.remove(sock)
                sock.close()
