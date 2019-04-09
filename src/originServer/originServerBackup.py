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

def backup_data():
	# Receive data from Primary and save it
	pass
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


state = State.SECONDARY

def main():
	global state
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