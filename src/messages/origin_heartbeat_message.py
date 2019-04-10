import sys

sys.path.insert(0, "../")

from .message import *
from config import *
from struct import *

class OriginHeartbeatMessage(Message):

	signature = 'B'
	size = calcsize(signature)

	def __init__(self):
		pass

	def send(self, soc):
		soc.send(pack(OriginHeartbeatMessage.signature, 1))

	def receive(self, soc):
		# soc.settimeout(MSG_DELAY+_HEARTBEAT_TIME)
		try:
			arr = soc.recv(OriginHeartbeatMessage.size)
			if len(arr) < OriginHeartbeatMessage.size:
				self.received = False
			else:
				self.received = True
		except:
			self.received = False
