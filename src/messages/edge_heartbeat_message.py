import sys

sys.path.insert(0, "../")

from .message import *
from config import *
from struct import *

class EdgeHeartbeatMessage(Message):

	"""
	loc (integer)
	load (integer) number of requests
	"""

	signature = 'HQ'
	size = calcsize(signature)

	def __init__(self, loc = None, load = None):
		if loc is None:
			loc = 1
		self.loc = loc
		if load is None:
			load = 0
		self.load = load

	def send(self, soc):
		soc.send(pack(EdgeHeartbeatMessage.signature, self.loc, self.load))

	def receive(self, soc):
		soc.settimeout(MSG_DELAY+5*EDGE_HEARTBEAT_TIME)
		try:
			arr = soc.recv(EdgeHeartbeatMessage.size)
			if len(arr) < EdgeHeartbeatMessage.size:
				self.received = False
			else:
				self.received = True
				self.loc,self.load = unpack(EdgeHeartbeatMessage.signature, arr)
		except Exception as e:
			print(e)
			self.received = False
