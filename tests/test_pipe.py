"""Tests for pipe and step classes."""
import pytest
from pipeline import pipe, step


class TestStepBasic:
    """Test basic step functionality."""

    def test_step_creation(self):
        """Test creating a step."""
        def add(x, amount):
            return x + amount
        s = step(add, 5)
        assert s.function is add
        assert s.args == (5,)
        assert s.kwargs == {}

    def test_step_call(self):
        """Test calling a step."""
        def add(x, amount):
            return x + amount
        s = step(add, 5)
        result = s(10)
        assert result == 15

    def test_step_with_kwargs(self):
        """Test step with keyword arguments."""
        def power(x, exp=2):
            return x ** exp
        s = step(power, exp=3)
        result = s(2)
        assert result == 8

    def test_step_with_args_and_kwargs(self):
        """Test step with both args and kwargs."""
        def func(x, a, b, c=None):
            return x + a + b + (c or 0)
        s = step(func, 1, 2, c=3)
        result = s(10)
        assert result == 16


class TestStepOperators:
    """Test step operator overloads."""

    def test_step_pipe_operator(self):
        """Test pipe operator (|) for step."""
        def add(x, amount):
            return x + amount
        s = step(add, 5)
        result = 10 | s
        assert result == 15

    def test_step_multiplication_operator(self):
        """Test multiplication operator for step repetition."""
        def add(x, amount):
            return (x or 0) + amount
        s = step(add, 5)
        result = s * 3
        assert result == 15  # Starts with None: None->5, 5->10, 10->15

    def test_step_multiplication_with_zero(self):
        """Test step multiplication with 0."""
        def add(x, amount):
            return (x or 0) + amount
        s = step(add, 5)
        with pytest.raises(ValueError, match="other < 1"):
            s * 0

    def test_step_multiplication_with_negative(self):
        """Test step multiplication with negative."""
        def add(x, amount):
            return (x or 0) + amount
        s = step(add, 5)
        with pytest.raises(ValueError, match="other < 1"):
            s * -1

    def test_step_chaining_with_pipe_operator(self):
        """Test chaining steps with pipe operator."""
        def add(x, amount):
            return x + amount
        def multiply(x, factor):
            return x * factor

        s1 = step(add, 5)
        s2 = step(multiply, 2)

        result = 10 | s1 | s2
        assert result == 30  # 10 + 5 = 15, then 15 * 2 = 30


class TestStepExport:
    """Test step export functionality."""

    def test_export_function_only(self):
        """Test export with function only."""
        def func(x):
            return x
        s = step(func)
        exported = s.export()
        assert exported == (func,)

    def test_export_with_args(self):
        """Test export with positional arguments."""
        def func(x, a, b):
            return x + a + b
        s = step(func, 1, 2)
        exported = s.export()
        assert exported == (func, (1, 2))

    def test_export_with_kwargs(self):
        """Test export with keyword arguments."""
        def func(x, a=None, b=None):
            return x
        s = step(func, a=1, b=2)
        exported = s.export()
        assert exported == (func, {'a': 1, 'b': 2})

    def test_export_with_args_and_kwargs(self):
        """Test export with both args and kwargs."""
        def func(x, a, b=None):
            return x
        s = step(func, 1, b=2)
        exported = s.export()
        assert exported == (func, (1,), {'b': 2})


class TestStepIteration:
    """Test step iteration/unpacking."""

    def test_step_iter(self):
        """Test iterating over step (unpacking)."""
        def func(x, a):
            return x + a
        s = step(func, 5)
        unpacked = tuple(s)
        assert unpacked == (func, (5,))

    def test_step_unpacking_in_tuple(self):
        """Test unpacking step in tuple."""
        def func(x, a):
            return x + a
        s = step(func, 5)
        pipeline_step = (*s,)
        assert pipeline_step == (func, (5,))


class TestStepRepr:
    """Test step representation."""

    def test_step_repr(self):
        """Test step repr output."""
        def add(x, amount):
            return x + amount
        s = step(add, 5)
        repr_str = repr(s)
        assert "step" in repr_str.lower()
        assert "add" in repr_str


class TestStepErrors:
    """Test step error handling."""

    def test_step_non_callable(self):
        """Test step with non-callable raises TypeError."""
        with pytest.raises(TypeError, match="function is not callable"):
            step("not_callable")


class TestPipeBasic:
    """Test basic pipe functionality."""

    def test_pipe_wrapping(self):
        """Test pipe wraps a function."""
        @pipe
        def add(x, amount):
            return x + amount
        assert callable(add)

    def test_pipe_creates_step(self):
        """Test pipe creates a step when called."""
        @pipe
        def add(x, amount):
            return x + amount
        s = add(5)
        assert isinstance(s, step)

    def test_pipe_step_execution(self):
        """Test executing a step created from pipe."""
        @pipe
        def add(x, amount):
            return x + amount
        s = add(5)
        result = s(10)
        assert result == 15

    def test_pipe_preserves_metadata(self):
        """Test that pipe preserves function metadata."""
        @pipe
        def my_function(x):
            """Test docstring."""
            return x + 1
        assert my_function.__name__ == "my_function"
        assert "Test docstring" in my_function.__doc__


class TestPipeNonCallable:
    """Test pipe error handling."""

    def test_pipe_non_callable(self):
        """Test pipe with non-callable raises TypeError."""
        with pytest.raises(TypeError, match="function is not callable"):
            pipe("not_callable")


class TestPipeRepr:
    """Test pipe representation."""

    def test_pipe_repr(self):
        """Test pipe repr output."""
        @pipe
        def my_func(x):
            return x
        repr_str = repr(my_func)
        assert "pipe" in repr_str.lower()


class TestIntegration:
    """Test integration scenarios."""

    def test_pipe_with_pipeline(self):
        """Test using pipe decorator with Pipeline."""
        from pipeline import Pipeline

        @pipe
        def add(x, amount):
            return x + amount

        pipeline = Pipeline([
            (add(5),),
            (add(10),),
        ])
        pipeline.run(10).wait()
        assert pipeline.results.get() == 25

    def test_step_chaining_order(self):
        """Test chaining multiple steps verifies left-to-right evaluation."""
        def add(x, amount):
            return x + amount
        def multiply(x, factor):
            return x * factor

        s1 = step(add, 5)
        s2 = step(multiply, 2)

        # 10 | s1 applies s1.__ror__(10) -> add(10, 5) = 15
        # 15 | s2 applies s2.__ror__(15) -> multiply(15, 2) = 30
        result = 10 | s1 | s2
        assert result == 30
