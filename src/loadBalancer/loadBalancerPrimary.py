# receives request from the clients and forwards it to appropriate edgeServer/originServer

import sys
import socket
from threading import Timer, Thread
import time

sys.path.insert(0, "../")

from config import *
from messages.lb_heartbeat_message import *

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

def heartBeat():
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
		msg.send(conn)
		time.sleep(LB_HEARTBEAT_TIME)

if __name__ == "__main__":
	t = Thread(target=heartBeat)
	t.start()
	t.join()
