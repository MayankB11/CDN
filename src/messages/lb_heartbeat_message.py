import sys

sys.path.insert(0, "../")

from .message import *
from config import *
from struct import *

class LBHeartbeatMessage(Message):

	size = 1

	def __init__(self):
		pass

	def send(self, soc):
		soc.send(pack('B', 1))

	def receive(self, soc):
		arr = soc.recv(LBHeartbeatMessage.size)
		if len(arr) < LBHeartbeatMessage.size:
			self.received = False
		else:
			self.received = True