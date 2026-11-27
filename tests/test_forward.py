"""Tests for the forward function."""
import pytest

from pipeline import Pipeline, chain, forward


class TestForward:
	"""Test forward argument routing and execution behavior."""

	def test_forward_positional_first(self):
		"""Test forwarding value as the first positional argument."""
		def greet(target):
			return f"Hello, {target}!"

		result = forward("world", greet, 1)
		assert result == "Hello, world!"

	def test_forward_positional_second(self):
		"""Test forwarding value as the second positional argument."""
		def divide(a, b):
			return a / b

		result = forward(2, divide, 2, 10)
		assert result == 5.0

	def test_forward_positional_middle(self):
		"""Test forwarding value into the middle of positional arguments."""
		def join_three(a, b, c):
			return f"{a}-{b}-{c}"

		result = forward("mid", join_three, 2, "first", "last")
		assert result == "first-mid-last"

	def test_forward_positional_end(self):
		"""Test forwarding value as the last positional argument."""
		def join_three(a, b, c):
			return f"{a}-{b}-{c}"

		result = forward("end", join_three, 3, "first", "second")
		assert result == "first-second-end"

	def test_forward_positional_with_kwargs(self):
		"""Test forwarding positional argument alongside existing keyword arguments."""
		def compute(a, b, scale=1):
			return (a + b) * scale

		result = forward(5, compute, 2, 10, scale=3)
		assert result == 45

	def test_forward_keyword_argument(self):
		"""Test forwarding value as a keyword argument."""
		def greet(name, punctuation="."):
			return f"Hello, {name}{punctuation}"

		result = forward("World", greet, "name", punctuation="!")
		assert result == "Hello, World!"

	def test_forward_keyword_with_positional_args(self):
		"""Test forwarding keyword argument alongside positional arguments."""
		def greet(greeting, name, separator=" "):
			return f"{greeting}{separator}{name}"

		result = forward("Alice", greet, "name", "Hi", separator=", ")
		assert result == "Hi, Alice"

	def test_rejects_non_callable_function(self):
		"""Test forward raises TypeError when function is not callable."""
		with pytest.raises(TypeError, match="function is not a callable"):
			forward("val", "not_a_callable", 1)

	def test_rejects_invalid_target_type(self):
		"""Test forward raises TypeError when target is neither int nor str."""
		with pytest.raises(TypeError, match="target must be int or str"):
			forward("val", lambda x: x, 1.5)

		with pytest.raises(TypeError, match="target must be int or str"):
			forward("val", lambda x: x, [1])

		with pytest.raises(TypeError, match="target must be int or str"):
			forward("val", lambda x: x, None)

	def test_rejects_target_int_less_than_one(self):
		"""Test forward raises ValueError when target integer is less than 1."""
		with pytest.raises(ValueError, match=r"target < 1\."):
			forward("val", lambda x: x, 0)

		with pytest.raises(ValueError, match=r"target < 1\."):
			forward("val", lambda x: x, -1)

	def test_propagates_function_exception(self):
		"""Test forward propagates exceptions raised by the target function."""
		def failing(*args, **kwargs):
			raise RuntimeError("Execution failed")

		with pytest.raises(RuntimeError, match="Execution failed"):
			forward("val", failing, "unused")

	def test_works_as_pipeline_step(self):
		"""Test forward can be used as a step in a Pipeline."""
		def divide(a, b):
			return a / b

		pipeline = Pipeline([
			(forward, (divide, 2, 20)),
		])
		result = pipeline(4)
		assert result == 5.0

	def test_works_in_chain(self):
		"""Test forward can be used inside chain."""
		def divide(a, b):
			return a / b

		result = chain([(forward, (divide, 2, 20))], default=4)
		assert result == 5.0
