"""Tests for the tap function."""
import pytest

from pipeline.tap import tap


class TestTapBasic:
	"""Test basic tap functionality."""

	def test_tap_returns_original_value(self):
		"""Test that tap returns the original value unchanged."""
		value = 42
		def side_effect(x):
			pass
		result = tap(value, side_effect)
		assert result == value
		assert result is value

	def test_tap_with_mutable_does_not_modify_original(self):
		"""Test that tap with mutable does not modify original."""
		original = {'key': 'value', 'list': [1, 2, 3]}
		def modify(x):
			x['key'] = 'modified'
			x['list'].append(4)
		result = tap(original, modify)
		assert result is original
		assert original == {'key': 'value', 'list': [1, 2, 3]}

	def test_tap_side_effect_executed(self):
		"""Test that the side effect function is executed."""
		executed = []
		def side_effect(x):
			executed.append(x)
		tap(42, side_effect)
		assert executed == [42]


class TestTapSideEffects:
	"""Test tap side effects."""

	def test_tap_with_print_like_function(self):
		"""Test tap with a function that captures output."""
		captured = []
		def capture_output(x):
			captured.append(f"Value: {x}")
		value = {'data': [1, 2, 3]}
		result = tap(value, capture_output)
		assert result is value
		assert len(captured) == 1

	def test_tap_modifies_deep_copy_not_original(self):
		"""Test that modifications in side effect don't affect original."""
		original = {'nested': {'deep': 'value'}, 'list': [1, 2, 3]}
		def mutate(x):
			x['nested']['deep'] = 'modified'
			x['list'].append(999)
			x['new_key'] = 'new'
		result = tap(original, mutate)
		assert result is original
		assert result == {'nested': {'deep': 'value'}, 'list': [1, 2, 3]}

	def test_tap_with_multiple_side_effects(self):
		"""Test tap with function that has multiple side effects."""
		effects = []
		def multi_effect(x):
			effects.append('started')
			x['modified'] = True
			effects.append('ended')
		value = {'original': True}
		result = tap(value, multi_effect)
		assert result == {'original': True}
		assert effects == ['started', 'ended']


class TestTapWithArgs:
	"""Test tap with additional arguments."""

	def test_tap_with_positional_args(self):
		"""Test tap with additional positional arguments."""
		results = []
		def func_with_args(value, arg1, arg2):
			results.append((value, arg1, arg2))
		tap(42, func_with_args, 'extra1', 'extra2')
		assert len(results) == 1
		assert results[0] == (42, 'extra1', 'extra2')

	def test_tap_with_keyword_args(self):
		"""Test tap with keyword arguments."""
		results = []
		def func_with_kwargs(value, key1=None, key2=None):
			results.append({'value': value, 'key1': key1, 'key2': key2})
		tap(42, func_with_kwargs, key1='val1', key2='val2')
		assert results[0] == {'value': 42, 'key1': 'val1', 'key2': 'val2'}

	def test_tap_with_mixed_args(self):
		"""Test tap with both positional and keyword arguments."""
		results = []
		def func_mixed(value, pos_arg, kw_arg=None):
			results.append({'value': value, 'pos': pos_arg, 'kw': kw_arg})
		tap(42, func_mixed, 'positional', kw_arg='keyword')
		assert results[0] == {'value': 42, 'pos': 'positional', 'kw': 'keyword'}


class TestTapTypes:
	"""Test tap with different types."""

	def test_tap_with_lists(self):
		"""Test tap with lists."""
		original = [1, 2, 3]
		def modify_list(lst):
			lst.append(4)
		result = tap(original, modify_list)
		assert result == [1, 2, 3]

	def test_tap_with_dicts(self):
		"""Test tap with dictionaries."""
		original = {'a': 1, 'b': 2}
		def modify_dict(d):
			d['c'] = 3
		result = tap(original, modify_dict)
		assert result == {'a': 1, 'b': 2}

	def test_tap_with_custom_objects(self):
		"""Test tap with custom objects."""
		class CustomClass:
			def __init__(self, value):
				self.value = value
		obj = CustomClass(42)
		def modify_obj(o):
			o.value = 100
		result = tap(obj, modify_obj)
		assert result is obj
		assert result.value == 42

	def test_tap_with_none(self):
		"""Test tap with None value."""
		result = tap(None, lambda x: x)
		assert result is None


class TestTapExceptions:
	"""Test tap error handling."""

	def test_tap_non_callable_function(self):
		"""Test tap with non-callable raises TypeError."""
		with pytest.raises(TypeError, match="function is not callable"):
			tap(42, "not_callable")

	def test_tap_exceptions_from_deepcopy(self):
		"""Test that deepcopy exceptions are propagated."""
		class NonCopyable:
			def __deepcopy__(self, memo):
				raise RuntimeError("Cannot copy")
		obj = NonCopyable()
		with pytest.raises(RuntimeError, match="Cannot copy"):
			tap(obj, lambda x: None)

	def test_tap_exceptions_from_side_effect(self):
		"""Test that exceptions from side effect are propagated."""
		def raise_error(x):
			raise ValueError("Side effect error")
		with pytest.raises(ValueError, match="Side effect error"):
			tap(42, raise_error)


class TestTapInChains:
	"""Test tap in functional chains."""

	def test_tap_in_compose_like_chain(self):
		"""Test tap used in a function composition chain."""
		logs = []
		def add_five(x):
			return x + 5
		def log_value(x):
			logs.append(x)
		def multiply_two(x):
			return x * 2

		result = add_five(10)
		result = tap(result, log_value)
		result = multiply_two(result)

		assert result == 30	 # (10 + 5) * 2
		assert logs == [15]

	def test_tap_return_value_ignored(self):
		"""Test that tap ignores the return value of the side effect function."""
		def returns_something(x):
			return "this should be ignored"
		result = tap(42, returns_something)
		assert result == 42
