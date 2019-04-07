# receives request from the clients and forwards it to appropriate edgeServer/originServer

import sys
import socket

sys.path.insert(0, "../")

from config import *

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

if __name__ == "__main__":
	pass
