# receives request from the clients and forwards it to appropriate edgeServer/originServer

import sys
import socket
from threading import Timer, Thread, Lock
import time

sys.path.insert(0, "../")

from config import *
from messages.lb_heartbeat_message import *
from messages.edge_heartbeat_message import *

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
		host = socket.gethostname()
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
	host = socket.gethostname()
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
	return (loc_id1[0]-loc_id2[0])**2 + (loc_id1[1]-loc_id2[1])**2

def serve_client(conn, addr):
	global edge_servers_available, edge_servers_availableL
	msg = ClientReqLBMessage()
	msg.receive(conn)
	if msg.received:
		loc_id = msg.loc_id
		# look in edge_servers_available after acquiring lock
		edge_servers_availableL.acquire()
		min_dist = dist(edge_servers_available[0][0], loc_id)
		best_server_index = 0
		for e,server in enumerate(edge_servers_available):
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

	# Serve clients
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	host = socket.gethostname()
	port = CLIENT_REQUEST_PORT
	sock.bind((host,port))
	sock.listen(MAX_CLIENT_REQUESTS)

	while(True):
		c, addr = sock.accept()
		t = Thread(target = serve_client,args = (c,addr))
		t.start()
	
	# Wait for other threads
	t_secondary_hb.join()
	t_edge_server_hb.join()