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
from enum import Enum
import pickle
from threading import Timer, Thread, Lock

sys.path.insert(0, "../../")

from messages.content_related_messages import *
from messages.origin_heartbeat_message import *
from config import *
from edgeServer.edgeServer import md5

class ContentStatus:
	INCOMPLETE = 0
	UNSYNCED = 1
	STORED = 2

class Content:
	def __init__(self, content_id, filename, status):
		self.content_id = content_id
		self.filename = filename
		self.status = status

####################################
# Global tables and lock variables #
####################################

content_dict = {}
content_dictL = Lock()

def dump():
	global content_dict
	f = open(ORIGIN_METADATA_FILENAME, 'wb')
	pickle.dump(content_dict, f)
	f.close()

def load():
	global content_dict
	f = open(ORIGIN_METADATA_FILENAME, 'rb')
	content_dict = pickle.load(f)
	f.close()

def print_dict():
	global content_dict
	for content in content_dict.values():
		print(content.content_id, content.filename, content.status)


####################################

def synchronizer():
	global content_dict, content_dictL

	while(True):
		sock = socket.socket()
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		host = ORIGIN_SERVER_IP_2
		port = ORIGIN_SYNCHRONIZER_PORT_2
		sock.bind((host, port))
		sock.listen(1)
		conn, addr = sock.accept()
		print('Accepted', conn, 'from', addr)
		print('Connected to other Origin Server')

		while(True):
			print("Looking for UNSYNCED files")
			try:
				for file in content_dict.values():
					if file.status == ContentStatus.UNSYNCED:
						# Sync this file
						print("Syncing file", file.filename, "with content id", file.content_id)
						file_size = int(os.stat('data/'+file.filename).st_size)
						file_des = FileDescriptionMessage(file.content_id,file_size,file.filename,md5('data/'+file.filename))
						print(file.content_id,file_size,file.filename,md5('data/'+file.filename))
						file_des.send(conn)

						# receive response from other server
						msg = OriginHeartbeatMessage(0)
						msg.receive(conn)
						if msg.file_exists:
							content_dictL.acquire()
							content_dict[file_des.content_id].status = ContentStatus.STORED
							dump()
							content_dictL.release()
							continue

						f = open('data/'+file.filename, 'rb')
						l = f.read(1018)
						i = 0
						while (l):
							# if message.seq_no <= i:
							msg = ContentMessage(file.content_id, i)
							msg.data = l
							msg.packet_size = len(l)
							msg.send(conn)
							i += 1
							l = f.read(1018)
						f.close()

						content_dictL.acquire()
						content_dict[file_des.content_id].status = ContentStatus.STORED
						dump()
						content_dictL.release()
				time.sleep(ORIGIN_HEARTBEAT_TIME)
			except Exception as e:
				print(e)
				break
		
def synchronize_receive():
	global content_dict, content_dictL


	host = ORIGIN_SERVER_IP_1
	port = ORIGIN_SYNCHRONIZER_PORT_1

	while(True):

		while(True):
			try:
				sock = socket.socket()
				sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				print('Socket successfully created')
				sock.connect((host, port))
				print("Connected to other server")
				break
			except:
				print("Cannot connect to other server")
				time.sleep(1)
				continue
		flag = 1
		while(True):
			try:
				file_des = FileDescriptionMessage(0, 0, '', '')
				file_des.receive(sock)
				if file_des.received:
					print("Receiving sync file details:")
					print(file_des.file_name)
					print(file_des.content_id)
					print(file_des.file_size)

					# check if file already exists and respond to the other server
					if file_des.content_id in content_dict:
						content = content_dict[file_des.content_id]
						if content.status == ContentStatus.STORED:
							file_exists = True
						elif content.status == ContentStatus.UNSYNCED:
							content_dictL.acquire()
							content_dict[file_des.content_id].status = ContentStatus.STORED
							dump()
							content_dictL.release()
							file_exists	= True
						else: # can check MD5 for incomplete files but unnecessary hassle :/
							file_exists = False
					else:
						file_exists = False

					msg = OriginHeartbeatMessage(file_exists)
					msg.send(sock)

					if file_exists:
						continue

					content_dictL.acquire()
					content_dict[file_des.content_id] = Content(file_des.content_id, file_des.file_name, ContentStatus.INCOMPLETE)
					dump()
					content_dictL.release()
					with open('data/' + file_des.file_name, 'wb') as f:
						print('file opened')
						print("Content ID: ",file_des.content_id)
						content_id = file_des.content_id
						file_size = file_des.file_size
						total_received=0
						seq_no=0
						while True:
							msg = ContentMessage(content_id, seq_no)

							try:
								msg.receive(sock,file_size,total_received)
							except Exception as e:
								print("Last Sequence Number received: ",last_seq_number_recv)
								print(e)
								flag = 0
								break
								# return last_seq_number_recv
							
							print("Sequence no: ",msg.seq_no)
							last_seq_number_recv = msg.seq_no
							data = msg.data
							total_received+=len(data)
							# print(len(data))
							if not data:
								break
							f.write(data)
					if flag == 0:
						break
					f.close()
					content_dictL.acquire()
					content_dict[file_des.content_id] = Content(file_des.content_id, file_des.file_name, ContentStatus.STORED)
					dump()
					content_dictL.release()
				else:
					print("Error receiving")
					break
			except Exception as e:
				print(e)


def serve_edge_server_helper(conn, addr):
	global content_dict
	message = ContentRequestMessage(0, 0)
	try:
		message.receive(conn)
		# Get filename from file
		if message.received == False:
			return
		
		# Check if file is present in edge server
		if message.content_id in content_dict:
			filename = content_dict[message.content_id].filename
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
	except Exception as e:
		print(e)

def serve_edge_server():
	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		print("Socket successfully created")
	except socket.error as err: 
		print ("socket creation failed with error %s" %(err)) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	port = ORIGIN_SERVER_PORT_2
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
	global content_dict, content_dictL
	file_des = FileDescriptionMessage(0, 0, '', '')
	file_des.receive(c)
	print(file_des.file_name)
	print(file_des.content_id)
	print(file_des.file_size)
	content_dictL.acquire()
	content_dict[file_des.content_id] = Content(file_des.content_id, file_des.file_name, ContentStatus.INCOMPLETE)
	dump()
	content_dictL.release()

	with open('data/'+file_des.file_name,'wb') as f:
		recv_size = 0 
		file_size = file_des.file_size
		while True:
			mes = ContentMessage(0,0)
			print('receiving data...')
			
			mes.receive(c,file_size,recv_size)
			print(mes.content_id) 
			print(mes.seq_no)
			
			data = mes.data
			if not data:
				break

			f.write(data)
			recv_size+=len(data)

	print("successfully received the file")

	if md5('data/'+file_des.file_name) == file_des.md5_val:
		print("MD5 Matched!")
	else:
		print("MD5 didn't match")
	content_dictL.acquire()
	content_dict[file_des.content_id].status = ContentStatus.UNSYNCED
	dump()
	content_dictL.release()
	print_dict()
	c.close()

def serve_content_provider():
	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		print("Socket successfully created")
	except socket.error as err: 
		print ("socket creation failed with error %s" %(err)) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	port = ORIGIN_CONTENT_PROVIDER_PORT_2
	s.bind(('', port))         
	print ("socket binded to %s" %(port)) 	
	
	s.listen(5)
	threads = []
	while True:
		c, addr = s.accept()
		print("Accepted connection from", addr)
		t = Thread(target = serve_content_provider_helper, args = (c,addr))
		threads.append(t)
		t.start()
	for t in threads:
		t.join()
	c.close()

def popluate_content_dict():
	global content_dict, content_dictL
	content_dictL.acquire()
	load()
	content_dictL.release()

def main():
	popluate_content_dict()
	threads = []
	t1 = Thread(target = synchronizer)
	threads.append(t1)
	t1.start()
	t2 = Thread(target = serve_edge_server)
	threads.append(t2)
	t2.start()
	t3 = Thread(target = serve_content_provider)
	threads.append(t3)
	t3.start()
	t4 = Thread(target = synchronize_receive)
	threads.append(t4)
	t4.start()
	for t in threads:
		t.join()
		
if __name__ == '__main__':
	main()
