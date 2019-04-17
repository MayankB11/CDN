from _thread import *
import socket
import sys 
import os 
import time
import sched
from threading import Timer, Thread
import selectors
sys.path.insert(0, "../")
from config import *
from messages.content_related_messages import *
from edgeServer.edgeServer import md5
content_dict = {}

def main():
	global content_dict
	try:
		sock = socket.socket()
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print('Socket successfully created')
	except socket.error as err:
		print('Socket creation failed with error %s', err)
		return
	
	host = socket.gethostname() # LB Primary
	port = ORIGIN_CONTENT_PROVIDER_PORT_1

	try:
		sock.connect((host, port))
		print("Connected to origin Primary")
	except:
		try:
			# Should connect to secondary
			print("Connected to origin Secondary")
			return
			pass
		except:
			print("Connection to origin failed")
			return
	
	filename = sys.argv[1]
	content_id = int(sys.argv[2])
	file_size = int(os.stat(filename).st_size)
	file_des = FileDescriptionMessage(content_id,file_size,filename,md5(filename))
	file_des.send(sock)
	f = open(filename, 'rb')
	l = f.read(1018)
	i = 0
	while (l):
		# if message.seq_no <= i:
		msg = ContentMessage(content_id, i)
		msg.data = l
		msg.packet_size = len(l)
		msg.send(sock)
		i += 1
		l = f.read(1018)
	f.close()
	sock.close()
	
if __name__ == '__main__':
	main()