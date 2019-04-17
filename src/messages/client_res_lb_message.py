import sys
from struct import *

sys.path.insert(0,"../")

from .message import *
from config import *


class ClientResLBMessage(Message):

	"""
	ip (ip address in the form of string)
	port (a integer number)
	"""

	signature = '4cH'
	size = calcsize(signature)

	def __init__(self, ip = None, port = None):
		self.ip = ip
		self.port = port

	def send(self,soc):
		ip = self.ip
		ip = ip.split('.')
		ip = [int(i).to_bytes(1, 'big') for i in ip]
		port = self.port
		soc.send(pack(ClientResLBMessage.signature,ip[0],ip[1],ip[2],ip[3],port))

	def receive(self,soc):
		arr = soc.recv(ClientResLBMessage.size)
		if len(arr) < ClientResLBMessage.size:
			self.received = False
		else:
			self.received = True
			ip0, ip1, ip2, ip3, port = unpack(ClientResLBMessage.signature,arr)
			self.ip = str(int.from_bytes(ip0, 'big')) + "." + str(int.from_bytes(ip1, 'big')) + "." + str(int.from_bytes(ip2, 'big')) + "." + str(int.from_bytes(ip3, 'big'))
			self.port = port
