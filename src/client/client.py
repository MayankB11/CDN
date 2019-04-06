import sys
# need to make it relative
sys.path.insert(0, "../")

from messages.dns_request_message import *
from messages.dns_response_message import *
from config import *

import selectors
import socket

############# Get IP of load balancer from DNS

s = socket.socket()         
host = DNS_IP
port = DNS_PORT            

s.connect((host, port))

print("Requesting IP from DNS")
msg = DNSRequestMessage(1, "www.google.com")
msg.send(s)

msg = DNSResponseMessage()
msg.receive(s)
ipblocks = msg.ipblocks

s.close()

############# Request file from load balancer


############# Request file from redirected IP of edge server


############# Verify file, close connections and show success


#############
