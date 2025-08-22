import pytest
from scheduler.executor import execute_task
from scheduler.models import Task


@pytest.mark.asyncio
async def test_execute_exec_success():
    """Test successful execution of an 'exec' task."""
    task = Task(type="exec", arguments="echo 'hello world'")
    result = await execute_task(task)
    assert result.return_code == 0
    assert result.stdout == "hello world"
    assert result.stderr == ""
    assert result.exception is None


@pytest.mark.asyncio
async def test_execute_exec_failure():
    """Test failing execution of an 'exec' task."""
    task = Task(type="exec", arguments="exit 1")
    result = await execute_task(task)
    assert result.return_code == 1
    assert result.stdout == ""
    assert result.stderr == ""
    assert result.exception is None


@pytest.mark.asyncio
async def test_execute_exec_stderr():
    """Test an 'exec' task that writes to stderr."""
    task = Task(type="exec", arguments="echo 'error message' >&2")
    result = await execute_task(task)
    assert result.return_code == 0
    assert result.stdout == ""
    assert result.stderr == "error message"
    assert result.exception is None


@pytest.mark.asyncio
async def test_execute_eval_success():
    """Test successful execution of an 'eval' task."""
    task = Task(type="eval", arguments="print('hello from eval')")
    result = await execute_task(task)
    assert result.return_code == 0
    assert result.stdout == "hello from eval"
    assert result.stderr == ""
    assert result.exception is None


@pytest.mark.asyncio
async def test_execute_eval_stderr():
    """Test an 'eval' task that writes to stderr."""
    task = Task(
        type="eval",
        arguments="import sys; print('eval error', file=sys.stderr)"
    )
    result = await execute_task(task)
    assert result.return_code == 0
    assert result.stdout == ""
    assert result.stderr == "eval error"
    assert result.exception is None


@pytest.mark.asyncio
async def test_execute_eval_exception():
    """Test an 'eval' task that raises an exception."""
    task = Task(type="eval", arguments="raise ValueError('eval exception')")
    result = await execute_task(task)
    assert result.return_code is None
    assert result.stdout == ""
    assert result.stderr == ""
    assert isinstance(result.exception, ValueError)
