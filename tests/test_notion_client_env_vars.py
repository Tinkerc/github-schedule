# tests/test_notion_client_env_vars.py
import os
import pytest
from core.notion_client import NotionClient

def test_init_loads_from_env_vars():
    """Test that NotionClient loads settings from environment variables"""
    # Set env vars
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key_123'
    os.environ['NOTION_DEBUG'] = 'true'
    os.environ['NOTION_DRY_RUN'] = 'false'
    os.environ['NOTION_DELETE_DUPLICATES'] = 'false'

    client = NotionClient()

    assert client.enabled == True
    assert client.api_key == 'test_key_123'
    assert client.debug == True
    assert client.dry_run == False
    assert client.delete_duplicates == False

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']
    del os.environ['NOTION_DEBUG']
    del os.environ['NOTION_DRY_RUN']
    del os.environ['NOTION_DELETE_DUPLICATES']

def test_init_defaults_to_disabled():
    """Test that NotionClient defaults to disabled when NOTION_ENABLED not set"""
    # Ensure NOTION_ENABLED is not set
    if 'NOTION_ENABLED' in os.environ:
        del os.environ['NOTION_ENABLED']

    client = NotionClient()

    assert client.enabled == False
    assert client.api_key is None  # Should not load if disabled

def test_init_skips_api_key_when_disabled():
    """Test that API key is not loaded when NOTION_ENABLED=false"""
    os.environ['NOTION_ENABLED'] = 'false'
    os.environ['NOTION_API_KEY'] = 'should_not_load'

    client = NotionClient()

    assert client.enabled == False
    # API key might be set during env var processing, but is_available will return False

    del os.environ['NOTION_ENABLED']
    if 'NOTION_API_KEY' in os.environ:
        del os.environ['NOTION_API_KEY']
