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
edge_server_load = {}
edge_server_load_l = Lock()
####################################

def heartBeat():
	while(True):
		sock = socket.socket()
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		host = LOAD_BALANCER_PRIMARY_IP
		port = LB_HEARTBEAT_PORT
		sock.bind((host, port))
		sock.listen(1)
		print("LB-LB Heartbeat socket binded")
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
	global edge_servers_available, edge_servers_availableL, edge_server_load, edge_server_load_l

	print("Connection Established with ", addr)
	# Edge server added
	msg = EdgeHeartbeatMessage()
	msg.receive(conn)
	prev_load = -1
	if msg.received:
		print("New edge server connected", addr)
		# prev_load = msg.load
		edge_server_load_l.acquire()
		edge_server_load[addr] = msg.load
		edge_server_load_l.release()
		prev_load = msg.load
		edge_servers_availableL.acquire()
		edge_servers_available.append((msg.loc, addr,msg.load))
		edge_servers_availableL.release()

	# Check for liveness
	while True:
		msg = EdgeHeartbeatMessage()
		msg.receive(conn)
		if msg.received == False:
			break
		if prev_load!=msg.load:
			edge_server_load_l.acquire()
			edge_server_load[addr] = msg.load
			edge_server_load_l.release()
			prev_load = msg.load
		print("Heartbeat received from", addr)

	print("Edge server ", addr, " failed")
	# Edge server removed
	for e,a in enumerate(edge_servers_available):
		if a[1] == addr:
			edge_servers_availableL.acquire()
			edge_servers_available.pop(e)
			edge_servers_availableL.release()
			edge_server_load_l.acquire()
			del edge_server_load[addr]
			edge_server_load_l.release()
			break
	conn.close()

def edge_heartbeat_handler():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	host = LOAD_BALANCER_PRIMARY_IP
	port = LB1_HEARTBEAT_LISTENER_PORT
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
	global edge_servers_available, edge_servers_availableL, edge_server_load, edge_server_load_l
	
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
		cur_load = sys.maxsize
		best_server_index = 0
		
		for e,server in enumerate(edge_servers_available):
			
			if server[1]==msg.prev_edge_ip:

				if e == 0:
					best_server_index = 1
				continue
			
			cur_dist = dist(server[0], loc_id)
			edge_server_load_l.acquire()
			
			if WEIGHT_DISTANCE*min_dist+WEIGHT_LOAD*cur_load > WEIGHT_DISTANCE*cur_dist+WEIGHT_LOAD*edge_server_load[edge_servers_available[e][1]]:
				min_dist = cur_dist
				cur_load = edge_server_load[edge_servers_available[e][1]]
				best_server_index = e
			
			edge_server_load_l.release()
		
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
	host = DNS_IP
	port = DNS_PORT
	s.connect((host, port))

	print("Adding IP to DNS")
	msg = DNSRequestMessage(0, "www.mycdn.com", LOAD_BALANCER_PRIMARY_IP, LB_CLIENT_LISTEN_PORT)
	msg.send(s)

	s.close()

	# Serve clients
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	host = LOAD_BALANCER_PRIMARY_IP
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