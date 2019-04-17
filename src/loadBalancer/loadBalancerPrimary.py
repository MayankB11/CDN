# receives request from the clients and forwards it to appropriate edgeServer/originServer

import sys
import socket
from threading import Timer, Thread, Lock
import time

sys.path.insert(0, "../")

from config import *
from messages.dns_request_message import *
from messages.lb_heartbeat_message import *
from messages.edge_heartbeat_message import *
from messages.client_req_lb_message import *
from messages.client_res_lb_message import *

####################################
# Global tables and lock variables #
####################################

edge_servers_available = [] # (loc_id, (ip,port)) entries
edge_servers_availableL = Lock()

####################################

def heartBeat():
	while(True):
		sock = socket.socket()
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		host = '127.0.0.1'
		port = LB_HEARTBEAT_PORT
		sock.bind((host, port))
		sock.listen(1)
		conn, addr = sock.accept()
		print('Accepted', conn, 'from', addr)
		print('Connected to backup load balancer')

		while(True):
			print("Sent HeartBeat")
			msg = LBHeartbeatMessage()
			try:
				msg.send(conn)
			except:
				print("Connection to backup failed")
				break
			time.sleep(LB_HEARTBEAT_TIME)

def receive_heartbeat(conn, addr):
	global edge_servers_available, edge_servers_availableL

	print("Connection Established with ", addr)
	# Edge server added
	msg = EdgeHeartbeatMessage()
	msg.receive(conn)
	if msg.received:
		print("New edge server connected", addr)
		edge_servers_availableL.acquire()
		edge_servers_available.append((msg.loc, addr))
		edge_servers_availableL.release()

	# Check for liveness
	while True:
		msg = EdgeHeartbeatMessage()
		msg.receive(conn)
		if msg.received == False:
			break
		print("Heartbeat received from", addr)

	print("Edge server ", addr, " failed")
	# Edge server removed
	for e,a in enumerate(edge_servers_available):
		if a[1] == addr:
			edge_servers_availableL.acquire()
			edge_servers_available.pop(e)
			edge_servers_availableL.release()
			break
	conn.close()

def edge_heartbeat_handler():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	host = '127.0.0.1'
	port = EDGE_HEARTBEAT_LISTENER_PORT
	sock.bind((host,port))
	sock.listen(MAX_EDGE_SERVERS)
	
	threads = []
	while True:
		c, addr = sock.accept()
		t = Thread(target = receive_heartbeat,args = (c,addr))
		threads.append(t)
		t.start()
	
	sock.close()

def dist(loc_id1, loc_id2):
	global LOCATION
	print(LOCATION[loc_id1])
	return (LOCATION[loc_id1][0]-LOCATION[loc_id2][0])**2 + (LOCATION[loc_id1][1]-LOCATION[loc_id2][1])**2

def serve_client(conn, addr):
	global edge_servers_available, edge_servers_availableL
	msg = ClientReqLBMessage()
	msg.receive(conn)
	if msg.received:
		print("Received request: loc id ", msg.loc_id, " from ", addr)
		loc_id = msg.loc_id
		# look in edge_servers_available after acquiring lock
		edge_servers_availableL.acquire()
		# At least one edge server would be available
		if(len(edge_servers_available)==1):
			msg = ClientResLBMessage(*edge_servers_available[0][1])
			edge_servers_availableL.release()
			msg.send(conn)
			conn.close()
			return

		if(len(edge_servers_available)==0):
			msg = ClientResLBMessage('0.0.0.0',EDGE_SERVER_PORT)
			edge_servers_availableL.release()
			msg.send(conn)
			conn.close()
			return

		min_dist = sys.maxsize
		best_server_index = -1
		for e,server in enumerate(edge_servers_available):
			print(type(server[1]))
			if server[1]==msg.prev_edge_ip:
				continue
			cur_dist = dist(server[0], loc_id)
			if min_dist > cur_dist:
				min_dist = cur_dist
				best_server_index = e
		msg = ClientResLBMessage(*edge_servers_available[best_server_index][1])
		edge_servers_availableL.release()
		msg.send(conn)
	conn.close()

if __name__ == "__main__":

	# Secondary Heartbeat thread
	t_secondary_hb = Thread(target=heartBeat)
	t_secondary_hb.start()
	
	# Edge server handler thread
	t_edge_server_hb = Thread(target = edge_heartbeat_handler)
	t_edge_server_hb.start()

	# Register itself to DNS
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
	host = '127.0.0.1'
	port = DNS_PORT
	s.connect((host, port))

	print("Adding IP to DNS")
	msg = DNSRequestMessage(0, "www.mycdn.com", LOAD_BALANCER_PRIMARY_IP, LB_CLIENT_LISTEN_PORT)
	msg.send(s)

	s.close()

	# Serve clients
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	host = '127.0.0.1'
	port = LB_CLIENT_LISTEN_PORT
	sock.bind((host,port))
	sock.listen(MAX_CLIENT_REQUESTS)

	while(True):
		c, addr = sock.accept()
		t = Thread(target = serve_client,args = (c,addr))
		t.start()
	
	# Wait for other threads
	t_secondary_hb.join()
	t_edge_server_hb.join()