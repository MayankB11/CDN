from _thread import *
import socket
import sys  
import time
import sched
from threading import Timer, Thread
import selectors
sys.path.insert(0, "../")
from config import *
from messages.content_related_messages import *

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
	port = ORIGIN_CONTENT_PROVIDER_PORT

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
	content_id = sys.argv[2]
	f = open(filename, 'rb')
	l = f.read(1020)
	i = 0
	while (l):
		# if message.seq_no <= i:
		msg = ContentMessage(int(content_id), i)
		msg.data = l
		msg.send(sock)
		i += 1
		l = f.read(1020)
	f.close()
	sock.close()
if __name__ == '__main__':
	main()