import sys
import selectors
import socket

sys.path.insert(0, "../")

from messages.dns_request_message import *
from messages.dns_response_message import *
from messages.client_req_lb_message import *
from messages.client_res_lb_message import *
from messages.content_related_messages import *
from config import *

############# Get IP of load balancer from DNS

s = socket.socket()         
host = '127.0.0.1'  ## DNS_IP
port = DNS_PORT            

s.connect((host, port))

print("Requesting IP from DNS")
msg = DNSRequestMessage(1, "www.mycdn.com")
msg.send(s)

msg = DNSResponseMessage()
msg.receive(s)
ipblocks = msg.ipblocks
print(ipblocks)

s.close()

############# Request file from load balancer

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
	raise Exception("Load Balancer could not be reached!")
else:
	print("Connection established to the load balancer")

msg = ClientReqLBMessage(1,1)
msg.send(s)

msg = ClientResLBMessage()
msg.receive(s)

print(msg.ip, msg.port)

############# Request file from redirected IP of edge server

def requestFile(edgeIP,edgePort,content_id,seq_no=0):
	## Sequence number is zero for initial request
	## returns last sequence number it received 
	## -2 if complete file is received
	## -1 if nothing is received
	## else the sequence number
	soc = socket.socket()             # Create a socket object                   
	soc.settimeout(10)
	
	try:
		print("Connecting to edge server ip: ",edgeIP)
		sys.stdout.flush()
		soc.connect((edgeIP, edgePort))
	except Exception as e:
		print("Unable to connect to edge server ip: ",edgeIP)
		return -1
	
	last_seq_number_recv = -1
	message = ContentRequestMessage(1, 0)
	message.send(soc)

	file_des = FileDescriptionMessage(0, 0, '', 0)
	
	try:
		file_des.receive(soc)
	except:
		print("Unable to get file details")
		print("Last Sequence Number received: ",last_seq_number_recv)
		return last_seq_number_recv
	
	print(file_des.file_name)
	print(file_des.content_id)
	print(file_des.file_size)
	with open('rec_' + file_des.file_name, 'wb') as f:
		print('file opened')
		print("Content ID: ",file_des.content_id)
		while True:
			msg = ContentMessage(1, 0)

			try:
				msg.receive(soc)
			except Exception as e:
				print("Last Sequence Number received: ",last_seq_number_recv)
				return last_seq_number_recv
			
			print("Sequence no: ",msg.seq_no)
			last_seq_number_recv = msg.seq_no
			data = msg.data
			# print(type(data))
			if not data:
				break
			f.write(data)
	f.close()
	return -2

print(requestFile(msg.ip, EDGE_SERVER_PORT ,1))
############# Verify file, close connections and show success


#############
