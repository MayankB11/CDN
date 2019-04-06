import sys

sys.path.insert(0, "../")

from .message import *
from config import *
from struct import *

def stream_ip(ip):
	ip = ip.split('.')
	ip = [int(i).to_bytes(1, 'big') for i in ip]
	return ip

def unstream_ip(ip0, ip1, ip2, ip3):
	return str(int.from_bytes(ip0, 'big')) + "." + str(int.from_bytes(ip1, 'big')) + "." + str(int.from_bytes(ip2, 'big')) + "." + str(int.from_bytes(ip3, 'big'))

class DNSResponseMessage(Message):

	"""
	ipblocks - <ip,port> x 2

	"""

	size = 24

	def __init__(self, ipblocks = None):
		self.ipblocks = ipblocks

	def send(self, soc):
		ip0 = stream_ip(self.ipblocks[0][0])
		ip1 = stream_ip(self.ipblocks[1][0])
		soc.send(pack('4cH4cH', ip0[0], ip0[1], ip0[2], ip0[3], self.ipblocks[0][1], ip1[0], ip1[1], ip1[2], ip1[3], self.ipblocks[1][1]))

	def receive(self, soc):
		arr = soc.recv(DNSResponseMessage.size)
		ip00, ip01, ip02, ip03, port0, ip10, ip11, ip12, ip13, port1 = unpack('4cH4cH', arr)
		self.ipblocks = [(unstream_ip(ip00, ip01, ip02, ip03), port0), (unstream_ip(ip10, ip11, ip12, ip13), port1)]

