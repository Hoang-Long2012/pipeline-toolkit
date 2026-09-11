"""Tests for the Stack data structure."""
import pytest

from pipeline.stack import Stack, StackOverflowError, StackUnderflowError


class TestStackInitialization:
	"""Test Stack initialization."""

	def test_init_default(self):
		"""Test stack initialization with default parameters."""
		stack = Stack()
		assert stack.empty()
		assert len(stack) == 0
		assert not bool(stack)

	def test_init_with_maxsize(self):
		"""Test stack initialization with maxsize."""
		stack = Stack(maxsize=5)
		assert stack.empty()
		assert len(stack) == 0

	def test_init_invalid_maxsize_type(self):
		"""Test stack initialization with invalid maxsize type."""
		with pytest.raises(TypeError, match="maxsize is not int"):
			Stack(maxsize="5")

	def test_init_negative_maxsize(self):
		"""Test stack initialization with negative maxsize."""
		with pytest.raises(ValueError, match="maxsize < 0"):
			Stack(maxsize=-1)


class TestStackPush:
	"""Test Stack push operation."""

	def test_push_single_item(self):
		"""Test pushing a single item."""
		stack = Stack()
		stack.push("item1")
		assert len(stack) == 1
		assert stack.get() == "item1"

	def test_push_multiple_items(self):
		"""Test pushing multiple items."""
		stack = Stack()
		stack.push("first")
		stack.push("second")
		stack.push("third")
		assert len(stack) == 3
		assert stack.get() == "third"

	def test_push_different_types(self):
		"""Test pushing different data types."""
		stack = Stack()
		stack.push(42)
		stack.push("string")
		stack.push([1, 2, 3])
		stack.push({"key": "value"})
		assert len(stack) == 4

	def test_push_to_full_stack(self):
		"""Test pushing to a full stack raises StackOverflowError."""
		stack = Stack(maxsize=2)
		stack.push("item1")
		stack.push("item2")
		with pytest.raises(StackOverflowError, match="stack overflow"):
			stack.push("item3")


class TestStackGet:
	"""Test Stack get operation."""

	def test_get_returns_top_item(self):
		"""Test get returns the top item without removing it."""
		stack = Stack()
		stack.push("first")
		stack.push("second")
		assert stack.get() == "second"
		assert len(stack) == 2

	def test_get_from_empty_stack(self):
		"""Test get on empty stack raises StackUnderflowError."""
		stack = Stack()
		with pytest.raises(StackUnderflowError, match="stack underflow"):
			stack.get()

	def test_get_multiple_times(self):
		"""Test multiple get operations return the same item."""
		stack = Stack()
		stack.push("item")
		assert stack.get() == "item"
		assert stack.get() == "item"
		assert len(stack) == 1


class TestStackPop:
	"""Test Stack pop operation."""

	def test_pop_removes_and_returns_item(self):
		"""Test pop removes and returns the top item."""
		stack = Stack()
		stack.push("first")
		stack.push("second")
		assert stack.pop() == "second"
		assert len(stack) == 1

	def test_pop_from_empty_stack(self):
		"""Test pop on empty stack raises StackUnderflowError."""
		stack = Stack()
		with pytest.raises(StackUnderflowError, match="stack underflow"):
			stack.pop()

	def test_pop_all_items(self):
		"""Test popping all items from stack."""
		stack = Stack()
		stack.push("a")
		stack.push("b")
		stack.push("c")
		assert stack.pop() == "c"
		assert stack.pop() == "b"
		assert stack.pop() == "a"
		assert stack.empty()


class TestStackClear:
	"""Test Stack clear operation."""

	def test_clear_empties_stack(self):
		"""Test clear removes all items."""
		stack = Stack()
		stack.push("a")
		stack.push("b")
		stack.clear()
		assert stack.empty()
		assert len(stack) == 0

	def test_clear_empty_stack(self):
		"""Test clear on already empty stack."""
		stack = Stack()
		stack.clear()
		assert stack.empty()


class TestStackUtilities:
	"""Test Stack utility methods."""

	def test_empty_method(self):
		"""Test empty method."""
		stack = Stack()
		assert stack.empty()
		stack.push("item")
		assert not stack.empty()

	def test_full_method(self):
		"""Test full method."""
		stack = Stack(maxsize=2)
		assert not stack.full()
		stack.push("a")
		assert not stack.full()
		stack.push("b")
		assert stack.full()

	def test_full_unlimited_stack(self):
		"""Test full on unlimited stack always returns False."""
		stack = Stack()
		for _ in range(100):
			stack.push("item")
		assert not stack.full()

	def test_len(self):
		"""Test len function."""
		stack = Stack()
		assert len(stack) == 0
		stack.push("a")
		assert len(stack) == 1
		stack.push("b")
		assert len(stack) == 2

	def test_bool_empty_stack(self):
		"""Test bool on empty stack."""
		stack = Stack()
		assert not bool(stack)

	def test_bool_non_empty_stack(self):
		"""Test bool on non-empty stack."""
		stack = Stack()
		stack.push("item")
		assert bool(stack)

	def test_contains(self):
		"""Test contains operator."""
		stack = Stack()
		stack.push("a")
		stack.push("b")
		assert "a" in stack
		assert "b" in stack
		assert "c" not in stack

	def test_iter(self):
		"""Test iteration over stack from top to bottom."""
		stack = Stack()
		stack.push("a")
		stack.push("b")
		stack.push("c")
		assert list(stack) == ["c", "b", "a"]
		assert len(stack) == 3

	def test_repr(self):
		"""Test repr output."""
		stack = Stack(maxsize=5)
		stack.push("a")
		repr_str = repr(stack)
		assert "Stack" in repr_str
		assert "maxsize=5" in repr_str


class TestStackLifo:
	"""Test Stack LIFO behavior."""

	def test_lifo_order(self):
		"""Test Last-In-First-Out order."""
		stack = Stack()
		for i in range(5):
			stack.push(i)
		for i in range(4, -1, -1):
			assert stack.pop() == i
