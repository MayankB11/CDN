import sys

from struct import *

from .message import *
from config import *

FILENAME_MAX_LEN = 236
MAX_DATA_PACKET_SIZE = 1018

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

class FileDescriptionMessage(Message):

	"""
	content_id (integer)
	file_size (integer)
	file_name (str)
        md5_val (bytes)
	"""

	size = 256

	def __init__(self, content_id, file_size, file_name, md5_val):
		self.content_id = content_id
		self.file_size = file_size
		self.file_name = file_name
		self.md5_val = md5_val

	def send(self, soc):
		soc.send(pack(str(FILENAME_MAX_LEN)+'sHH16s', self.file_name.encode(), self.file_size, self.content_id, self.md5_val))

	def receive(self, soc):
		arr = soc.recv(FileDescriptionMessage.size)
		if len(arr) < FileDescriptionMessage.size:
			self.received = False
		else:
			self.received = True
			file_name, file_size, content_id, md5_val = unpack(str(FILENAME_MAX_LEN)+'sHH16s', arr)
			self.file_name = file_name.decode().strip()
			self.file_size = file_size
			self.content_id = content_id
			self.md5_val = md5_val

class ContentMessage(Message):

	"""
	content_id (integer)
	seq_no (integer)
	packet_size (integer)
	data (bytes)
	"""

	size = 1024

	def __init__(self, content_id, seq_no):
		self.content_id = content_id
		self.seq_no = seq_no
		self.packet_size = 0
		self.data = None

	def send(self, soc):
		soc.send(pack('H' + str(MAX_DATA_PACKET_SIZE) + 'sHH', self.content_id, self.data, self.packet_size, self.seq_no))

	def receive(self, soc):
		arr = soc.recv(ContentMessage.size)
		if len(arr) < ContentMessage.size:
			self.received = False
		else:
			self.received = True
			content_id, data, packet_size, seq_no = unpack('H' + str(MAX_DATA_PACKET_SIZE) + 'sHH', arr)
			self.content_id = content_id
			self.seq_no = seq_no
			self.data = data[:packet_size]
			self.packet_size = packet_size
