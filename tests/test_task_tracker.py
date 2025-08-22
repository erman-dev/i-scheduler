from scheduler.models import Task, TaskStatus
from scheduler.task_tracker import TaskTracker


def test_execution_order():
    """Test that tasks are returned in the correct topological order."""
    task_tracker = TaskTracker()
    task_tracker.add_task(
        "task1", Task(type="exec", arguments="")
    )
    task_tracker.add_task(
        "task2", Task(type="exec", arguments="")
    )
    task_tracker.add_task(
        "task3", Task(type="exec", arguments="", dependencies=("task2",))
    )

    task_tracker.prepare_topo_sorter()

    ready_tasks = task_tracker.get_ready()
    assert ready_tasks == {"task1", "task2"}
    task_tracker.tasks["task1"].status = TaskStatus.OK
    task_tracker.tasks["task2"].status = TaskStatus.OK
    task_tracker.topo_sorter.done("task1")
    task_tracker.topo_sorter.done("task2")

    ready_tasks = task_tracker.get_ready()
    assert ready_tasks == {"task3"}


def test_dependencies_of_failed_task_are_skipped():
    """Test that dependencies of a failed task are marked as skipped and
    subsequent tasks are also skipped."""
    task_tracker = TaskTracker()
    task_tracker.add_task(
        "task1", Task(type="exec", arguments="")
    )
    task_tracker.add_task(
        "task2", Task(type="exec", arguments="", dependencies=("task1",))
    )
    task_tracker.add_task(
        "task3", Task(type="exec", arguments="", dependencies=("task2",))
    )

    task_tracker.prepare_topo_sorter()

    # Simulate task1 failing
    task_tracker.tasks["task1"].status = TaskStatus.FAILED
    ready_tasks = task_tracker.get_ready()
    assert "task1" in ready_tasks
    task_tracker.topo_sorter.done("task1")

    # Now, task2 should be skipped
    ready_tasks = task_tracker.get_ready()
    assert not ready_tasks
    assert task_tracker.tasks["task2"].status == TaskStatus.SKIPPED

    # And task3 should also be skipped
    ready_tasks = task_tracker.get_ready()
    assert not ready_tasks
    assert task_tracker.tasks["task3"].status == TaskStatus.SKIPPED
