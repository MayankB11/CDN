import sys

sys.path.insert(0, "../")

from .message import *
from config import *
from struct import *

class LBHeartbeatMessage(Message):

	"""
	no input
	A single byte message
	"""

	signature = 'B'
	size = calcsize(signature)

	def __init__(self):
		pass

	def send(self, soc):
		soc.send(pack(LBHeartbeatMessage.signature, 1))

	def receive(self, soc):
		arr = soc.recv(LBHeartbeatMessage.size)
		if len(arr) < LBHeartbeatMessage.size:
			self.received = False
		else:
			self.received = True