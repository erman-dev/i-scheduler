import json
from jsonschema import validate
from scheduler.models import Task, InputModel, InputTaskModel
from scheduler.task_tracker import TaskTracker
from typing import List


def load_and_validate_data(file_path: str, schema_path: str) -> InputModel:
    """
    Loads data from a JSON file and validates it against a schema.
    """
    with open(file_path) as f:
        raw_data = json.load(f)

    with open(schema_path) as f:
        schema = json.load(f)
    validate(instance=raw_data, schema=schema)

    return InputModel.model_validate(raw_data)


def populate_task_tracker(task_tracker: TaskTracker,
                          tasks_data: List[InputTaskModel]) -> None:
    """
    Populates a TaskTracker from validated input tasks data.
    """

    for task_data in tasks_data:
        task_tracker.add_task(
            task_data.name,
            Task(
                type=task_data.type,
                arguments=task_data.arguments,
                dependencies=task_data.dependencies,
            ),
        )


def load_tasks(task_tracker: TaskTracker,
               file_path: str,
               schema_path: str) -> None:
    """
    Loads tasks from a JSON file, validates the data against an JSON schema,
    and then uses Pydantic models to create a TaskTracker.
    """
    validated_data = load_and_validate_data(file_path, schema_path)
    populate_task_tracker(task_tracker, validated_data.tasks)
