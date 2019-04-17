# receives request from the clients and forwards it to appropriate edgeServer/originServer

import sys
import socket
from threading import Timer, Thread, Lock
import time

sys.path.insert(0, "../")

from enum import Enum
from config import *
from messages.dns_request_message import *
from messages.lb_heartbeat_message import *
from messages.edge_heartbeat_message import *
from messages.client_req_lb_message import *
from messages.client_res_lb_message import *

edge_servers_available = [] # (loc_id, (ip,port)) entries
edge_servers_availableL = Lock()
edge_server_load = {}
edge_server_load_l = Lock()

def dist(loc_id1, loc_id2):
	global LOCATION
	print(LOCATION[loc_id1])
	return (LOCATION[loc_id1][0]-LOCATION[loc_id2][0])**2 + (LOCATION[loc_id1][1]-LOCATION[loc_id2][1])**2

class State(Enum):
	PRIMARY = 1
	SECONDARY = 2

# def acceptClientReq(sock,mask):
# 	conn, addr = sock.accept()
# 	print("Accepted requested from client addr: ",addr)
# 	conn.setblocking(false)
# 	sel.register(conn, selectors.EVENT_READ, serve_client)

# def readClientReq(sock,mask):
# 	msg = ClientReqLBMessage()
# 	msg.recv(sock)
	# TO DO DECIDE THE EDGE SERVER BASED ON LOCATION ID

def clientReqListener():
	global state
	sock = socket.socket()
	host = LOAD_BALANCER_SECONDARY_IP  # do we need to transfer this to config.py??????????
	port = LB_CLIENT_LISTEN_PORT_BACKUP
	sock.bind((host, port))
	sock.listen(MAX_CLIENT_REQUESTS)
	print('Secondary binded to 10010')
	# sock.setblocking(False)
	while(True):
		if state == State.SECONDARY:
			break
		c, addr = sock.accept()
		t = Thread(target = serve_client,args = (c,addr))
		t.start()

def balancer():
	global state
	while(True):
		if state == State.SECONDARY:
			break
		print("Now acting as primary")
		clientReqListener()
		time.sleep(1)

def check_and_run_balancer():
	global state
	if state == State.SECONDARY:
		state = State.PRIMARY
		t = Thread(target=balancer)
		t.start()

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
		best_server_index = -1
		
		for e,server in enumerate(edge_servers_available):
			
			if server[1]==msg.prev_edge_ip:
				continue
			
			cur_dist = dist(server[0], loc_id)
			edge_server_load_l.acquire()
			
			if WEIGHT_DISTANCE*min_dist+WEIGHT_LOAD*cur_load > WEIGHT_DISTANCE*cur_dist+WEIGHT_LOAD*edge_server_load[edge_servers_available[best_server_index][1]]:
				min_dist = cur_dist
				best_server_index = e
			
			edge_server_load_l.release()
		
		msg = ClientResLBMessage(*edge_servers_available[best_server_index][1])
		edge_servers_availableL.release()
		
		msg.send(conn)
	
	conn.close()

state = State.SECONDARY

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
	
	host = LOAD_BALANCER_SECONDARY_IP
	port = LB2_HEARTBEAT_LISTENER_PORT
	
	sock.bind((host,port))
	
	sock.listen(MAX_EDGE_SERVERS)
	
	threads = []
	
	while True:
		c, addr = sock.accept()
		t = Thread(target = receive_heartbeat,args = (c,addr))
		threads.append(t)
		t.start()

	for t in threads():
		t.join()
	sock.close()


if __name__ == "__main__":

	t_edge_server_hb = Thread(target = edge_heartbeat_handler)
	t_edge_server_hb.start()

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
	host = DNS_IP
	port = DNS_PORT
	try:
		s.connect((host, port))
	except Exception as e:
		print(e)

	print("Adding IP to DNS")
	msg = DNSRequestMessage(0, "www.mycdn.com", LOAD_BALANCER_SECONDARY_IP, LB_CLIENT_LISTEN_PORT_BACKUP)
	try:
		msg.send(s)
	except Exception as e:
		print(e)

	s.close()

	while(True):

		sock = socket.socket()
		
		host = LOAD_BALANCER_PRIMARY_IP
		port = LB_HEARTBEAT_PORT
		
		print("Trying to connect to primary")
		
		while(True):
			try:
				sock.connect((host, port))
				break
			except:
				check_and_run_balancer()
				time.sleep(1)
				continue

		print('Connected to primary')
		state = State.SECONDARY
		sock.settimeout(2)

		msg = LBHeartbeatMessage()
		msg.receive(sock)

		while msg.received:
			msg.receive(sock)
	
	t_edge_server_hb.join()
