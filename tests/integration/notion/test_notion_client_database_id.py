# tests/test_notion_client_database_id.py
import os
import pytest
from core.notion_client import NotionClient

def test_get_database_id_from_env_var():
    """Test that database ID is loaded from environment variable"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()

    # Set database ID for tech_insights
    os.environ['NOTION_DB_TECH_INSIGHTS'] = 'abc123def456'

    db_id = client._get_database_id('tech_insights')

    assert db_id == 'abc123def456'

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']
    del os.environ['NOTION_DB_TECH_INSIGHTS']

def test_get_database_id_returns_none_when_not_set():
    """Test that _get_database_id returns None when env var not set"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()

    # Ensure database ID is not set
    if 'NOTION_DB_TECH_INSIGHTS' in os.environ:
        del os.environ['NOTION_DB_TECH_INSIGHTS']

    db_id = client._get_database_id('tech_insights')

    assert db_id is None

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']

def test_get_database_id_task_id_case_conversion():
    """Test that task_id is correctly converted to env var name"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()

    # Set with underscores
    os.environ['NOTION_DB_TRENDING_AI'] = 'xyz789'

    # Query with underscores
    db_id = client._get_database_id('trending_ai')

    assert db_id == 'xyz789'

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']
    del os.environ['NOTION_DB_TRENDING_AI']
