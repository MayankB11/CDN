from _thread import *
import socket
import sys  
import time
import sched
from threading import Timer, Thread
import selectors
sys.path.insert(0, "../")
from messages.edge_heartbeat_message import *


def send_heartbeat():
	#print("Send hearbeat")
	try:
		sock = socket.socket()
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print('Socket successfully created')
	except socket.error as err:
		print('Socket creation failed with error %s', err)
		return
	
	
	host = socket.gethostname() # LB Primary
	port = EDGE_HEARTBEAT_LISTENER_PORT

	# To handle: what happens when LB Primary fails
	while True:
		
		try:
			sock.connect((host, port))
			print("Connected to LB Primary")
		except:
			try:
				# Should connect to secondary
				print("Connected to LB Secondary")
				break
				pass
			except:
				print("Connection to LB failed")
				break
	
		while(True):
			print("Try to send heartbeat")
			msg = EdgeHeartbeatMessage()
			try:
				msg.send(sock)
			except:
				print("Connection to load balancer primary failed")
				break
			time.sleep(EDGE_HEARTBEAT_TIME)
	sock.close()
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# def accept_client(conn):
# 	c,addr = conn.accept()
# 	print("Accepted connection from",addr)
# 	c.setblocking(False)
# 	sel.register(conn, selectors.EVENT_READ, serve_client)

# def serve_client(conn):
# 	conn.close()
# 	pass

# def main():
# #	check_timer()
# # 	TO DO
# #	1. Start new thread for heartbeat mechanism

# #	2. Use select to listen to/serve clients, similar to DNS
	
# 	sel = selectors.DefaultSelector()
	
# 	try: 
# 		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
# 		print("Socket successfully created")
# 	except socket.error as err: 
# 		print ("socket creation failed with error %s" %(err)) 

# 	port = 20020

# 	s.bind(('', port))         
# 	print ("socket binded to %s" %(port)) 	
	
# 	s.listen()

# 	s.setblocking(False)

# 	sel.register(s, selectors.EVENT_READ, data=None)
	
# 	while True:
# 		events = sel.select(timeout=None)
# 		for key, mask in events:
# 			if key.data is None:
# 				accept_client(key.fileobj)
# 			else:
# 				serve_client(key, mask)
# 		break

# 	s.close()
def main():
	pass


if __name__ == '__main__':
	Threads = []
	t1 = Thread(target = send_heartbeat)
	t1.start()
	t2 = Thread(target = main)
	t2.start()
	Threads.append(t1)
	Threads.append(t2)
	for t in Threads:
		t.join()	
	# main()

