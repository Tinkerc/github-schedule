# Testing Standards and Conventions

## Directory Structure

```
project/
├── tests/                          # Automated pytest tests
│   ├── unit/                      # Unit tests for individual functions
│   ├── integration/               # Integration tests for workflows
│   ├── conftest.py                # Pytest configuration
│   └── README.md                  # Testing documentation
│
├── scripts/                        # Manual and utility scripts
│   ├── manual/                    # Manual verification scripts
│   ├── demo/                      # Feature demonstration scripts
│   └── README.md                  # Scripts documentation
│
└── main.py                         # Application entry point
```

## File Naming Conventions

### Automated Tests (tests/)
- **Pattern**: `test_<module>_<feature>.py`
- **Example**: `test_notion_client_database_id.py`
- **Run via**: `pytest tests/unit/test_notion_client.py`

### Manual Scripts (scripts/manual/)
- **Pattern**: `<feature>_<action>.py`
- **Example**: `verification.py`, `api_test.py`
- **Run via**: `python scripts/manual/verification.py`

### Demo Scripts (scripts/demo/)
- **Pattern**: `<feature>_demo.py` or descriptive name
- **Example**: `wecom_format.py`, `message_splitting.py`
- **Run via**: `python scripts/demo/wecom_format.py`

## Writing Tests

### Unit Tests

```python
# tests/unit/test_example.py
import pytest

@pytest.mark.unit
def test_specific_behavior():
    """Test specific behavior with assertions"""
    result = some_function()
    assert result == expected_value
```

### Integration Tests

```python
# tests/integration/test_workflow.py
import pytest

@pytest.mark.integration
def test_full_workflow():
    """Test complete workflow"""
    # Test multiple components working together
    assert workflow_complete()
```

### Manual Scripts

```python
# scripts/manual/verification.py
"""
Manual verification script for X feature
Run: python scripts/manual/verification.py
"""

def main():
    print("Verifying feature...")
    # Manual testing code here
    
if __name__ == "__main__":
    main()
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Only Unit Tests
```bash
pytest tests/unit/ -v
```

### Run Only Integration Tests
```bash
pytest tests/integration/ -v
```

### Run Specific Test File
```bash
pytest tests/unit/test_notion_client.py -v
```

### Run with Coverage
```bash
pytest --cov=core --cov=tasks --cov-report=html
```

### Run Manual Scripts
```bash
# Manual verification
python scripts/manual/verification.py

# Demo showcase
python scripts/demo/wecom_format.py
```

## When to Use Which

| Scenario | Location |
|----------|----------|
| Testing a single function | `tests/unit/` |
| Testing complete workflow | `tests/integration/` |
| Quick manual verification | `scripts/manual/` |
| Showcasing output format | `scripts/demo/` |
| Debugging/one-off script | `scripts/manual/` |

## Golden Rules

1. **Never** put `test_*.py` files in project root
2. **Always** use pytest for automated tests
3. **Manual scripts** should have clear main() functions
4. **Demo scripts** should showcase, not test
5. **Integration tests** should test real workflows
6. **Unit tests** should be fast and isolated

## Migration Guide

If you need to add a new test:

1. Is it automated and repeatable? → `tests/unit/` or `tests/integration/`
2. Is it manual verification? → `scripts/manual/`
3. Is it showcasing a feature? → `scripts/demo/`

## CI/CD Integration

The pytest tests in `tests/` should be run in CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: pytest
```

Manual scripts in `scripts/` are for development only.
