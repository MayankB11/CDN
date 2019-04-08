# receives request from the clients and forwards it to appropriate edgeServer/originServer

import sys
import socket
from threading import Timer, Thread
import time
from enum import Enum

sys.path.insert(0, "../")

from config import *
from messages.lb_heartbeat_message import *

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

if __name__ == "__main__":

	while(True):

		sock = socket.socket()
		host = socket.gethostname()
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
