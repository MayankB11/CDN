# 4 main components
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
import os
sys.path.insert(0, "../")
from messages.content_related_messages import *
from messages.origin_heartbeat_message import *
from config import *
from edgeServer.edgeServer import md5

content_dict = {}

def send_heartbeat():
	while(True):
		sock = socket.socket()
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		host = socket.gethostname()
		port = ORIGIN_HEARTBEAT_PORT
		sock.bind((host, port))
		sock.listen(1)
		conn, addr = sock.accept()
		print('Accepted', conn, 'from', addr)
		print('Connected to backup Origin Server')

		while(True):
			print("Sent HeartBeat")
			msg = OriginHeartbeatMessage()
			try:
				msg.send(conn)
			except:
				print("Connection to backup failed")
				break
			time.sleep(ORIGIN_HEARTBEAT_TIME)
		

def serve_edge_server_helper(conn, addr):
	global content_id
	message = ContentRequestMessage(0, 0)
	message.receive(conn)
	# Get filename from file
	if message.received == False:
		return
	
	# Check if file is present in edge server
	if message.content_id in content_dict:
		filename = content_dict[message.content_id]
                # before sending the file, send its details plus a checksum
		file_size = int(os.stat('data/'+filename).st_size)
		print("filename: ",filename)
		file_des = FileDescriptionMessage(message.content_id, file_size, filename, md5('data/'+filename))
		file_des.send(conn)
		f = open('data/'+filename, 'rb')
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

def serve_edge_server():
	global content_dict
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

def serve_content_provider_helper(c,addr):
	global content_dict
	file_des = FileDescriptionMessage(0, 0, '', 0)
	file_des.receive(c)
	print(file_des.file_name)
	print(file_des.content_id)
	print(file_des.file_size)
	content_dict[file_des.content_id] = file_des.file_name
	with open('data/'+file_des.file_name,'wb') as f:
		while True:
			mes = ContentMessage(0,0)
			print('receiving data...')
			mes.receive(c)
			print(mes.content_id) 
			print(mes.seq_no)
			data = mes.data
			if not data:
				break
			f.write(data)
		print("successfully received the file")
	if md5('data/'+file_des.file_name) == file_des.md5_val:
		print("MD5 Matched!")
	else:
		print("MD5 didn't match")
	c.close()

def serve_content_provider():
	global content_dict
	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		print("Socket successfully created")
	except socket.error as err: 
		print ("socket creation failed with error %s" %(err)) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	port = ORIGIN_CONTENT_PROVIDER_PORT
	s.bind(('', port))         
	print ("socket binded to %s" %(port)) 	
	
	s.listen(5)
	threads = []
	while True:
		s, addr = s.accept()
		print("Accepted connection from", addr)
		t = Thread(target = serve_content_provider_helper, args = (s,addr))
		threads.append(t)
		t.start()
	for t in threads:
		t.join()
	s.close()

def popluate_content_dict():
	global content_dict
	files_list = os.listdir('data/')
	i = 1
	for filename in files_list:
		print('Content id: ',i,'\tFilename: ',filename)
		content_dict[i] = filename
		i=i+1

def main():
	popluate_content_dict()
	threads = []
	t1 = Thread(target = send_heartbeat)
	threads.append(t1)
	t1.start()
	t2 = Thread(target = serve_edge_server);
	threads.append(t2)
	t2.start()
	t3 = Thread(target = serve_content_provider)
	threads.append(t3)
	t3.start()
	for t in threads:
		t.join()
if __name__ == '__main__':
	main()