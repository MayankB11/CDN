from _thread import *
import socket
import sys  
import time
import sched
from threading import Timer, Thread
import selectors
sys.path.insert(0, "../")
from messages.edge_heartbeat_message import *

#Define tables
#Edge_ID, Edge_addr, Predicted load, Loc

def receive_heartbeat(conn, addr):
	print("Connection Established with ", addr)
	while True:
		msg = EdgeHeartbeatMessage()
		msg.receive(conn)
		if msg.received == False:
			break
		print("Heartbeat received from", addr)
	print("Edge server ", addr, " failed")
	conn.close()

def edge_heartbeat_handler():
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	host = socket.gethostname()
	port = EDGE_HEARTBEAT_LISTENER_PORT
	sock.bind((host,port))
	sock.listen(5)
	
	threads = []
	while True:
		c, addr = sock.accept()
		t = Thread(target = receive_heartbeat,args = (c,addr))
		threads.append(t)
		t.start()
	
	for t in threads:
		t.join()
	
	sock.close()

def main():
	
	threads = []
	t = Thread(target = edge_heartbeat_handler)
	t.start()

	for t in threads:
		t.join()

if __name__ == '__main__':
	main()
	# t = Thread(target=receive_heartbeat)
	# t.start()
	# t.join()	