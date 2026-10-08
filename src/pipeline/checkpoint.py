"""Utility for synchronizing execution between threads."""
import threading


class Checkpoint:
	"""A synchronization point that pauses execution until continued."""
	def __init__(self):
		self._condition = threading.Condition()
		self._value = None
		self._generation = 0
		self._next = False
	def __call__(self, value):
		"""Publish a value and pause until ``next()`` is called."""
		with self._condition:
			self._value = value
			self._generation += 1
			self._next = False
			self._condition.notify_all()
			while not self._next:
				self._condition.wait()
		return value
	def next(self):
		"""Allow the current checkpoint to continue."""
		with self._condition:
			self._next = True
			self._condition.notify_all()
	def wait(self):
		"""Wait until the checkpoint is reached again."""
		with self._condition:
			generation = self._generation
			while self._generation == generation:
				self._condition.wait()
	@property
	def value(self):
		"""Return the most recently published value."""
		with self._condition:
			return self._value
