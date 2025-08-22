from graphlib import TopologicalSorter
from typing import Dict
from scheduler.logger import get_logger
from scheduler.models import Task, TaskStatus

logger = get_logger(__name__)


class TaskTracker:
    tasks: Dict[str, Task]
    topo_sorter: TopologicalSorter

    def __init__(self):
        self.tasks = {}
        self.topo_sorter = TopologicalSorter()

    def add_task(self, name: str, task: Task):
        """Adds a task to the tracker.

        :param name: The name of the task.
        :param task: The task object to add.
        """

        self.tasks[name] = task

    def validate_dependencies(self):
        """Check if all task dependencies refer to existing tasks.

        :raises KeyError: If a task has a dependency on a task that
                          does not exist.
        """

        all_task_names = set(self.tasks.keys())
        for task_name, task in self.tasks.items():
            missing_deps = set(task.dependencies) - all_task_names
            if missing_deps:
                raise KeyError(
                    f"Task '{task_name}' has unknown dependencies: "
                    f"{', '.join(missing_deps)}"
                )

    def prepare_topo_sorter(self):
        """Prepare the topological sorter with the current task graph.

        This method validates task dependencies and then prepares the
        topological sorter. It ensures the task graph is valid before
        execution can begin.

        :raises KeyError: If a task has a dependency on a task that
                          does not exist.
        :raises graphlib.CycleError: If a circular dependency is detected in
                                     the task graph.
        """

        self.validate_dependencies()

        graph = {name: set(task.dependencies)
                 for name, task in self.tasks.items()}
        logger.debug(graph)

        self.topo_sorter = TopologicalSorter(graph)
        self.topo_sorter.prepare()

    def _check_failed_dependencies(self, task: Task) -> bool:
        """Check if any of a task's dependencies have failed or been skipped.

        :param task: The task to check the dependencies of.
        :return: True if any dependency has failed or been skipped,
                 False otherwise.
        """

        logger.debug(
            "Deps status: "
            f"{[self.tasks[dep].status for dep in task.dependencies]}"
        )
        return any(
            self.tasks[dep].status in
            (TaskStatus.FAILED, TaskStatus.SKIPPED)
            for dep in task.dependencies)

    def get_ready(self) -> set[str]:
        """Get a set of tasks that are ready to be executed.

        This method retrieves tasks that are ready from the topological sorter.
        It also checks for tasks whose dependencies have failed or been
        skipped, and marks them as SKIPPED. Such tasks are not included in the
        returned set.

        :return: A set of names of the tasks that are ready to be executed.
        """

        ready_tasks = self.topo_sorter.get_ready()

        to_run_tasks = set()
        for task_name in ready_tasks:
            if self._check_failed_dependencies(self.tasks[task_name]):
                logger.info(f"Skipped: {task_name}")
                self.tasks[task_name].status = TaskStatus.SKIPPED
                self.topo_sorter.done(task_name)
            else:
                to_run_tasks.add(task_name)

        return to_run_tasks
