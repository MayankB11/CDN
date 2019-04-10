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

edge_servers_available = []
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
	print("Connection Established with ", addr)
	while True:
		msg = EdgeHeartbeatMessage()
		msg.receive(conn)
		if msg.received == False:
			break
		print("Heartbeat received from", addr)
	##### TODO: Edge server failed, update table
	print("Edge server ", addr, " failed")
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
		##### TODO: Got new connection from edge server, update table
		t = Thread(target = receive_heartbeat,args = (c,addr))
		threads.append(t)
		t.start()
	
	sock.close()

def serve_client(conn, addr):
	msg = ClientReqLBMessage()
	msg.reeive(conn)


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