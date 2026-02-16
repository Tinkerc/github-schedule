# tests/test_notion_client_obsolete_config_warning.py
import os
import tempfile
import pytest
from pathlib import Path
from core.notion_client import NotionClient
from io import StringIO
import sys

def test_warns_about_obsolete_config_file():
    """Test that NotionClient warns when config/notion_config.json exists"""
    # Create a temporary config file
    original_path = Path(__file__).parent.parent / 'config' / 'notion_config.json'
    temp_config = Path(__file__).parent.parent / 'config' / 'notion_config.json.temp'

    # Backup existing config if present
    had_backup = False
    if original_path.exists():
        original_path.rename(temp_config)
        had_backup = True

    try:
        # Create test config file
        original_path.parent.mkdir(exist_ok=True)
        original_path.write_text('{"test": "data"}')

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        client = NotionClient()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Should contain warning
        assert 'WARNING: config/notion_config.json is no longer used' in output
        assert 'Please use environment variables instead' in output

    finally:
        # Cleanup
        if original_path.exists():
            original_path.unlink()
        if had_backup and temp_config.exists():
            temp_config.rename(original_path)
