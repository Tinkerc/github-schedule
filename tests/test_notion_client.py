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

@patch('core.notion_client.NotionAPI')
def test_create_sub_page(mock_notion_api):
    """Test creating a sub-page under a parent page"""
    from unittest.mock import Mock
    # Setup mock
    mock_client = Mock()
    mock_notion_api.return_value = mock_client
    mock_client.pages.create.return_value = {"id": "new-page-123"}

    os.environ['NOTION_API_KEY'] = 'test_key'
    client = NotionClient()
    client.dry_run = False

    result = client._create_sub_page(
        parent_page_id="parent-123",
        markdown_content="# Test Content\n\nThis is test content.",
        date="2026-02-16"
    )

    assert result is True
    mock_client.pages.create.assert_called_once()

    # Verify the call arguments
    call_args = mock_client.pages.create.call_args
    assert call_args[1]['parent']['page_id'] == "parent-123"
    assert call_args[1]['properties']['Name']['title'][0]['text']['content'] == "2026-02-16"

def test_create_sub_page_dry_run():
    """Test dry run mode for sub-page creation"""
    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_DRY_RUN'] = 'true'

    client = NotionClient()

    result = client._create_sub_page(
        parent_page_id="parent-123",
        markdown_content="# Test",
        date="2026-02-16"
    )

    assert result is True

    # Cleanup
    del os.environ['NOTION_DRY_RUN']
    del os.environ['NOTION_ENABLED']

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

@patch('core.notion_client.NotionAPI')
def test_delete_existing_sub_pages(mock_notion_api):
    """Test deleting existing sub-pages with matching date"""
    from unittest.mock import Mock
    # Setup mock
    mock_client = Mock()
    mock_notion_api.return_value = mock_client

    # Mock search response to find pages
    mock_client.pages.search.return_value = {
        'results': [
            {
                'id': 'page-1',
                'parent': {'page_id': 'parent-123'},
                'properties': {'Name': {'title': [{'text': {'content': '2026-02-16'}}]}}
            },
            {
                'id': 'page-2',
                'parent': {'page_id': 'parent-123'},
                'properties': {'Name': {'title': [{'text': {'content': '2026-02-16'}}]}}
            }
        ]
    }
    mock_client.pages.update.return_value = {}

    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_ENABLED'] = 'true'
    client = NotionClient()
    client.dry_run = False

    client._delete_existing_sub_pages(
        parent_page_id="parent-123",
        date="2026-02-16"
    )

    # Verify both pages were archived
    assert mock_client.pages.update.call_count == 2
    calls = mock_client.pages.update.call_args_list
    assert calls[0][1]['archived'] is True
    assert calls[1][1]['archived'] is True

    # Cleanup
    del os.environ['NOTION_ENABLED']

def test_delete_existing_sub_pages_dry_run():
    """Test dry run mode doesn't delete"""
    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_DRY_RUN'] = 'true'

    client = NotionClient()

    # Should not raise any errors
    client._delete_existing_sub_pages("parent-123", "2026-02-16")

    # Cleanup
    del os.environ['NOTION_DRY_RUN']
    del os.environ['NOTION_ENABLED']

@patch('core.notion_client.NotionAPI')
def test_sync_markdown_uses_sub_page_mode(mock_notion_api):
    """Test sync_markdown uses sub-page mode when parent_page_id configured"""
    from unittest.mock import Mock
    mock_client = Mock()
    mock_notion_api.return_value = mock_client
    mock_client.databases.retrieve.return_value = {}  # Not called in sub-page mode

    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_PAGE_TECH_INSIGHTS'] = 'parent-123'

    client = NotionClient()
    client.dry_run = False

    # Mock delete and create methods
    with patch.object(client, '_delete_existing_sub_pages') as mock_delete:
        with patch.object(client, '_create_sub_page', return_value=True) as mock_create:
            result = client.sync_markdown(
                task_id='tech_insights',
                markdown_content='# Test',
                date='2026-02-16'
            )

            assert result is True
            mock_delete.assert_called_once_with('parent-123', '2026-02-16')
            mock_create.assert_called_once_with('parent-123', '# Test', '2026-02-16')

    # Cleanup
    del os.environ['NOTION_PAGE_TECH_INSIGHTS']
    del os.environ['NOTION_ENABLED']

@patch('core.notion_client.NotionAPI')
def test_sync_markdown_falls_back_to_database(mock_notion_api):
    """Test sync_markdown falls back to database mode when no parent_page_id"""
    from unittest.mock import Mock
    mock_client = Mock()
    mock_notion_api.return_value = mock_client
    mock_client.databases.retrieve.return_value = {
        'id': 'db-123',
        'data_sources': []
    }

    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_DB_TECH_INSIGHTS'] = 'db-123'

    client = NotionClient()
    client.dry_run = False

    result = client.sync_markdown(
        task_id='tech_insights',
        markdown_content='# Test',
        date='2026-02-16'
    )

    assert result is True
    # Verify database API was called (not sub-page methods)
    mock_client.databases.retrieve.assert_called()

    # Cleanup
    del os.environ['NOTION_DB_TECH_INSIGHTS']
    del os.environ['NOTION_ENABLED']


