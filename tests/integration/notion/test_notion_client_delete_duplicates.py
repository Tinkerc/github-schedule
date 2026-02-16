# tests/test_notion_client_delete_duplicates.py
import os
import pytest
from core.notion_client import NotionClient

def test_delete_duplicates_defaults_to_true():
    """Test that delete_duplicates defaults to True"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'

    # Don't set NOTION_DELETE_DUPLICATES
    if 'NOTION_DELETE_DUPLICATES' in os.environ:
        del os.environ['NOTION_DELETE_DUPLICATES']

    client = NotionClient()

    assert client.delete_duplicates == True

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']

def test_delete_duplicates_can_be_disabled():
    """Test that delete_duplicates can be set to False"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_DELETE_DUPLICATES'] = 'false'

    client = NotionClient()

    assert client.delete_duplicates == False

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']
    del os.environ['NOTION_DELETE_DUPLICATES']
