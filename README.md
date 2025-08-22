# Inmanta Task Scheduler

This program executes a set of tasks with a maximal level of concurrency while respecting the dependencies between the tasks.

Author: Roman Krček

## Setup

1.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running

To run the scheduler, provide an input JSON file and an optional schema for validation:

```bash
python3 -m scheduler.runner --input <path_to_input.json> --schema <path_to_schema.json>
```

For example:

```bash
python3 -m scheduler.runner --input assignment/input1.json --schema assignment/schema.json
```

## Testing

To run the test suite, use `tox`:

```bash
pip install tox
tox -e pytest
tox -e linters
```

This will run all tests, lint code and provide test coverage.

## Task Execution Strategy

The scheduler supports two types of tasks: `exec` and `eval`.

### `exec` Tasks

-   **Execution:** `exec` tasks are executed as shell commands in a separate subprocess using `asyncio.create_subprocess_shell`.
-   **Concurrency:** This allows `exec` tasks to run concurrently without blocking the main event loop.
-   **Output:** `stdout` and `stderr` are captured from the subprocess.
-   **Result:** The task's success or failure is determined by the return code of the shell command.

### `eval` Tasks

-   **Execution:** `eval` tasks execute a snippet of Python code. To avoid blocking the asyncio event loop, the code is run in a separate thread using `loop.run_in_executor`.
-   **Concurrency:** This allows `eval` tasks to run concurrently with other tasks.
-   **Output:** `stdout` and `stderr` are captured by redirecting the standard streams within the thread.
-   **Result:** An `eval` task is considered successful if no unhandled exceptions are raised during its execution. Any exception is caught and reported as a failure.


## Task Tracking and Dependency Management

The `TaskTracker` class is the core of the dependency management system.

-   **Dependency Graph:** It uses Python's built-in `graphlib.TopologicalSorter` to manage the task dependency graph and determine which tasks are ready to run based on the status of their dependencies.
-   **Task State:** The state of each task (e.g., `PENDING`, `RUNNING`, `OK`, `FAILED`, `SKIPPED`) is tracked in a separate dictionary within the `TaskTracker`.
-   **Failure and Skipping:**
    -   If a task fails during execution, it is marked as `FAILED`.
    -   Any task that depends on a `FAILED` or `SKIPPED` task will automatically be marked as `SKIPPED` and will not be executed. This ensures that the scheduler doesn't waste resources on tasks that are guaranteed to fail or are no longer relevant.


## Note for the reviewers of the code

This code was test on Ubuntu 24.04 with python3.12.3 which satisfies the python3.6+ requirement.
As I understood it, the text said to develop it with python3.6+, but not make it backwards compatible
down to python3.6. Graphlib, one of the core dependencies this code is written on top of is a library
that is only supports python3.9+ as pythons 3.6-3.8 are end-of-life for quite some time.
