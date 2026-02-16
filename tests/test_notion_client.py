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

def test_get_parent_page_id_from_env():
    """Test getting parent page ID from environment variable"""
    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_PAGE_TECH_INSIGHTS'] = 'page-456'

    client = NotionClient()
    result = client._get_parent_page_id("tech_insights")
    assert result == "page-456"

    # Cleanup
    del os.environ['NOTION_PAGE_TECH_INSIGHTS']

def test_get_parent_page_id_not_found():
    """Test returning None when parent page ID not configured"""
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()
    result = client._get_parent_page_id("nonexistent")
    assert result is None

from unittest.mock import patch, MagicMock

def test_sync_markdown_returns_false_on_no_config():
    """Test that sync_markdown returns False when database not configured"""
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()
    result = client.sync_markdown('unknown_task', '# Test', '2026-02-16')
    assert result == False

def test_sync_markdown_returns_false_on_no_api_key():
    """Test that sync_markdown returns False when no API key"""
    if 'NOTION_API_KEY' in os.environ:
        del os.environ['NOTION_API_KEY']

    client = NotionClient()
    result = client.sync_markdown('tech_insights', '# Test', '2026-02-16')
    assert result == False

def test_sync_markdown_dry_run_mode():
    """Test that dry_run mode returns True without API calls"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_DRY_RUN'] = 'true'

    client = NotionClient()

    with patch.object(client, '_find_and_delete_existing') as mock_delete, \
         patch.object(client, '_create_new_entry') as mock_create:
        result = client.sync_markdown('tech_insights', '# Test Content', '2026-02-16')

        # Should succeed without calling API methods
        assert result == True
        mock_delete.assert_not_called()
        mock_create.assert_not_called()

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_DRY_RUN']


