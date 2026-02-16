# tests/test_notion_client_is_available.py
import os
import pytest
from core.notion_client import NotionClient

def test_is_available_returns_false_when_disabled():
    """Test that is_available returns False when NOTION_ENABLED=false"""
    os.environ['NOTION_ENABLED'] = 'false'

    client = NotionClient()
    result = client.is_available()

    assert result == False

    del os.environ['NOTION_ENABLED']

def test_is_available_returns_false_when_no_api_key():
    """Test that is_available returns False when enabled but no API key"""
    os.environ['NOTION_ENABLED'] = 'true'
    if 'NOTION_API_KEY' in os.environ:
        del os.environ['NOTION_API_KEY']

    client = NotionClient()
    result = client.is_available()

    assert result == False

    del os.environ['NOTION_ENABLED']

def test_is_available_returns_true_when_configured():
    """Test that is_available returns True when properly configured"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key_123'

    client = NotionClient()
    result = client.is_available()

    assert result == True

    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']
