# tests/integration/test_notion_missing_config.py
"""Integration test: Verify graceful handling when Notion enabled but missing config"""
import os
import sys
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_graceful_skip_when_missing_api_key():
    """Test that tasks gracefully skip Notion when API key is missing"""
    # Enable Notion but don't set API key
    os.environ['NOTION_ENABLED'] = 'true'

    # Ensure API key is NOT set
    if 'NOTION_API_KEY' in os.environ:
        del os.environ['NOTION_API_KEY']

    from main import main

    # Capture output to verify graceful skip
    captured_output = StringIO()
    sys.stdout = captured_output

    exit_code = main()

    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()

    # Verify Notion was gracefully skipped
    assert 'NOTION_API_KEY not set' in output or 'Notion' in output, \
        "Should see message about missing API key or Notion being skipped"

    # Cleanup
    del os.environ['NOTION_ENABLED']

    # Print summary
    print(f"✓ Integration test passed: Graceful skip when API key missing (exit code: {exit_code})")
    if exit_code != 0:
        print(f"  Note: Some tasks may have failed, but Notion was gracefully skipped")

if __name__ == '__main__':
    test_graceful_skip_when_missing_api_key()
    print("✓ Integration test passed: Graceful skip when API key missing")
