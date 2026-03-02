You can run the server in one terminal and the simulation script in another.

1. Run the Server
Open a terminal and run: python event_loop_server.py

2. Run the Simulation
Open a second terminal and run: python simulate_clients.py

🔬 The Scenarios We Are Simulating
Here is what the simulation script does and how the event loop handles it:

Scenario 1: The Normal Request
What happens: A client connects, sends a full HTTP request immediately, and waits for a response. How the server handles it:

select() wakes up because the server_socket is ready. We accept() the client.
In the next loop, select() wakes up because the client socket has data. We recv(), send the HTTP response, and close the socket.
Scenario 2: The Slowloris (Slow Client)
What happens: This is a classic Denial-of-Service attack technique. A client connects, sends half of a request (GET / HTTP/1.1\r\n), and then literally goes to sleep for 2 seconds before sending the rest. How the server handles it: If we wrote a normal synchronous server, the whole server would freeze for 2 seconds waiting for the rest of the data, blocking everyone else. But our event loop is non-blocking!

The client sends part 1. select() wakes up, we recv() the partial data.
The client goes to sleep.
Crucially, the server goes back to the select() loop. It does not wait.
While the slow client is sleeping, a completely different client (Client 3) connects, sends a normal request, gets a response, and disconnects instantly. The slow client never blocked the server!
Finally, the slow client wakes up, sends the rest of the data, and gets its response.
Scenario 3: The Abrupt Disconnect
What happens: A client connects, realizes they don't want anything, and immediately closes the connection before sending any data. How the server handles it:

The server accept()s the connection.
Next loop, select() says the client socket is ready to read.
We call recv(), but it returns b'' (empty bytes).
The server realizes empty bytes = graceful disconnect. It removes the socket from its internal list and closes it cleanly. No crash.
Scenario 4: The Connection Reset (TCP RST)
What happens: A client connects, and then forcefully pulls the plug (sends a TCP RST packet instead of a graceful FIN packet). This happens if a user's computer crashes or their internet drops abruptly. How the server handles it:

The server accept()s the connection.
Next loop, select() says the socket is ready.
The server calls recv(), but the OS throws a ConnectionResetError.
Our try...except ConnectionResetError: block catches it gracefully, prints a message, removes the dead socket from the list, and continues to the next loop. No crash.
