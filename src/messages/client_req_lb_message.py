import sys
from struct import *

sys.path.insert(0,"../")

from .message import *
from config import *


class ClientReqLBMessage(Message):

	"""
	content_id (integer)
	loc_id (interger)
	prev_edge_ip (string containing IP address)
	"""

	signature = "HH4c"
	size = calcsize(signature)

	def __init__(self,content_id = None,loc_id = None, prev_edge_ip='0.0.0.0'):
		self.loc_id = loc_id
		self.content_id = content_id
		self.prev_edge_ip = prev_edge_ip

	def send(self,soc):
		loc_id = self.loc_id
		content_id = self.content_id
		prev_edge_ip = self.prev_edge_ip
		ip = prev_edge_ip.split('.')
		ip = [int(i).to_bytes(1, 'big') for i in ip]
		soc.send(pack(ClientReqLBMessage.signature,content_id,loc_id,ip[0],ip[1],ip[2],ip[3]))

	def receive(self,soc):
		recv_size = 0
		arr = bytearray()
		while recv_size!=ClientReqLBMessage.size:
			temp = soc.recv(ClientReqLBMessage.size-recv_size)
			arr = arr+temp
			recv_size+=len(temp)
			
			if len(arr)<ClientReqLBMessage.size:
				self.received = False
			else:
				self.received = True
				content_id, loc_id, ip0, ip1, ip2, ip3 = unpack(ClientReqLBMessage.signature,arr)
				self.content_id = content_id
				self.loc_id	= loc_id
				self.prev_edge_ip = str(int.from_bytes(ip0, 'big')) + "." + str(int.from_bytes(ip1, 'big')) + "." + str(int.from_bytes(ip2, 'big')) + "." + str(int.from_bytes(ip3, 'big'))