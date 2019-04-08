from _thread import *
import socket
import sys  
import time
import sched
from threading import Timer
import selectors

	# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
## To be done in a separate thread

def check_timer():
	while 1:
		t = Timer(5,send_heartbeat)
		t.start()
		t.join()
	pass

def send_heartbeat():
	print("Send hearbeat")

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def accept_client(conn):
	c,addr = conn.accept()
	print("Accepted connection from",addr)
	c.setblocking(False)
	sel.register(conn, selectors.EVENT_READ, serve_client)
def serve_client(conn):
	conn.close()
	pass

def main():
#	check_timer()
# 	TO DO
#	1. Start new thread for heartbeat mechanism

#	2. Use select to listen to/serve clients, similar to DNS
	
	sel = selectors.DefaultSelector()
	
	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		print("Socket successfully created")
	except socket.error as err: 
		print ("socket creation failed with error %s" %(err)) 

	port = 20020

	s.bind(('', port))         
	print ("socket binded to %s" %(port)) 	
	
	s.listen()

	s.setblocking(False)

	sel.register(s, selectors.EVENT_READ, data=None)
	
	while True:
		events = sel.select(timeout=None)
		for key, mask in events:
			if key.data is None:
				accept_client(key.fileobj)
			else:
				serve_client(key, mask)
		break

	s.close()

if __name__ == '__main__':
	main()

