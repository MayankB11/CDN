import sys

sys.path.insert(0, "../")

from .message import *
from config import *
from struct import *

class OriginHeartbeatMessage(Message):

	"""
	file_exists (single byte)
	"""

	signature = 'B'
	size = calcsize(signature)

	def __init__(self, file_exists):
		self.file_exists = file_exists

	def send(self, soc):
		soc.send(pack(OriginHeartbeatMessage.signature, self.file_exists))

	def receive(self, soc):
		# soc.settimeout(MSG_DELAY+_HEARTBEAT_TIME)
		try:
			arr = soc.recv(OriginHeartbeatMessage.size)
			if len(arr) < OriginHeartbeatMessage.size:
				self.received = False
			else:
				self.received = True
				self.file_exists = unpack(OriginHeartbeatMessage.signature, arr)[0]
		except:
			self.received = False
