# Input validation
x validate required --schema and --input
x schema validation, fail if output does not conform to schema
x detect reference to unknown task
x detect circular dependencies

# Run validation
x exec/eval that fails must return proper return code
x ensure proper stdout is returned
x ensure proper stderr is returned

# Task tracker
- dependencies of skipped task are skipped
- dependencies of failed task are skipped
- make sure failed tasks are marked as failed
- ensure proper execution order