import sys
# need to make it relative
sys.path.insert(0, "/home/animesh/Documents/Dev/DS/CDN/src/")

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

err_count = 0

for host, port in ipblocks:
	s = socket.socket()
	try:
		s.connect((host, port))
		break
	except socket.error:
		err_count += 1
		continue

if err_count == 2:
	raise Exception("Load Balancer could not be reached!")




############# Request file from redirected IP of edge server


############# Verify file, close connections and show success


#############
