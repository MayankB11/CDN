import sys

sys.path.insert(0, "../")

from .message import *
from config import *
from struct import *

class EdgeHeartbeatMessage(Message):

	signature = 'B'
	size = calcsize(signature)

	def __init__(self):
		pass

	def send(self, soc):
		soc.send(pack(EdgeHeartbeatMessage.signature, 1))

	def receive(self, soc):
		soc.settimeout(MSG_DELAY+EDGE_HEARTBEAT_TIME)
		try:
			arr = soc.recv(EdgeHeartbeatMessage.size)
			if len(arr) < EdgeHeartbeatMessage.size:
				self.received = False
			else:
				self.received = True
		except:
			self.received = False
