import os
import pytest
from core.notion_client import NotionClient

def test_notion_client_init_without_api_key():
    """Test that NotionClient initializes even without API key"""
    # Ensure no API key is set
    if 'NOTION_API_KEY' in os.environ:
        del os.environ['NOTION_API_KEY']

    client = NotionClient()
    assert client is not None
    assert client.is_available() == False

def test_notion_client_init_with_api_key():
    """Test that NotionClient detects API key from environment"""
    os.environ['NOTION_API_KEY'] = 'test_key_123'
    client = NotionClient()
    assert client is not None
    # Note: Actual availability check requires valid key format

def test_get_database_id_from_env_var():
    """Test that environment variables override config file"""
    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_DB_TECH_INSIGHTS'] = 'env_db_id_123'

    client = NotionClient()
    db_id = client._get_database_id('tech_insights')
    assert db_id == 'env_db_id_123'

    # Cleanup
    del os.environ['NOTION_DB_TECH_INSIGHTS']

def test_get_database_id_from_config():
    """Test that config file is used when no env var is set"""
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()
    # Use the default config which has empty strings
    db_id = client._get_database_id('tech_insights')
    # Should return None or empty string from config
    assert db_id is None or db_id == ''

def test_get_database_id_not_found():
    """Test that None is returned for unknown task_id"""
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()
    db_id = client._get_database_id('unknown_task')
    assert db_id is None

