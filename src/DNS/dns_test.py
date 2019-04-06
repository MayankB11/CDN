import sys

sys.path.insert(0, "../")

from messages.dns_request_message import *
from messages.dns_response_message import *
from config import *

import selectors
import socket

s = socket.socket()    
host = DNS_IP 
port = DNS_PORT                

s.connect((host, port))

print("Adding ip to DNS")
msg = DNSRequestMessage(0, "www.google.com", "172.16.2.30", 12312)
msg.send(s)

print("Requesting ip from DNS")
msg = DNSRequestMessage(1, "www.google.com")
msg.send(s)

print("Got response:")
msg = DNSResponseMessage()
msg.receive(s)
print(msg.ipblocks)

s.close()