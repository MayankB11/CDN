from abc import ABCMeta, abstractmethod

class Message:
	""" Base class for messages"""

	def __init__(self):
		pass

	@abstractmethod
	def send(self, soc):
		pass

	@abstractmethod
	def receive(self, soc):
		pass