# receives request from the clients and forwards it to appropriate edgeServer/originServer

import sys
import socket
from threading import Timer, Thread, Lock
import time
from enum import Enum

sys.path.insert(0, "../")

from config import *
from messages.dns_request_message import *
from messages.lb_heartbeat_message import *
from messages.edge_heartbeat_message import *
from messages.client_req_lb_message import *
from messages.client_res_lb_message import *

edge_servers_available = [] # (loc_id, (ip,port)) entries
edge_servers_availableL = Lock()
	
class State(Enum):
	PRIMARY = 1
	SECONDARY = 2

def acceptClientReq(sock,mask):
	conn, addr = sock.accept()
	print("Accepted requested from client addr: ",addr)
	conn.setblocking(false)
	sel.register(conn, selectors.EVENT_READ, readClientReq)

def readClientReq(sock,mask):
	msg = ClientReqLBMessage()
	msg.recv(sock)
	# TO DO DECIDE THE EDGE SERVER BASED ON LOCATION ID

def clientReqListener():
	sock = socket.socket()
	host = socket.gethostname()  # do we need to transfer this to config.py??????????
	port = LB_CLIENT_LISTEN_PORT
	sock.bind((host, port))
	sock.listen(LB_CLIENT_MAX_LISTEN)
	sock.setblocking(False)
	sel.register(sock, selectors.EVENT_READ, acceptClientReq)

def balancer():
	global state
	while(True):
		if state == State.SECONDARY:
			break
		print("Now acting as primary")
		time.sleep(1)

def check_and_run_balancer():
	global state
	if state == State.SECONDARY:
		state = State.PRIMARY
		t = Thread(target=balancer)
		t.start()


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
	host = '127.0.0.1'
	port = LB2_HEARTBEAT_LISTENER_PORT
	sock.bind((host,port))
	sock.listen(MAX_EDGE_SERVERS)
	
	threads = []
	while True:
		c, addr = sock.accept()
		t = Thread(target = receive_heartbeat,args = (c,addr))
		threads.append(t)
		t.start()
	
	sock.close()


if __name__ == "__main__":

	t_edge_server_hb = Thread(target = edge_heartbeat_handler)
	t_edge_server_hb.start()

	while(True):

		sock = socket.socket()
		host = '127.0.0.1'
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
