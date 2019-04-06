import sys
# need to make it relative
sys.path.insert(0, "../")

from .message import *
from config import *
from struct import *

class DNSRequestMessage(Message):

	"""
	service_id (integer) :	0 - add_entry
				 			1 - get_ip
	hostname (string)
	ip (string)
	port (integer)

	"""

	size = 256

	def __init__(self, service_id, hostname, ip = None, port = None):
		self.service_id = service_id
		if len(hostname) > HOSTNAME_MAX_LEN:
			raise Exception("Length of hostname must be less than 249 characters!")
		self.hostname = hostname
		if service_id == 0:
			self.ip = ip
			self.port = port
		else:
			self.ip = "0.0.0.0"
			self.port = 0

	def send(self, soc):
		ip = self.ip
		ip = ip.split('.')
		ip = [int(i).to_bytes(1, 'big') for i in ip]
		soc.send(pack('B'+str(HOSTNAME_MAX_LEN)+'s4cH', self.service_id, self.hostname.encode(), ip[0], ip[1], ip[2], ip[3], self.port))

	def receive(self, soc):
		arr = soc.recv(DNSRequestMessage.size)
		if len(arr) < DNSRequestMessage.size:
			self.received = False
		else:
			self.received = True
			service_id, hostname, ip0, ip1, ip2, ip3, port = unpack('B'+str(HOSTNAME_MAX_LEN)+'s4cH', arr)
			self.service_id = service_id
			self.hostname = hostname.decode().strip()
			self.ip = str(int.from_bytes(ip0, 'big')) + "." + str(int.from_bytes(ip1, 'big')) + "." + str(int.from_bytes(ip2, 'big')) + "." + str(int.from_bytes(ip3, 'big'))
			self.port = port

