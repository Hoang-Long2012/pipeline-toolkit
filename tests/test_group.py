"""Tests for the Group class."""

import pytest

from pipeline import Group, Pipeline


def _increment(value):
	return value + 1


def _double(value):
	return value * 2


class TestGroupInitialization:
	"""Test Group initialization."""

	def test_init_default_is_empty(self):
		"""Test default initialization creates an empty group."""
		group = Group()
		assert len(group) == 0

	def test_init_with_pipelines(self):
		"""Test initialization with a sequence of Pipeline objects."""
		p1 = Pipeline()
		p2 = Pipeline()
		group = Group([p1, p2])
		assert group[0] is p1
		assert group[1] is p2

	def test_init_with_subgroups(self):
		"""Test initialization with a sequence of nested Group objects."""
		subgroup = Group([Pipeline()])
		group = Group([subgroup])
		assert group[0] is subgroup

	def test_init_with_mixed_items(self):
		"""Test initialization with both Pipeline and Group objects."""
		p = Pipeline()
		subgroup = Group()
		group = Group([p, subgroup])
		assert group[0] is p
		assert group[1] is subgroup

	def test_init_with_generator(self):
		"""Test initialization from a generator of pipelines."""
		p1 = Pipeline()
		p2 = Pipeline()

		def item_generator():
			yield p1
			yield p2

		group = Group(item_generator())
		assert len(group) == 2
		assert group[0] is p1
		assert group[1] is p2

	def test_init_from_another_group(self):
		"""Test initialization from an existing Group instance."""
		p = Pipeline()
		original = Group([p])
		new_group = Group(original)
		assert len(new_group) == 1
		assert new_group[0] is p

	def test_init_invalid_item_type(self):
		"""Test initialization with invalid item raises TypeError."""
		with pytest.raises(TypeError, match="Pipeline or Group"):
			Group(["not_a_pipeline"])

	def test_init_non_iterable(self):
		"""Test initialization with non-iterable raises TypeError."""
		with pytest.raises(TypeError):
			Group(123)


class TestGroupAdd:
	"""Test Group add method."""

	def test_add_pipeline(self):
		"""Test adding a Pipeline instance."""
		group = Group()
		p = Pipeline()
		group.add(p)
		assert len(group) == 1
		assert group[0] is p

	def test_add_subgroup(self):
		"""Test adding a nested Group instance."""
		group = Group()
		subgroup = Group()
		group.add(subgroup)
		assert len(group) == 1
		assert group[0] is subgroup

	def test_add_preserves_insertion_order(self):
		"""Test sequential add calls maintain order."""
		group = Group()
		p1 = Pipeline()
		p2 = Pipeline()
		group.add(p1)
		group.add(p2)
		assert group[0] is p1
		assert group[1] is p2

	def test_add_invalid_type(self):
		"""Test adding invalid item raises TypeError."""
		group = Group()
		with pytest.raises(TypeError, match="Pipeline or Group"):
			group.add("invalid")


class TestGroupInsert:
	"""Test Group insert method."""

	def test_insert_pipeline_at_beginning(self):
		"""Test inserting pipeline at index 0."""
		p1 = Pipeline()
		p2 = Pipeline()
		group = Group([p1])
		group.insert(0, p2)
		assert group[0] is p2
		assert group[1] is p1

	def test_insert_pipeline_in_middle(self):
		"""Test inserting pipeline in the middle of a group."""
		p1 = Pipeline()
		p2 = Pipeline()
		p3 = Pipeline()
		group = Group([p1, p2])
		group.insert(1, p3)
		assert group[0] is p1
		assert group[1] is p3
		assert group[2] is p2

	def test_insert_pipeline_beyond_length(self):
		"""Test inserting pipeline at index beyond current length appends."""
		p1 = Pipeline()
		p2 = Pipeline()
		group = Group([p1])
		group.insert(100, p2)
		assert len(group) == 2
		assert group[1] is p2

	def test_insert_subgroup(self):
		"""Test inserting nested group at specified index."""
		p = Pipeline()
		subgroup = Group()
		group = Group([p])
		group.insert(0, subgroup)
		assert group[0] is subgroup
		assert group[1] is p

	def test_insert_invalid_index_type_str(self):
		"""Test inserting with string index raises TypeError."""
		group = Group()
		with pytest.raises(TypeError, match="not a int"):
			group.insert("0", Pipeline())

	def test_insert_invalid_index_type_float(self):
		"""Test inserting with float index raises TypeError."""
		group = Group()
		with pytest.raises(TypeError, match="not a int"):
			group.insert(1.5, Pipeline())

	def test_insert_negative_index(self):
		"""Test inserting with negative index raises ValueError."""
		group = Group([Pipeline()])
		with pytest.raises(ValueError, match="negative"):
			group.insert(-1, Pipeline())

	def test_insert_invalid_pipeline_type(self):
		"""Test inserting invalid object raises TypeError."""
		group = Group()
		with pytest.raises(TypeError, match="Pipeline or Group"):
			group.insert(0, "invalid")


class TestGroupExtend:
	"""Test Group extend method."""

	def test_extend_with_pipelines(self):
		"""Test extending group with multiple pipelines."""
		p1 = Pipeline()
		p2 = Pipeline()
		group = Group()
		group.extend([p1, p2])
		assert len(group) == 2
		assert group[0] is p1
		assert group[1] is p2

	def test_extend_with_subgroups(self):
		"""Test extending group with nested groups."""
		sub1 = Group()
		sub2 = Group()
		group = Group()
		group.extend([sub1, sub2])
		assert len(group) == 2
		assert group[0] is sub1
		assert group[1] is sub2

	def test_extend_with_another_group(self):
		"""Test extending group with another Group instance."""
		p1 = Pipeline()
		p2 = Pipeline()
		source = Group([p1, p2])
		group = Group()
		group.extend(source)
		assert len(group) == 2
		assert group[0] is p1
		assert group[1] is p2

	def test_extend_with_generator(self):
		"""Test extending group with an item generator."""
		p1 = Pipeline()
		p2 = Pipeline()

		def item_generator():
			yield p1
			yield p2

		group = Group()
		group.extend(item_generator())
		assert len(group) == 2
		assert group[0] is p1
		assert group[1] is p2

	def test_extend_invalid_item_raises_type_error(self):
		"""Test extending with an invalid item raises TypeError."""
		group = Group()
		with pytest.raises(TypeError, match="Pipeline or Group"):
			group.extend([Pipeline(), "invalid"])

	def test_extend_failure_leaves_group_unmodified(self):
		"""Test that failure during extend leaves existing items unchanged."""
		initial_pipeline = Pipeline()
		group = Group([initial_pipeline])
		with pytest.raises(TypeError, match="Pipeline or Group"):
			group.extend([Pipeline(), "invalid"])
		assert len(group) == 1
		assert group[0] is initial_pipeline

	def test_extend_non_iterable(self):
		"""Test extending with non-iterable raises TypeError."""
		group = Group()
		with pytest.raises(TypeError):
			group.extend(123)


class TestGroupRemove:
	"""Test Group remove method."""

	def test_remove_pipeline(self):
		"""Test removing existing pipeline."""
		p = Pipeline()
		group = Group([p])
		group.remove(p)
		assert len(group) == 0

	def test_remove_subgroup(self):
		"""Test removing existing nested group."""
		subgroup = Group()
		group = Group([subgroup])
		group.remove(subgroup)
		assert len(group) == 0

	def test_remove_first_occurrence_only(self):
		"""Test remove removes only the first occurrence of duplicated pipeline."""
		p1 = Pipeline(name="p1")
		p2 = Pipeline(name="p2")
		group = Group([p1, p2, p1])
		group.remove(p1)
		assert len(group) == 2
		assert group[0] is p2
		assert group[1] is p1

	def test_remove_pipeline_not_found(self):
		"""Test removing pipeline not present raises ValueError."""
		group = Group([Pipeline(name="p1")])
		with pytest.raises(ValueError):
			group.remove(Pipeline(name="p2"))

	def test_remove_subgroup_not_found(self):
		"""Test removing nested group not present raises ValueError."""
		group = Group([Group([Pipeline(name="p1")])])
		with pytest.raises(ValueError):
			group.remove(Group([Pipeline(name="p2")]))

	def test_remove_invalid_type(self):
		"""Test removing invalid type raises TypeError."""
		group = Group()
		with pytest.raises(TypeError, match="Pipeline or Group"):
			group.remove("invalid")


class TestGroupPop:
	"""Test Group pop method."""

	def test_pop_first(self):
		"""Test popping first element."""
		p1 = Pipeline()
		p2 = Pipeline()
		group = Group([p1, p2])
		popped = group.pop(0)
		assert popped is p1
		assert len(group) == 1
		assert group[0] is p2

	def test_pop_last(self):
		"""Test popping last element."""
		p1 = Pipeline()
		p2 = Pipeline()
		group = Group([p1, p2])
		popped = group.pop(1)
		assert popped is p2
		assert len(group) == 1
		assert group[0] is p1

	def test_pop_middle(self):
		"""Test popping middle element."""
		p1 = Pipeline()
		p2 = Pipeline()
		p3 = Pipeline()
		group = Group([p1, p2, p3])
		popped = group.pop(1)
		assert popped is p2
		assert len(group) == 2
		assert group[0] is p1
		assert group[1] is p3

	def test_pop_subgroup(self):
		"""Test popping nested group."""
		subgroup = Group()
		group = Group([subgroup])
		popped = group.pop(0)
		assert popped is subgroup
		assert len(group) == 0

	def test_pop_invalid_index_type(self):
		"""Test popping with non-integer index raises TypeError."""
		group = Group([Pipeline()])
		with pytest.raises(TypeError, match="not a int"):
			group.pop("0")

	def test_pop_negative_index(self):
		"""Test popping with negative index raises ValueError."""
		group = Group([Pipeline()])
		with pytest.raises(ValueError, match="negative"):
			group.pop(-1)

	def test_pop_index_out_of_range(self):
		"""Test popping with out of range index raises IndexError."""
		group = Group([Pipeline()])
		with pytest.raises(IndexError, match="out of range"):
			group.pop(1)

	def test_pop_empty_group(self):
		"""Test popping from empty group raises IndexError."""
		group = Group()
		with pytest.raises(IndexError, match="out of range"):
			group.pop(0)


class TestGroupClear:
	"""Test Group clear method."""

	def test_clear_removes_all_items(self):
		"""Test clear empties non-empty group."""
		group = Group([Pipeline(), Group()])
		group.clear()
		assert len(group) == 0

	def test_clear_empty_group(self):
		"""Test clear on empty group executes safely."""
		group = Group()
		group.clear()
		assert len(group) == 0


class TestGroupReverse:
	"""Test Group reverse method."""

	def test_reverse_multiple_items(self):
		"""Test reversing items in place."""
		p1 = Pipeline()
		p2 = Pipeline()
		group = Group([p1, p2])
		group.reverse()
		assert group[0] is p2
		assert group[1] is p1

	def test_reverse_empty_group(self):
		"""Test reversing empty group executes safely."""
		group = Group()
		group.reverse()
		assert len(group) == 0

	def test_reverse_single_item(self):
		"""Test reversing single item group keeps item."""
		p = Pipeline()
		group = Group([p])
		group.reverse()
		assert group[0] is p


class TestGroupIndex:
	"""Test Group index method."""

	def test_index_pipeline(self):
		"""Test finding index of a pipeline."""
		p1 = Pipeline(name="p1")
		p2 = Pipeline(name="p2")
		group = Group([p1, p2])
		assert group.index(p2) == 1

	def test_index_subgroup(self):
		"""Test finding index of a nested group."""
		p = Pipeline(name="p")
		subgroup = Group([p])
		group = Group([p, subgroup])
		assert group.index(subgroup) == 1

	def test_index_returns_first_occurrence(self):
		"""Test index returns first occurrence when duplicates exist."""
		p1 = Pipeline(name="p1")
		p2 = Pipeline(name="p2")
		group = Group([p1, p2, p1])
		assert group.index(p1) == 0

	def test_index_pipeline_not_found(self):
		"""Test missing pipeline raises ValueError mentioning pipeline."""
		group = Group([Pipeline(name="p1")])
		with pytest.raises(ValueError, match="pipeline not found in group"):
			group.index(Pipeline(name="p2"))

	def test_index_subgroup_not_found(self):
		"""Test missing subgroup raises ValueError mentioning subgroup."""
		group = Group([Pipeline(name="p1")])
		with pytest.raises(ValueError, match="sub-group not found in group"):
			group.index(Group())

	def test_index_invalid_type(self):
		"""Test finding index of invalid object raises TypeError."""
		group = Group()
		with pytest.raises(TypeError, match="Pipeline or Group"):
			group.index("invalid")


class TestGroupCount:
	"""Test Group count method."""

	def test_count_pipeline_not_found(self):
		"""Test count returns 0 for absent pipeline."""
		group = Group([Pipeline(name="p1")])
		assert group.count(Pipeline(name="p2")) == 0

	def test_count_pipeline_single(self):
		"""Test count returns 1 for pipeline present once."""
		p1 = Pipeline(name="p1")
		p2 = Pipeline(name="p2")
		group = Group([p1, p2])
		assert group.count(p1) == 1

	def test_count_pipeline_multiple(self):
		"""Test count returns correct frequency for duplicates."""
		p1 = Pipeline(name="p1")
		p2 = Pipeline(name="p2")
		group = Group([p1, p2, p1])
		assert group.count(p1) == 2

	def test_count_subgroup(self):
		"""Test count for nested group."""
		subgroup = Group()
		group = Group([subgroup, subgroup])
		assert group.count(subgroup) == 2

	def test_count_invalid_type(self):
		"""Test count with invalid object raises TypeError."""
		group = Group()
		with pytest.raises(TypeError, match="Pipeline or Group"):
			group.count("invalid")


class TestGroupGetItem:
	"""Test Group __getitem__ method."""

	def test_getitem_valid_index(self):
		"""Test retrieving pipeline by valid index."""
		p = Pipeline()
		group = Group([p])
		assert group[0] is p

	def test_getitem_subgroup(self):
		"""Test retrieving nested group by index."""
		subgroup = Group()
		group = Group([subgroup])
		assert group[0] is subgroup

	def test_getitem_invalid_index_type_str(self):
		"""Test getitem with string index raises TypeError."""
		group = Group([Pipeline()])
		with pytest.raises(TypeError, match="not a int"):
			_ = group["0"]

	def test_getitem_invalid_index_type_slice(self):
		"""Test getitem with slice raises TypeError."""
		group = Group([Pipeline()])
		with pytest.raises(TypeError, match="not a int"):
			_ = group[0:1]

	def test_getitem_negative_index(self):
		"""Test getitem with negative index raises ValueError."""
		group = Group([Pipeline()])
		with pytest.raises(ValueError, match="negative"):
			_ = group[-1]

	def test_getitem_index_out_of_range(self):
		"""Test getitem with out of range index raises IndexError."""
		group = Group([Pipeline()])
		with pytest.raises(IndexError, match="out of range"):
			_ = group[1]

	def test_getitem_empty_group(self):
		"""Test getitem on empty group raises IndexError."""
		group = Group()
		with pytest.raises(IndexError, match="out of range"):
			_ = group[0]


class TestGroupSetItem:
	"""Test Group __setitem__ method."""

	def test_setitem_valid_pipeline(self):
		"""Test replacing item with a pipeline."""
		p1 = Pipeline()
		p2 = Pipeline()
		group = Group([p1])
		group[0] = p2
		assert group[0] is p2

	def test_setitem_subgroup(self):
		"""Test replacing item with a nested group."""
		p = Pipeline()
		subgroup = Group()
		group = Group([p])
		group[0] = subgroup
		assert group[0] is subgroup

	def test_setitem_invalid_index_type(self):
		"""Test setitem with non-integer index raises TypeError."""
		group = Group([Pipeline()])
		with pytest.raises(TypeError, match="not a int"):
			group["0"] = Pipeline()

	def test_setitem_negative_index(self):
		"""Test setitem with negative index raises ValueError."""
		group = Group([Pipeline()])
		with pytest.raises(ValueError, match="negative"):
			group[-1] = Pipeline()

	def test_setitem_index_out_of_range(self):
		"""Test setitem with out of range index raises IndexError."""
		group = Group([Pipeline()])
		with pytest.raises(IndexError, match="out of range"):
			group[1] = Pipeline()

	def test_setitem_invalid_pipeline_type(self):
		"""Test setitem with invalid object raises TypeError."""
		group = Group([Pipeline()])
		with pytest.raises(TypeError, match="Pipeline or Group"):
			group[0] = "invalid"


class TestGroupDelItem:
	"""Test Group __delitem__ method."""

	def test_delitem_valid_index(self):
		"""Test deleting item at valid index shifts remaining items."""
		p1 = Pipeline()
		p2 = Pipeline()
		group = Group([p1, p2])
		del group[0]
		assert len(group) == 1
		assert group[0] is p2

	def test_delitem_invalid_index_type(self):
		"""Test delitem with non-integer index raises TypeError."""
		group = Group([Pipeline()])
		with pytest.raises(TypeError, match="not a int"):
			del group["0"]

	def test_delitem_negative_index(self):
		"""Test delitem with negative index raises ValueError."""
		group = Group([Pipeline()])
		with pytest.raises(ValueError, match="negative"):
			del group[-1]

	def test_delitem_index_out_of_range(self):
		"""Test delitem with out of range index raises IndexError."""
		group = Group([Pipeline()])
		with pytest.raises(IndexError, match="out of range"):
			del group[1]

	def test_delitem_empty_group(self):
		"""Test delitem on empty group raises IndexError."""
		group = Group()
		with pytest.raises(IndexError, match="out of range"):
			del group[0]


class TestGroupContains:
	"""Test Group __contains__ method."""

	def test_contains_pipeline_true(self):
		"""Test in operator returns True for contained pipeline."""
		p = Pipeline()
		group = Group([p])
		assert p in group

	def test_contains_pipeline_false(self):
		"""Test in operator returns False for absent pipeline."""
		group = Group([Pipeline(name="p1")])
		assert Pipeline(name="p2") not in group

	def test_contains_subgroup_true(self):
		"""Test in operator returns True for contained nested group."""
		subgroup = Group()
		group = Group([subgroup])
		assert subgroup in group

	def test_contains_subgroup_false(self):
		"""Test in operator returns False for absent nested group."""
		group = Group([Group([Pipeline(name="p1")])])
		assert Group([Pipeline(name="p2")]) not in group

	def test_contains_invalid_type(self):
		"""Test in operator with invalid object raises TypeError."""
		group = Group()
		with pytest.raises(TypeError, match="Pipeline or Group"):
			_ = "invalid" in group


class TestGroupIteration:
	"""Test Group __iter__ and __reversed__ methods."""

	def test_iter_yields_all_items_in_order(self):
		"""Test iteration yields all items in insertion order."""
		p1 = Pipeline()
		sub = Group()
		p2 = Pipeline()
		group = Group([p1, sub, p2])
		assert list(group) == [p1, sub, p2]

	def test_iter_empty_group(self):
		"""Test iteration over empty group yields no items."""
		assert list(Group()) == []

	def test_reversed_yields_items_in_reverse_order(self):
		"""Test reversed yields items in backward order."""
		p1 = Pipeline()
		sub = Group()
		p2 = Pipeline()
		group = Group([p1, sub, p2])
		assert list(reversed(group)) == [p2, sub, p1]

	def test_reversed_empty_group(self):
		"""Test reversed over empty group yields no items."""
		assert list(reversed(Group())) == []


class TestGroupSizingAndTruthiness:
	"""Test Group __len__ and __bool__ methods."""

	def test_len_empty(self):
		"""Test len of empty group is 0."""
		assert len(Group()) == 0

	def test_len_with_items(self):
		"""Test len reflects number of items."""
		assert len(Group([Pipeline(), Group()])) == 2

	def test_bool_empty(self):
		"""Test empty group evaluates to False."""
		assert not bool(Group())

	def test_bool_with_items(self):
		"""Test non-empty group evaluates to True."""
		assert bool(Group([Pipeline()]))


class TestGroupCopy:
	"""Test Group copy method and its shallow copy semantics."""

	def test_copy_returns_new_group_instance(self):
		"""Test copy creates a distinct Group instance."""
		group = Group([Pipeline()])
		copied = group.copy()
		assert copied is not group

	def test_copy_equals_original(self):
		"""Test copied group equals the original group."""
		group = Group([Pipeline()])
		copied = group.copy()
		assert copied == group

	def test_copy_internal_container_is_independent(self):
		"""Test internal pipelines container is distinct from the original."""
		group = Group([Pipeline()])
		copied = group.copy()
		assert copied._pipelines is not group._pipelines

	def test_copy_preserves_contained_pipeline_instances(self):
		"""Test contained Pipeline instances are preserved by reference."""
		pipeline = Pipeline()
		group = Group([pipeline])
		copied = group.copy()
		assert copied[0] is pipeline

	def test_copy_preserves_nested_group_instances(self):
		"""Test contained nested Group instances are preserved by reference."""
		subgroup = Group([Pipeline()])
		group = Group([subgroup])
		copied = group.copy()
		assert copied[0] is subgroup

	def test_add_on_original_does_not_affect_copy(self):
		"""Test adding to original group does not mutate the copy."""
		group = Group([Pipeline()])
		copied = group.copy()
		group.add(Pipeline())
		assert len(group) == 2
		assert len(copied) == 1

	def test_add_on_copy_does_not_affect_original(self):
		"""Test adding to copied group does not mutate the original."""
		group = Group([Pipeline()])
		copied = group.copy()
		copied.add(Pipeline())
		assert len(group) == 1
		assert len(copied) == 2

	def test_remove_on_original_does_not_affect_copy(self):
		"""Test removing item from original group does not mutate the copy."""
		pipeline = Pipeline()
		group = Group([pipeline])
		copied = group.copy()
		group.remove(pipeline)
		assert len(group) == 0
		assert len(copied) == 1
		assert copied[0] is pipeline

	def test_replacement_on_original_does_not_affect_copy(self):
		"""Test replacing item in original group does not mutate the copy."""
		p1 = Pipeline(name="p1")
		p2 = Pipeline(name="p2")
		group = Group([p1])
		copied = group.copy()
		group[0] = p2
		assert group[0] is p2
		assert copied[0] is p1


class TestGroupEquality:
	"""Test Group __eq__ method."""

	def test_eq_identical_groups(self):
		"""Test equality between groups with identical items."""
		p = Pipeline()
		assert Group([p]) == Group([p])

	def test_eq_different_order(self):
		"""Test inequality between groups with same items in different order."""
		p1 = Pipeline(name="p1")
		p2 = Pipeline(name="p2")
		assert Group([p1, p2]) != Group([p2, p1])

	def test_eq_different_elements(self):
		"""Test inequality between groups with different pipelines."""
		assert Group([Pipeline(name="p1")]) != Group([Pipeline(name="p2")])

	def test_eq_nested_groups_equal(self):
		"""Test equality between groups containing equal nested groups."""
		p = Pipeline()
		assert Group([Group([p])]) == Group([Group([p])])

	def test_eq_non_group_type(self):
		"""Test equality comparison with non-Group object returns False."""
		p = Pipeline()
		assert (Group([p]) == [p]) is False
		assert (Group([p]) == "not_a_group") is False

	def test_ne_different_groups(self):
		"""Test != operator returns True for differing groups."""
		assert Group([Pipeline()]) != Group()

	def test_ne_non_group_type(self):
		"""Test != operator returns True when compared with non-Group object."""
		assert Group() != []


class TestGroupRepr:
	"""Test Group __repr__ method."""

	def test_repr_empty_group(self):
		"""Test repr for empty group."""
		assert repr(Group()) == "Group(pipeline=0, sub-group=0)"

	def test_repr_pipelines_only(self):
		"""Test repr for group containing only pipelines."""
		assert repr(Group([Pipeline(), Pipeline()])) == "Group(pipeline=2, sub-group=0)"

	def test_repr_subgroups_only(self):
		"""Test repr for group containing only nested groups."""
		assert repr(Group([Group(), Group()])) == "Group(pipeline=0, sub-group=2)"

	def test_repr_mixed(self):
		"""Test repr for group containing both pipelines and nested groups."""
		assert repr(Group([Pipeline(), Group()])) == "Group(pipeline=1, sub-group=1)"


class TestGroupExecution:
	"""Test Group run, wait, stop, and __call__ execution methods."""

	def test_run_returns_self(self):
		"""Test run returns the Group instance itself."""
		group = Group()
		assert group.run() is group

	def test_run_executes_pipelines(self):
		"""Test run asynchronously executes all contained pipelines."""
		p1 = Pipeline([(_increment,)], default=1)
		p2 = Pipeline([(_increment,)], default=2)
		group = Group([p1, p2])
		group.run()
		group.wait()
		assert p1.result == 2
		assert p2.result == 3

	def test_run_passes_positional_args(self):
		"""Test run passes positional arguments to contained pipelines."""
		p1 = Pipeline([(_increment,)])
		p2 = Pipeline([(_double,)])
		group = Group([p1, p2])
		group.run(10)
		group.wait()
		assert p1.result == 11
		assert p2.result == 20

	def test_run_passes_kwargs(self):
		"""Test run passes keyword arguments to contained pipelines."""
		p1 = Pipeline([(_increment,)])
		p2 = Pipeline([(_double,)])
		group = Group([p1, p2])
		group.run(default=5)
		group.wait()
		assert p1.result == 6
		assert p2.result == 10

	def test_run_propagates_to_nested_group(self):
		"""Test run triggers execution in nested groups."""
		p1 = Pipeline([(_increment,)], default=0)
		p2 = Pipeline([(_increment,)], default=10)
		p3 = Pipeline([(_increment,)], default=20)
		inner = Group([p2, p3])
		outer = Group([p1, inner])
		outer.run()
		outer.wait()
		assert p1.result == 1
		assert p2.result == 11
		assert p3.result == 21

	def test_run_passes_args_to_nested_group(self):
		"""Test run forwards positional arguments down to nested group pipelines."""
		p1 = Pipeline([(_increment,)])
		p2 = Pipeline([(_double,)])
		inner = Group([p2])
		outer = Group([p1, inner])
		outer.run(15)
		outer.wait()
		assert p1.result == 16
		assert p2.result == 30

	def test_run_passes_kwargs_to_nested_group(self):
		"""Test run forwards keyword arguments down to nested group pipelines."""
		p1 = Pipeline([(_increment,)])
		p2 = Pipeline([(_double,)])
		inner = Group([p2])
		outer = Group([p1, inner])
		outer.run(default=7)
		outer.wait()
		assert p1.result == 8
		assert p2.result == 14

	def test_wait_returns_self(self):
		"""Test wait returns the Group instance itself."""
		group = Group()
		assert group.wait() is group

	def test_wait_blocks_until_execution_finishes(self):
		"""Test wait blocks until running pipelines finish."""
		p = Pipeline([(_increment,)], default=1)
		group = Group([p])
		group.run()
		group.wait()
		assert not p.running
		assert p.result == 2

	def test_wait_propagates_to_nested_group(self):
		"""Test wait blocks until pipelines inside nested group finish."""
		p1 = Pipeline([(_increment,)], default=1)
		p2 = Pipeline([(_double,)], default=2)
		inner = Group([p2])
		outer = Group([p1, inner])
		outer.run()
		outer.wait()
		assert not p1.running
		assert not p2.running
		assert p1.result == 2
		assert p2.result == 4

	def test_wait_propagates_timeout(self):
		"""Test wait forwards timeout parameter to nested group pipelines."""
		p = Pipeline([(_increment,)], default=0)
		inner = Group([p])
		outer = Group([inner])
		outer.run(delay=1)
		ret = outer.wait(timeout=0.01)
		assert ret is outer
		assert p.running
		outer.stop()

	def test_stop_returns_self(self):
		"""Test stop returns the Group instance itself."""
		group = Group()
		assert group.stop() is group

	def test_stop_terminates_running_pipelines(self):
		"""Test stop terminates running pipelines in group."""
		p = Pipeline([(_increment,)], default=0)
		group = Group([p])
		group.run(delay=5)
		assert p.running
		group.stop()
		assert not p.running

	def test_stop_propagates_to_nested_group(self):
		"""Test stop terminates running pipelines inside nested group."""
		p1 = Pipeline([(_increment,)], default=0)
		p2 = Pipeline([(_double,)], default=0)
		inner = Group([p2])
		outer = Group([p1, inner])
		outer.run(delay=5)
		assert p1.running
		assert p2.running
		outer.stop()
		assert not p1.running
		assert not p2.running

	def test_call_returns_self(self):
		"""Test __call__ returns the Group instance itself."""
		group = Group()
		assert group() is group

	def test_call_executes_pipelines(self):
		"""Test calling group instance triggers execution identically to run()."""
		p = Pipeline([(_increment,)], default=3)
		group = Group([p])
		group()
		group.wait()
		assert p.result == 4

	def test_call_propagates_to_nested_group(self):
		"""Test calling group instance propagates execution to nested group."""
		p1 = Pipeline([(_increment,)], default=5)
		p2 = Pipeline([(_double,)], default=5)
		inner = Group([p2])
		outer = Group([p1, inner])
		outer()
		outer.wait()
		assert p1.result == 6
		assert p2.result == 10

	def test_call_passes_args_and_kwargs(self):
		"""Test calling group instance forwards arguments to pipelines."""
		p1 = Pipeline([(_increment,)])
		p2 = Pipeline([(_double,)])
		inner = Group([p2])
		outer = Group([p1, inner])
		outer(10)
		outer.wait()
		assert p1.result == 11
		assert p2.result == 20
