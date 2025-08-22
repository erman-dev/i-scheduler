import asyncio
import argparse
from scheduler.executor import execute_task
from scheduler.loader import load_tasks
from scheduler.logger import get_logger
from scheduler.models import TaskStatus
from scheduler.task_tracker import TaskTracker
from tabulate import tabulate

logger = get_logger(__name__)


def print_summary(task_tracker: TaskTracker):
    """Print a summary of all tasks and their final status.

    :param task_tracker: The TaskTracker instance containing the tasks.
    """
    headers = ["Name", "Status", "Type", "Arguments", "Dependencies"]
    rows = []
    for name, task in task_tracker.tasks.items():
        rows.append([name, task.status.name, task.type,
                    task.arguments, ", ".join(task.dependencies)])

    logger.info(
        "\n" +
        tabulate(rows, headers=headers, tablefmt="grid", maxcolwidths=50)
    )


async def runner(task_name: str, task_tracker: TaskTracker):
    """Runs a single task and update its status in the task tracker.

    This coroutine is responsible for executing a single task. It first marks
    the task as RUNNING. It then calls the executor to run the task and waits
    for the result.

    Based on the execution result, it updates the task's status to COMPLETED
    or FAILED. It also logs any stdout, stderr, or exceptions that occur.
    Finally, it marks the task as done in the topological sorter to allow
    dependent tasks to run.

    :param task_name: The name of the task to run.
    :param task_tracker: The TaskTracker instance managing the tasks.
    """

    # Mark the task as running and run it
    logger.info(f"Started: {task_name}")
    task_tracker.tasks[task_name].status = TaskStatus.RUNNING
    result = await execute_task(task_tracker.tasks[task_name])

    # If execution was successful, mark the task as completed and print
    # output if available
    if result.return_code == 0 and result.exception is None:
        task_tracker.tasks[task_name].status = TaskStatus.COMPLETED
        if result.stdout:
            logger.info(f"Output {task_name}: {result.stdout}")

    # else mark as failed and inform the user
    else:
        task_tracker.tasks[task_name].status = TaskStatus.FAILED
        if result.stderr:
            logger.error(f"Error {task_name}: {result.stderr}")
        if result.exception:
            logger.error(f"Exception {task_name}: {result.exception}")

    logger.info(f"Ended:   {task_name}")
    task_tracker.topo_sorter.done(task_name)


async def main():
    parser = argparse.ArgumentParser(description="Task Scheduler")
    parser.add_argument("--input",
                        help="Path to the input JSON file")
    parser.add_argument("--schema",
                        help="Path to the JSON schema file for validation")
    args = parser.parse_args()

    task_tracker = TaskTracker()

    try:
        load_tasks(task_tracker, args.input, args.schema)
    except Exception as e:
        logger.error(f"Failed to load tasks: {e}")
        return

    task_tracker.prepare_topo_sorter()

    # Loop over all tasks until they are all finished
    while task_tracker.topo_sorter.is_active():
        node_group = task_tracker.get_ready()

        if not node_group:
            await asyncio.sleep(0.25)
        else:
            tasks = set()
            for node in node_group:
                task = asyncio.create_task(runner(node, task_tracker))
                tasks.add(task)
                task.add_done_callback(tasks.discard)

    print_summary(task_tracker)


if __name__ == "__main__":
    asyncio.run(main())
