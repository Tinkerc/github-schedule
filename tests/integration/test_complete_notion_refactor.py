# tests/integration/test_complete_notion_refactor.py
"""Final integration test to verify Notion refactor is complete"""
import os
import sys
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_notion_disabled():
    """Test system works with Notion disabled"""
    os.environ['NOTION_ENABLED'] = 'false'
    from main import main
    result = main()
    del os.environ['NOTION_ENABLED']
    print("✓ Notion disabled: System runs successfully")
    return result

def test_notion_enabled_dry_run():
    """Test system works with Notion enabled in dry-run mode"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_DB_TECH_INSIGHTS'] = 'test_db_id'
    os.environ['NOTION_DRY_RUN'] = 'true'

    # Capture output to verify dry-run message
    captured_output = StringIO()
    sys.stdout = captured_output

    from main import main
    result = main()

    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()

    # Verify dry-run message appeared
    assert 'DRY RUN' in output, "Should see dry-run message"

    # Cleanup
    for key in ['NOTION_ENABLED', 'NOTION_API_KEY', 'NOTION_DB_TECH_INSIGHTS', 'NOTION_DRY_RUN']:
        if key in os.environ:
            del os.environ[key]

    print("✓ Notion enabled dry-run: System works correctly")
    return result

def test_no_config_file_references():
    """Verify no config file references remain in code"""
    from pathlib import Path
    core_file = Path(__file__).parent.parent.parent / 'core' / 'notion_client.py'
    content = core_file.read_text()

    # Should not reference self.config
    assert 'self.config' not in content, "No self.config references should remain"
    print("✓ Code verification: No config file references in NotionClient")

def test_env_var_attributes():
    """Verify new env var attributes exist"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'

    from core.notion_client import NotionClient
    client = NotionClient()

    # Verify all new attributes exist
    assert hasattr(client, 'enabled'), "Should have 'enabled' attribute"
    assert hasattr(client, 'delete_duplicates'), "Should have 'delete_duplicates' attribute"
    assert hasattr(client, 'api_key'), "Should have 'api_key' attribute"
    assert hasattr(client, 'debug'), "Should have 'debug' attribute"
    assert hasattr(client, 'dry_run'), "Should have 'dry_run' attribute"

    # Should NOT have config attribute
    assert not hasattr(client, 'config'), "Should not have 'config' attribute"

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']

    print("✓ Attribute verification: All new env var attributes present, config removed")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("FINAL INTEGRATION TEST - Notion Refactor Complete")
    print("="*60 + "\n")

    print("Running comprehensive tests...\n")

    # Test 1: Notion disabled
    result1 = test_notion_disabled()

    # Test 2: Notion enabled dry-run
    result2 = test_notion_enabled_dry_run()

    # Test 3: No config file references
    test_no_config_file_references()

    # Test 4: Env var attributes
    test_env_var_attributes()

    print("\n" + "="*60)
    print("✓ ALL INTEGRATION TESTS PASSED")
    print("="*60)
    print("\nSummary:")
    print("  • Notion disabled mode: Working")
    print("  • Notion enabled dry-run: Working")
    print("  • Code quality: No config references")
    print("  • Architecture: Env var attributes correct")
    print("\n✓ Notion refactor is complete and verified!")
    print("="*60 + "\n")
