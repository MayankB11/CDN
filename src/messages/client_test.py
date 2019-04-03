from dns_request_message import *

import socket               # Import socket module

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.

s.connect((host, port))

msg = DNSRequestMessage(0, "www.google.com", "172.16.2.30", 12312)
msg.send(s)