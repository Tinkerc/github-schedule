# tests/test_notion_client_current_behavior.py
"""Document current NotionClient behavior before refactoring"""
import os
import pytest
from core.notion_client import NotionClient

def test_current_init_with_no_config():
    """Test that NotionClient initializes even without config file"""
    # Ensure no env vars set
    for key in list(os.environ.keys()):
        if 'NOTION' in key:
            del os.environ[key]

    client = NotionClient()
    # Current behavior: Should have default config
    assert hasattr(client, 'config')
    assert client.config.get('settings', {}).get('enabled') == True

def test_current_is_available_checks_config_file():
    """Test that is_available currently checks config file"""
    # This test documents current behavior
    client = NotionClient()
    # Current: Returns True even without API key if config.enabled=True
    result = client.is_available()
    # Document what happens currently
    print(f"Current is_available result: {result}")
