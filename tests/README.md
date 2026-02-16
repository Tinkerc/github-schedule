# Tests Directory

This directory contains all automated tests for the project.

## Structure

- `unit/` - Unit tests for individual modules and functions
- `integration/` - Integration tests for end-to-end workflows

## Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/unit/test_example.py
```

Run with verbose output:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=core --cov=tasks
```
