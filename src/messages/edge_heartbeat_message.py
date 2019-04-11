import sys

sys.path.insert(0, "../")

from .message import *
from config import *
from struct import *

class EdgeHeartbeatMessage(Message):

	signature = 'H'
	size = calcsize(signature)

	def __init__(self, loc = None):
		if loc is None:
			loc = 1
		self.loc = loc

	def send(self, soc):
		soc.send(pack(EdgeHeartbeatMessage.signature, self.loc))

	def receive(self, soc):
		soc.settimeout(MSG_DELAY+EDGE_HEARTBEAT_TIME)
		try:
			arr = soc.recv(EdgeHeartbeatMessage.size)
			if len(arr) < EdgeHeartbeatMessage.size:
				self.received = False
			else:
				self.received = True
				self.loc = unpack(EdgeHeartbeatMessage.signature, arr)[0]
		except:
			self.received = False
