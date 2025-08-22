import pytest
from unittest.mock import patch
from scheduler import runner


@pytest.mark.asyncio
async def test_missing_input_file(caplog):
    """
    Test that the runner exits gracefully if the input file is not found.
    """
    with patch("sys.argv",
               ["runner.py",
                "--input",
                "non_existent_file.json"]):
        await runner.main()
        assert "Failed to load tasks" in caplog.text
        assert "No such file or directory" in caplog.text


@pytest.mark.asyncio
async def test_missing_schema_file(tmp_path, caplog):
    """
    Test that the runner exits gracefully if the schema file is not found.
    """
    input_file = tmp_path / "input.json"
    input_file.write_text('{"tasks": []}')
    with patch("sys.argv",
               ["runner.py",
                "--input",
                str(input_file),
                "--schema",
                "non_existent_schema.json"]):
        await runner.main()
        assert "Failed to load tasks" in caplog.text
        assert "No such file or directory" in caplog.text
