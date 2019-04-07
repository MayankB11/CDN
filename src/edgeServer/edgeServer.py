from _thread import *
import socket
import sys  
import time
import sched
from threading import Timer

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
## To be done in a separate thread

def check_timer():
	while 1:
		t = Timer(5,send_heartbeat)
		t.start()
		t.join()
	pass

def send_heartbeat():
	print("Send hearbeat")

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def accept_client():
	pass
def serve_client(conn):
	conn.close()
	pass

def main():
#	check_timer()
# 	TO DO
#	1. Start new thread for heartbeat mechanism
#	2. Use select to listen to/serve clients, similar to DNS
	pass

if __name__ == '__main__':
	main()

