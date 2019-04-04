import sys
# need to make it relative
sys.path.insert(0, "/home/animesh/Documents/Dev/DS/CDN/src/")

from messages.dns_request_message import *
from messages.dns_response_message import *
from config import *

import selectors
import socket

'''
Code for dummy DNS. It provides two services:
1) add_entry(hostname, ip, host)
2) get_ip(hostname)

services can be accessed using messages having the folowing structure (256 bytes):
 ------------------------------------------------------------------------------
| SERVICE_ID (1 byte) | Hostname (249 bytes) | IPv4 (4 bytes) | Port (2 bytes) |
 ------------------------------------------------------------------------------

SERVICE_ID : 0 - add_entry
			 1 - get_ip

Reply for get_ip is of the form (12 bytes):
 -----------------------
| IP block1 | IP block2 |
 -----------------------

IP block (6 bytes):
 ---------------------------------
| IPv4 (4 bytes) | Port (2 bytes) |
 ---------------------------------

'''


sel = selectors.DefaultSelector()

hostname_ip_map = {}

def accept(sock, mask):
	conn, addr = sock.accept()  # Should be ready
	print('Accepted', conn, 'from', addr)
	conn.setblocking(False)
	sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
	msg = DNSRequestMessage(0, "")
	msg.receive(conn)
	if msg.received:
		if msg.service_id == 0:
			# add_entry
			if msg.hostname in hostname_ip_map:
				hostname_ip_map[msg.hostname].append((msg.ip, msg.port))
			else:
				hostname_ip_map[msg.hostname] = [(msg.ip, msg.port)]
		else:
			# get_ip
			if msg.hostname not in hostname_ip_map:
				ipblocks = []
			else:
				ipblocks = hostname_ip_map[msg.hostname][0:2]

			while len(ipblocks) < 2:
				ipblocks.append(('0.0.0.0', 0))

			response_msg = DNSResponseMessage(ipblocks)
			response_msg.send(conn)
	else:
		print('closing', conn)
		sel.unregister(conn)
		conn.close()

sock = socket.socket()
host = DNS_IP
port = DNS_PORT
sock.bind((host, port))
sock.listen(DNS_MAX_LISTEN)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
	events = sel.select()
	for key, mask in events:
		callback = key.data
		callback(key.fileobj, mask)