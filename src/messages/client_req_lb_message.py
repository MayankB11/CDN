import sys
from struct import *

sys.path.insert(0,"../")

from .message import *
from config import *


class ClientReqLBMessage(Message):

	signature = "HH"
	size = calcsize(signature)

	def __init__(self,content_id = None,loc_id = None):
		self.loc_id = loc_id
		self.content_id = content_id

	def send(self,soc):
		loc_id = self.loc_id
		content_id = self.content_id
		soc.send(pack(ClientReqLBMessage.signature,loc_id,content_id))

	def receive(self,soc):
		arr = soc.recv(ClientReqLBMessage.size)
		if len(arr) < ClientReqLBMessage.size:
			self.received = False
		else:
			self.received = True
			loc_id, content_id = unpack(ClientReqLBMessage.signature,arr)
			self.loc_id = loc_id
			self.content_id = content_id