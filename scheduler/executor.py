import asyncio
import io
from contextlib import redirect_stdout, redirect_stderr
from scheduler.logger import get_logger
from scheduler.models import Task, ExecutionResult
from typing import Tuple

logger = get_logger(__name__)


async def execute_task(task: Task) -> ExecutionResult:
    """Execute a task based on its type.

    :param task: The task to execute.
    :return: An ExecutionResult containing the output and status of the
             execution.
    :raises ValueError: If the task type is unknown.
    """

    logger.debug(f"Executing task with arguments: {task.arguments}")
    if task.type == "exec":
        return await _execute_exec(task)
    elif task.type == "eval":
        return await _execute_eval(task)
    else:
        logger.error(f"Unknown task type: {task.type}")
        raise ValueError(f"Unknown task type: {task.type}")


async def _execute_exec(task: Task) -> ExecutionResult:
    """Executes a command in a subprocess.

    This method takes an 'exec' task and runs its arguments as a shell
    command in a new subprocess. It captures the stdout, stderr, and
    return code of the command.

    :param task: The 'exec' task to execute.
    :return: An ExecutionResult containing the output and status of the
             execution.
    """

    try:
        process = await asyncio.create_subprocess_shell(
            task.arguments,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()

        return ExecutionResult(
            stdout=stdout.decode().strip(),
            stderr=stderr.decode().strip(),
            return_code=process.returncode
        )

    except Exception as e:
        logger.exception("An error occurred during exec task execution.")
        return ExecutionResult(exception=e)


def _blocking_eval(code: str) -> Tuple[str, str]:
    """Execute a Python code snippet and capture stdout and stderr.

    :param code: The Python code to execute.
    :return: A tuple containing the captured stdout and stderr as strings.
    """

    f_out = io.StringIO()
    f_err = io.StringIO()
    with redirect_stdout(f_out), redirect_stderr(f_err):
        exec(code)
    return f_out.getvalue().strip(), f_err.getvalue().strip()


async def _execute_eval(task: Task) -> ExecutionResult:
    """Execute a Python code snippet in a separate thread.

    This method takes an 'eval' task and executes its Python code
    arguments. To prevent blocking the asyncio event loop, the execution
    is performed in a separate thread using `run_in_executor`. It captures
    and returns the stdout, stderr, and any exceptions that occur.

    :param task: The 'eval' task to execute.
    :return: An ExecutionResult containing the output and status of the
             execution.
    """

    try:
        loop = asyncio.get_running_loop()
        stdout, stderr = await loop.run_in_executor(
            None, _blocking_eval, task.arguments
        )
        logger.debug(
            "Eval task completed successfully for arguments: "
            f"{task.arguments}")
        return ExecutionResult(stdout=stdout, stderr=stderr, return_code=0)
    except Exception as e:
        logger.exception("An error occurred during eval task execution.")
        return ExecutionResult(exception=e)
