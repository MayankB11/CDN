import sys

sys.path.insert(0, "../")

from .message import *
from config import *
from struct import *

class OriginHeartbeatMessage(Message):

	size = 1

	def __init__(self):
		pass

	def send(self, soc):
		soc.send(pack('B', 1))

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
