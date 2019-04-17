import sys
import time
from struct import *

from .message import *
from config import *

FILENAME_MAX_LEN = 176
MAX_DATA_PACKET_SIZE = 1018

class ContentRequestMessage(Message):

	"""
	content_id (integer)
	seq_no (integer)

	"""
	signature = 'HQ'
	size = calcsize(signature)

	def __init__(self, content_id, seq_no):
		self.content_id = content_id
		self.seq_no = seq_no

	def send(self, soc):
		print("Content Request Size: ",ContentRequestMessage.size)
		print("Seq No: ",self.seq_no,"\tBytes sent: ",soc.send(pack(ContentRequestMessage.signature, self.content_id, self.seq_no)))

	def receive(self, soc):
		arr = soc.recv(ContentRequestMessage.size)
		if len(arr) < ContentRequestMessage.size:
			self.received = False
		else:
			self.received = True
			content_id, seq_no = unpack(ContentRequestMessage.signature, arr)
			self.content_id = content_id
			self.seq_no = seq_no

class FileDescriptionMessage(Message):

	"""
	content_id (integer)
	file_size (integer)
	file_name (str)
        md5_val (bytes)
	"""

	signature = 'H'+str(FILENAME_MAX_LEN)+'sQHH128s'
	size = calcsize(signature)


	def __init__(self, content_id, file_size, file_name, md5_val):
		self.content_id = content_id
		self.file_size = file_size
		self.file_name = file_name
		self.md5_val = md5_val

	def send(self, soc):
		print("Sending")
		soc.send(pack(FileDescriptionMessage.signature, len(self.file_name), self.file_name.encode(), self.file_size, self.content_id, len(self.md5_val), self.md5_val))
		print("Pack sent")

	def receive(self, soc):
		arr = soc.recv(FileDescriptionMessage.size)
		if len(arr) < FileDescriptionMessage.size:
			self.received = False
		else:
			self.received = True
			print("Receiving")
			file_name_len, file_name, file_size, content_id, md5_len, md5_val = unpack(FileDescriptionMessage.signature, arr)
			self.file_name = file_name.decode()[:file_name_len]
			self.file_size = file_size
			self.content_id = content_id
			self.md5_val = md5_val[:md5_len]

class ContentMessage(Message):

	"""
	content_id (integer)
	seq_no (integer)
	packet_size (integer)
	data (bytes)
	"""

	signature = 'H' + str(MAX_DATA_PACKET_SIZE) + 'sHQ'
	size = calcsize(signature)

	def __init__(self, content_id, seq_no):
		self.content_id = content_id
		self.seq_no = seq_no
		self.packet_size = 0
		self.data = None

	def send(self, soc):
		print("Content Message size: ",ContentMessage.size,"\tSeq No: ",self.seq_no)
		print("Bytes sent: ",soc.send(pack(ContentMessage.signature, self.content_id, self.data, self.packet_size, self.seq_no)))
		# time.sleep(0.05)

	def receive(self, soc,file_size,total_received):
		recv_size = 0
		arr = bytearray()
		while recv_size != ContentMessage.size and recv_size+total_received!=file_size:
			try:
				# print("Trying to receive........")
				temp = soc.recv(ContentMessage.size-recv_size)
				if len(temp)==0:
					self.received = False
					print("Unable to connect to edge server")
					raise Exception("Unable to connect to edge server")
			except:
				self.received = False
				print("Unable to connect to edge server")
				raise Exception("Unable to connect to edge server")
			arr = arr+temp
			recv_size+=len(temp)
			# print(recv_size)
		
		# print(len(arr))
		if len(arr) < ContentMessage.size and recv_size+total_received!=file_size:
			self.received = False
		else:
			self.received = True
			temp = bytearray(ContentMessage.size-recv_size)
			content_id, data, packet_size, seq_no = unpack(ContentMessage.signature,arr+temp)
			self.content_id = content_id
			self.seq_no = seq_no
			self.data = data[:packet_size]
			self.packet_size = packet_size
