import json
from jsonschema import validate
from scheduler.models import Task, InputModel, InputTaskModel
from scheduler.task_tracker import TaskTracker
from typing import List


def load_and_validate_data(file_path: str, schema_path: str) -> InputModel:
    """Load data from a JSON file and validate it against a schema.

    :param file_path: The path to the input JSON file.
    :param schema_path: The path to the JSON schema file for validation.
    :return: A validated InputModel object.
    :raises jsonschema.ValidationError: If the input data is invalid against
                                     the schema.
    :raises pydantic.ValidationError: If the input data is invalid for the
                                      Pydantic model.
    """
    with open(file_path) as f:
        raw_data = json.load(f)

    with open(schema_path) as f:
        schema = json.load(f)

    validate(instance=raw_data, schema=schema)

    return InputModel.model_validate(raw_data)


def validate_unique_task_names(tasks_data: List[InputTaskModel]) -> None:
    """Check if all task names are unique.

    :param tasks_data: A list of validated task data models.
    :raises ValueError: If duplicate task names are found.
    """
    seen_names = set()
    for task in tasks_data:
        if task.name in seen_names:
            raise ValueError(f"Duplicate task name found: {task.name}")
        seen_names.add(task.name)


def populate_task_tracker(task_tracker: TaskTracker,
                          tasks_data: List[InputTaskModel]) -> None:
    """Populate a TaskTracker from validated input tasks data.

    :param task_tracker: The TaskTracker instance to populate.
    :param tasks_data: A list of validated task data models.
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
    """Load tasks from a JSON file and populate a TaskTracker.

    This function orchestrates the loading and validation of tasks from a
    JSON file and then populates a given TaskTracker instance with those
    tasks.

    :param task_tracker: The TaskTracker instance to populate.
    :param file_path: The path to the input JSON file.
    :param schema_path: The path to the JSON schema file for validation.
    """
    validated_data = load_and_validate_data(file_path, schema_path)
    validate_unique_task_names(validated_data.tasks)
    populate_task_tracker(task_tracker, validated_data.tasks)
