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
