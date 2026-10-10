"""Provide context about a failed pipeline step."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorContext:
	"""Represent the context of a failed pipeline step.

	Attributes:
		index: The one-based index of the failed step.
		step: The step tuple that raised the exception.
		error: The exception raised by the step.
		previous_result: The result passed to the failed step.
	"""
	index: int
	step: tuple
	error: Exception
	previous_result: object
