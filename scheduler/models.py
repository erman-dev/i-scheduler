from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Tuple, Literal, Optional


class TaskStatus(Enum):
    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3
    SKIPPED = 4


class Task(BaseModel):
    type: Literal["eval", "exec"]
    arguments: str
    dependencies: Tuple[str, ...] = Field(default_factory=tuple)
    status: TaskStatus = TaskStatus.PENDING
    model_config = ConfigDict(arbitrary_types_allowed=True)


class InputTaskModel(BaseModel):
    name: str
    type: Literal["eval", "exec"]
    arguments: str
    dependencies: Tuple[str, ...] = Field(default_factory=tuple)


class InputModel(BaseModel):
    tasks: List[InputTaskModel]


class ExecutionResult(BaseModel):
    stdout: str = ""
    stderr: str = ""
    return_code: int | None = None
    exception: Optional[Exception] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)
