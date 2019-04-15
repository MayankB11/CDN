# Components
# Get heartbeat
# Serve as primary when needed - functionalities - 
	# 1. Change state
	# 2. Serve edge servers
	# 3. Serve content providers
# Back up data received from primary

import sys
import socket
from threading import Timer, Thread
import time
from enum import Enum

sys.path.insert(0, "../")

from config import *
from messages.origin_heartbeat_message import *



class State(Enum):
	PRIMARY = 1
	SECONDARY = 2

state = State.SECONDARY

def backup_data():
	# Receive data from Primary and save it
	global state
	while(True):
		if state == State.SECONDARY:
			# Define socket to receive data
			# Accept connection
			# Receive data, store it
			# if socket disconnects, break out of loop, wait till we become primary
		else:
			time.sleep(1)
			#  Do nothing

def serve_edge_server():
	# Send data to Edge server
	pass
def serve_content_provider():
	# Receive data from content provider
	pass

def origin_primary():
	global state
	while(True):
		if state == State.SECONDARY:
			return
		print("Now acting as primary")
		time.sleep(1)

def check_and_run_origin():
	global state
	if state == State.SECONDARY:
		state = State.PRIMARY
		t = Thread(target=origin_primary)
		t.start()

def popluate_content_dict():
	global content_dict
	files_list = os.listdir('data/')
	i = 1
	for filename in files_list:
		print('Content id: ',i,'\tFilename: ',filename)
		content_dict[i] = filename
		i=i+1

def main():
	global state
	popluate_content_dict()
	while(True):

		sock = socket.socket()
		host = socket.gethostname()
		port = ORIGIN_HEARTBEAT_PORT
		print("Trying to connect to primary")
		while(True):
			try:
				sock.connect((host, port))
				break
			except:
				check_and_run_origin()
				time.sleep(1)
				continue

		print('Connected to primary')
		state = State.SECONDARY
		sock.settimeout(2)

		msg = OriginHeartbeatMessage()
		msg.receive(sock)

		while msg.received:
			msg.receive(sock)

if __name__ == '__main__':
	main()