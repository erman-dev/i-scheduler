from graphlib import CycleError
import json
import pytest
from jsonschema import ValidationError as JsonSchemaValidationError
from pydantic import ValidationError as PydanticValidationError
from scheduler.loader import (
    load_and_validate_data,
    populate_task_tracker,
)
from scheduler.models import InputTaskModel
from scheduler.task_tracker import TaskTracker


def create_schema_file(tmp_path, schema):
    schema_file = tmp_path / "schema.json"
    with open(schema_file, "w") as f:
        json.dump(schema, f)
    return schema_file


def test_schema_validation_fails(tmp_path):
    """
    Test that a JsonSchemaValidationError is raised for data that does not
    conform to the schema.
    """
    schema = {
        "type": "object",
        "properties": {"tasks": {"type": "array"}},
        "required": ["tasks"],
    }
    schema_file = create_schema_file(tmp_path, schema)

    invalid_data = {"some_other_key": "value"}
    input_file = tmp_path / "invalid_input.json"
    with open(input_file, "w") as f:
        json.dump(invalid_data, f)

    with pytest.raises(JsonSchemaValidationError):
        load_and_validate_data(input_file, schema_file)


def test_unknown_dependency_fails():
    """
    Test that a KeyError is raised when a task has a dependency on an
    unknown task.
    """
    task_defs = [
        InputTaskModel(
            name="task1",
            type="exec",
            arguments="echo 'task1'",
            dependencies=["non_existent_task"],
        )
    ]

    task_tracker = TaskTracker()
    populate_task_tracker(task_tracker, task_defs)

    with pytest.raises(KeyError):
        task_tracker.prepare_topo_sorter()


def test_cycle_dependency_fails():
    """
    Test that a CycleError is raised when there is a circular dependency.
    """

    task_defs = [
        InputTaskModel(
            name="task1",
            type="exec",
            arguments="echo 'task1'",
            dependencies=["task2"],
        ),
        InputTaskModel(
            name="task2",
            type="exec",
            arguments="echo 'task2'",
            dependencies=["task1"],
        ),
    ]

    task_tracker = TaskTracker()
    populate_task_tracker(task_tracker, task_defs)

    with pytest.raises(CycleError):
        task_tracker.prepare_topo_sorter()


def test_pydantic_validation_fails(tmp_path):
    """
    Test that a PydanticValidationError is raised for data that is
    structurally valid but violates Pydantic model rules.
    """
    schema = {"type": "object", "properties": {"tasks": {"type": "array"}}}
    schema_file = create_schema_file(tmp_path, schema)
    # This data has an invalid 'type' for the task
    data = {
        "tasks": [
            {
                "name": "task1",
                "type": "invalid_type",
                "arguments": "echo 'task1'",
            }
        ]
    }
    input_file = tmp_path / "pydantic_invalid.json"
    with open(input_file, "w") as f:
        json.dump(data, f)

    with pytest.raises(PydanticValidationError):
        load_and_validate_data(input_file, schema_file)


def test_populate_task_tracker():
    """
    Test that the task tracker is populated correctly from a valid InputModel.
    """
    task_defs = [
        InputTaskModel(name="task1", type="exec", arguments="echo 'task1'"),
        InputTaskModel(
            name="task2",
            type="exec",
            arguments="echo 'task2'",
            dependencies=["task1"],
        ),
    ]

    task_tracker = TaskTracker()
    populate_task_tracker(task_tracker, task_defs)

    assert "task1" in task_tracker.tasks
    assert "task2" in task_tracker.tasks
    assert task_tracker.tasks["task1"].dependencies == ()
    assert task_tracker.tasks["task2"].dependencies == ("task1",)
