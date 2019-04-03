from dns_request_message import *

import socket               # Import socket module

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port

s.listen(5)                 # Now wait for client connection.

c, addr = s.accept()
msg = DNSRequestMessage(0, "")
msg.receive(c)

print(msg.ip)