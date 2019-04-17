
import socket
import sys  
import time
import sched
import selectors
import hashlib
import os

sys.path.insert(0, "../")

from _thread import *
from threading import Timer, Thread, Lock
from config import *
from messages.edge_heartbeat_message import *
from messages.content_related_messages import *

EDGE_SERVER_STORAGE_CAPACITY = 700000
current_free_space = EDGE_SERVER_STORAGE_CAPACITY

"""
n_clients is the variable containing number of clients this edge server is serving
n_clients_l is the lock of n_clients
"""
n_clients = 0
n_clients_l = Lock()

# Dictionary of files present at the edge server
# format : content_id: filename
content_dict = {}
# format : content_id : (time.time(), file_size)
lru_dict = {}

def md5(fname):
 	
 	hash_md5 = hashlib.md5()
 	with open(fname, "rb") as f:
  		for chunk in iter(lambda: f.read(4096), b""):
   			hash_md5.update(chunk)
 	return hash_md5.digest()

def send_heartbeat_primary():
	
	global n_clients,n_clients_l
	
	host = LOAD_BALANCER_PRIMARY_IP # LB Primary
	port = LB1_HEARTBEAT_LISTENER_PORT
	
	while True:
		try:
			try:
				sock = socket.socket()
				sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				print('Socket successfully created')
			
			except socket.error as err:
				print('Socket creation failed with error %s', err)
				return
			
			sock.connect((host, port))
			print("Connected to LB Primary")
		
		except Exception as e:
			print('Load balancer primary seems to be down. Trying to reconnect in a second.', e)
			time.sleep(1)
			continue
			
		while(True):
			print("Try to send heartbeat")
			
			n_clients_l.acquire()
			load = n_clients
			n_clients_l.release()
			
			msg = EdgeHeartbeatMessage(1,load)
			
			try:
				msg.send(sock)
			except Exception as e:
				print("Connection to load balancer primary failed",e)
				break
			
			time.sleep(EDGE_HEARTBEAT_TIME)
	sock.close()



def send_heartbeat_secondary():
	global n_clients,n_clients_l
	
	host = LOAD_BALANCER_SECONDARY_IP # LB Primary
	port = LB2_HEARTBEAT_LISTENER_PORT

	while True:		
		try:
			try:
				sock = socket.socket()
				sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				print('Socket successfully created')
			
			except socket.error as err:
				print('Socket creation failed with error %s', err)
				return
			
			sock.connect((host, port))
			print("Connected to LB Secondary")
		
		except Exception as e:
			print('Load balancer secondary seems to be down. Trying to reconnect in a second.',e)
			time.sleep(1)
			continue
	
		while(True):
			print("Try to send heartbeat")
		
			n_clients_l.acquire()
			load = n_clients
			n_clients_l.release()
		
			msg = EdgeHeartbeatMessage(1,load)
			
			try:
				msg.send(sock)
			except Exception as e:
				print("Connection to load balancer secondary failed",e)
				break
			
			time.sleep(EDGE_HEARTBEAT_TIME)
	sock.close()

def connectOrigin(ipblocks):

	"""
	Method to connect to LBs
	IP blocks contains the DNS response
	"""

	err_count = 0

	for host, port in ipblocks:
		s = socket.socket()
		try:
			print("Connecting ",host,":",port)
			s.connect((host, port))
			print("Connected ",host,":",port)
			break
		except socket.error:
			err_count += 1
			print("Connection failed ",host,":",port)
			continue

	if err_count == 2:
		print("Origin server could not be reached!")
		return s,0
	else:
		print("Connection established to the origin server")
		return s,1

def fetch_and_send(conn,addr,content_id,last_received_seq_no):
	
	global EDGE_SERVER_STORAGE_CAPACITY, current_free_space

	ipblocks = [(ORIGIN_SERVER_IP_1,ORIGIN_SERVER_PORT_1),(ORIGIN_SERVER_IP_2,ORIGIN_SERVER_PORT_2)]
	flag = 0 # 0 is default, 1 is finished, -1 is not finished

	while True:

		s,err = connectOrigin(ipblocks)
		if err == 0:
			raise Exception("Load Balancer could not be reached!")

		message = ContentRequestMessage(content_id, 0)
		message.send(s)
		
		file_des = FileDescriptionMessage(0, 0, '', bytearray())
		file_des.receive(s)
		
		print("File fetching: ",file_des.file_name)
		# now check if this file can be brought in or not:
		if file_des.file_size >= EDGE_SERVER_STORAGE_CAPACITY:
			# rather than storing this file, just send this file to the edge server
			print("File too big!")
			pass
		
		else:
			# this following can be used
			# first check if the total free space currently available is less or not
			while current_free_space < file_des.file_size:
				# remove least recently used file
				content_id_to_delete = min(lru_dict, key=lru_dict.get)
				current_free_space += lru_dict[content_id_to_delete][1]
				
				del lru_dict[content_id_to_delete]
				os.remove('data/'+content_dict[content_id_to_delete])
				del content_dict[content_id_to_delete]
				print("File Deleted")
			
			content_dict[file_des.content_id] = file_des.file_name
			lru_dict[file_des.content_id] = (time.time(), file_des.file_size)
			
			if flag!=-1:
				file_des.send(conn)
			flag = 0		
			print('data/'+file_des.file_name+"...........")
			
			with open('data/'+file_des.file_name,'wb') as f:
				
				recv_size = 0 
				file_size = file_des.file_size
				req_seq = 0

				while True:
					mes = ContentMessage(0,0)
					print('receiving data...')
					
					try:
						mes.receive(s,file_size,recv_size)
					except:				
						if mes.received == False:
							print('Yo')
							flag = -1
							last_received_seq_no = req_seq
							break		

					print(mes.content_id)
					print(mes.seq_no)
					
					req_seq = mes.seq_no+1
					
					data = mes.data
					if not data:
						break

					f.write(data)
					recv_size+=len(data)
					current_free_space -= len(data)
					
					if last_received_seq_no>mes.seq_no:
						continue

					mes.send(conn)
			
				if flag == -1:
					continue
				flag = 1

				print("successfully received the file")

			if md5('data/'+file_des.file_name) == file_des.md5_val:
				print("MD5 Matched!")

			else:
				print("MD5 didn't match")
				os.remove('data/'+file_des.file_name)

			content_dict[content_id]=file_des.file_name
			# print("After updating the content_dict")
			# print(content_dict)
			# print("After writing Current free space = "+str(current_free_space))
		
		s.close()

		if flag == 1:
			break

def serve_client(conn,addr):
	
	global n_clients_l,n_clients,content_dict
	
	n_clients_l.acquire()
	n_clients = n_clients+1
	n_clients_l.release()
	
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
		
		lru_dict[message.content_id] = (time.time(), file_size)
		
		file_des = FileDescriptionMessage(message.content_id, file_size, filename, md5('data/'+filename))
		file_des.send(conn)
		
		f = open('data/'+filename, 'rb')
		f.seek(message.seq_no*1018)
		
		l = f.read(1018)
		i = message.seq_no
		
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
		fetch_and_send(conn,addr,message.content_id,message.seq_no)

	n_clients_l.acquire()
	n_clients = n_clients-1
	n_clients_l.release()
	
	conn.close()

def main():	
	global n_clients, n_clients_l

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

	threads = []
	while True:
		c, addr = s.accept()
		print("Accepted connection from", addr)
		
		t = Thread(target = serve_client, args = (c,addr))
		threads.append(t)
		t.start()
	
	for t in threads:
		t.join()
	
	s.close()



if __name__ == '__main__':
	Threads = []
	t1 = Thread(target = send_heartbeat_primary)
	t1.start()
	t2 = Thread(target = send_heartbeat_secondary)
	t2.start()
	main()
	t1.join()
	t2.join()
