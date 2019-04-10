from _thread import *
import socket
import sys  
import time
import sched
from threading import Timer, Thread
import selectors
sys.path.insert(0, "../")
from messages.edge_heartbeat_message import *
from messages.content_related_messages import *
import hashlib
import os

EDGE_SERVER_PORT = 30001

def md5(fname):
 	hash_md5 = hashlib.md5()
 	with open(fname, "rb") as f:
  		for chunk in iter(lambda: f.read(4096), b""):
   			hash_md5.update(chunk)
 	return hash_md5.digest()

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


# def accept_client(conn):
# 	c,addr = conn.accept()
# 	print("Accepted connection from",addr)
# 	c.setblocking(False)
# 	sel.register(conn, selectors.EVENT_READ, serve_client)

# Dictionary of files present at the edge server
content_dict = {1: 'share.png'}
lru_dict = {1:None}

def serve_client(conn,addr):
	message = ContentRequestMessage(0, 0)
	message.receive(conn)
	# Get filename from file
	if message.received == False:
		return
	
	# Check if file is present in edge server
	if message.content_id in content_dict:
		filename = content_dict[message.content_id]
                # before sending the file, send its details plus a checksum
		file_size = int(os.stat(filename).st_size)
		file_des = FileDescriptionMessage(message.content_id, file_size, filename, md5(filename))
		file_des.send(conn)
		f = open(filename, 'rb')
		l = f.read(1018)
		i = 0
		while (l):
			if message.seq_no <= i:
				msg = ContentMessage(message.content_id, i)
				msg.data = l
				msg.packet_size = len(l)
				msg.send(conn)
				i += 1
			l = f.read(1018)
		f.close()
	else:
		# Get chunks of data from origin and send to client
		pass
	conn.close()

def main():	
	# sel = selectors.DefaultSelector()
	
	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		print("Socket successfully created")
	except socket.error as err: 
		print ("socket creation failed with error %s" %(err)) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	port = EDGE_SERVER_PORT
	s.bind(('', port))         
	print ("socket binded to %s" %(port)) 	
	
	s.listen(5)

	# s.setblocking(False)
	# sel.register(s, selectors.EVENT_READ, data=None)
	threads = []
	while True:
		c, addr = s.accept()
		print("Accepted connection from", addr)
		t = Thread(target = serve_client, args = (c,addr))
		threads.append(t)
		t.start()
		# events = sel.select(timeout=None)
		# for key, mask in events:
		# 	if key.data is None:
		# 		accept_client(key.fileobj)
		# 	else:
		# 		serve_client(key, mask)
		# break
	for t in threads:
		t.join()
	s.close()



if __name__ == '__main__':
	Threads = []
	t = Thread(target = send_heartbeat)
	t.start()
	main()
	t.join()

