import sys

from struct import *

from .message import *
from config import *

FILENAME_MAX_LEN = 252
MAX_DATA_PACKET_SIZE = 1020

class ContentRequestMessage(Message):

	"""
	content_id (integer)
	seq_no (integer)

	"""

	size = 4

	def __init__(self, content_id, seq_no):
		self.content_id = content_id
		self.seq_no = seq_no

	def send(self, soc):
		soc.send(pack('HH', self.content_id, self.seq_no))

	def receive(self, soc):
		arr = soc.recv(ContentRequestMessage.size)
		if len(arr) < ContentRequestMessage.size:
			self.received = False
		else:
			self.received = True
			content_id, seq_no = unpack('HH', arr)
			self.content_id = content_id
			self.seq_no = seq_no

class FileDetailsMessage(Message):

	"""
	content_id (integer)
	file_size (integer)
	file_name (str)
	"""

	size = 256

	def __init__(self, content_id, file_size, file_name):
		self.content_id = content_id
		self.file_size = file_size
		self.file_name = file_name

	def send(self, soc):
		soc.send(pack(str(FILENAME_MAX_LEN)+'sHH', self.file_name.encode(), self.file_size, self.content_id))

	def receive(self, soc):
		arr = soc.recv(FileDetailsMessage.size)
		if len(arr) < FileDetailsMessage.size:
			self.received = False
		else:
			self.received = True
			file_name, file_size, content_id = unpack(str(FILENAME_MAX_LEN)+'sHH', arr)
			self.file_name = file_name
			self.file_size = file_size
			self.content_id = content_id

class ContentMessage(Message):

	"""
	content_id (integer)
	seq_no (integer)
	data (bytes)
	"""

	size = 1024

	def __init__(self, content_id, seq_no):
		self.content_id = content_id
		self.seq_no = seq_no
		self.data = None

	def send(self, soc):
		soc.send(pack('HH' + str(MAX_DATA_PACKET_SIZE) + 's', self.content_id, self.seq_no, self.data))

	def receive(self, soc):
		arr = soc.recv(ContentMessage.size)
		if len(arr) < ContentMessage.size:
			self.received = False
		else:
			self.received = True
			content_id, seq_no, data = unpack('HH' + str(MAX_DATA_PACKET_SIZE) + 's', arr)
			self.content_id = content_id
			self.seq_no = seq_no
			self.data = data
