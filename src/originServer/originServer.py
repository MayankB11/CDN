# 3 main components
# Serve edge servers
# Send heartbeat to backup
# Receive data from Content providers
# Replicate data to backup

from _thread import *
import socket
import sys  
import time
import sched
from threading import Timer, Thread
import selectors
sys.path.insert(0, "../")
from messages.content_related_messages import *
from messages.origin_heartbeat_message import *

content_dict = {}
def send_heartbeat():
	pass
def serve_edge_server_helper(conn, addr):
	conn.close()
def serve_edge_server():
	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		print("Socket successfully created")
	except socket.error as err: 
		print ("socket creation failed with error %s" %(err)) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	port = ORIGIN_SERVER_PORT
	s.bind(('', port))         
	print ("socket binded to %s" %(port)) 	
	
	s.listen(5)


	threads = []
	while True:
		c, addr = s.accept()
		print("Accepted connection from", addr)
		t = Thread(target = serve_edge_server_helper, args = (c,addr))
		threads.append(t)
		t.start()
	for t in threads:
		t.join()
	s.close()		
def serve_content_provider():
	pass
def main():
	threads = []
	t = Thread(target = serve_edge_server);
	threads.append(t)
	t.start()
	for t in threads:
		t.join()
if __name__ == '__main__':
	main()