"""
Example unit test to demonstrate testing structure
"""
import pytest


def test_example():
    """Example test function"""
    assert True


@pytest.mark.unit
def test_module_import():
    """Test that core modules can be imported"""
    from core.base import Task, Notifier
    from core.notion_client import NotionClient
    
    assert Task is not None
    assert Notifier is not None
    assert NotionClient is not None
