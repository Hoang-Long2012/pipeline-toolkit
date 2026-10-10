"""Utility for synchronizing execution between threads."""
import threading


class Checkpoint:
	"""A synchronization point that pauses execution until continued."""
	def __init__(self):
		self._condition = threading.Condition()
		self._value = None
		self._active = False
	def __call__(self, value):
		"""Publish a value and pause until ``next()`` is called."""
		with self._condition:
			self._value = value
			self._active = True
			self._condition.notify_all()
			while self._active:
				self._condition.wait()
		return value
	def next(self):
		"""Release the active checkpoint."""
		with self._condition:
			self._active = False
			self._condition.notify_all()
	def wait(self):
		"""Wait until a checkpoint is active."""
		with self._condition:
			while not self._active:
				self._condition.wait()
	@property
	def value(self):
		"""Return the most recently published value."""
		with self._condition:
			return self._value
	@property
	def is_active(self):
		"""Return whether the checkpoint is currently active."""
		with self._condition:
			return self._active
