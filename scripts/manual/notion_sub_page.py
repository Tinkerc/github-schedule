#!/usr/bin/env python3
"""
Manual test script for Notion sub-page creation.

This script tests creating sub-pages under a parent page.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
from core.notion_client import NotionClient

load_dotenv()

def get_parent_page_id():
    """Get parent page ID from various environment variable sources"""
    # Try different environment variable names in order of priority
    page_id_sources = [
        ('NOTION_PAGE_ID', 'Generic test page'),
        ('NOTION_PAGE_TECH_INSIGHTS', 'Tech Insights parent page'),
        ('NOTION_PAGE_TRENDING_AI', 'Trending AI parent page'),
        ('NOTION_PAGE_AI_NEWS', 'AI News parent page'),
    ]

    for env_var, description in page_id_sources:
        page_id = os.environ.get(env_var)
        if page_id:
            return page_id, env_var, description

    return None, None, None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Test Notion sub-page creation')
    parser.add_argument('--dry-run-only', action='store_true',
                        help='Only run dry-run test (no Notion API calls)')
    parser.add_argument('--real', action='store_true',
                        help='Skip confirmation prompt and run real test immediately')
    args = parser.parse_args()

    print("="*60)
    print("Notion Sub-Page Creation Test")
    print("="*60)

    # Dry run only mode
    if args.dry_run_only:
        print("\n🔵 Dry-run mode: No Notion API calls will be made")
        print("\n" + "="*60)
        print("Step 1: Dry Run Test")
        print("="*60)

        client = NotionClient()
        client.dry_run = True

        test_date = "2026-02-16"
        test_content = """# Test Sub-Page

This is a test page in dry-run mode.

No API calls are made to Notion.
"""

        result = client.sync_markdown('test', test_content, test_date)
        if result:
            print("✓ Dry run successful")
            print("\n✅ Test passed! The script is ready to use.")
            print("\nTo test with real Notion API:")
            print("  1. Create a test page in Notion")
            print("  2. Add NOTION_PAGE_ID to .env file")
            print("  3. Run: python scripts/test_sub_page_creation.py")
            return 0
        else:
            print("✗ Dry run failed")
            return 1

    # Check if any parent page ID is set
    parent_page_id, env_var, description = get_parent_page_id()
    if not parent_page_id:
        print("\n❌ Error: No parent page ID environment variable found")
        print("\nTo run this test, set one of these environment variables:")
        print("  - NOTION_PAGE_ID (for generic testing)")
        print("  - NOTION_PAGE_TECH_INSIGHTS")
        print("  - NOTION_PAGE_TRENDING_AI")
        print("  - NOTION_PAGE_AI_NEWS")
        print("\nExample:")
        print("  export NOTION_PAGE_ID=your-page-id-here")
        print("  # Or add to .env file:")
        print("  NOTION_PAGE_ID=your-page-id-here")
        print("\nTo get a page ID:")
        print("  1. Create a test page in Notion")
        print("  2. Open the page")
        print("  3. Copy the page ID from the URL (32 characters)")
        print("\nQuick test (dry-run only):")
        print("  python scripts/test_sub_page_creation.py --dry-run-only")
        return 1

    print(f"\n📄 Using: {description}")
    print(f"📄 Environment Variable: {env_var}")
    print(f"📄 Parent Page ID: {parent_page_id}")

    # Ensure Notion is enabled for testing
    if os.environ.get('NOTION_ENABLED', '').lower() != 'true':
        print("\n⚠️  Enabling Notion for this test (NOTION_ENABLED=true)")
        os.environ['NOTION_ENABLED'] = 'true'

    # Create client
    client = NotionClient()

    if not client.is_available():
        print("\n❌ Notion client not available")
        print("Check NOTION_API_KEY environment variable")
        return 1

    # Test content
    test_date = "2026-02-16"
    test_content = """# Test Sub-Page

This is a test page created by the sub-page creation test script.

## Features

- Created as a child of parent page
- Title is the date
- Contains markdown content
- Supports **bold** and *italic*

## Code Block

```python
def hello():
    print("Hello, Notion!")
```

## List

1. Item 1
2. Item 2
3. Item 3

Created for testing purposes.
"""

    print(f"\n📅 Test Date: {test_date}")
    print(f"📝 Content Length: {len(test_content)} characters")

    # Determine task_id based on which env var was used
    task_id_map = {
        'NOTION_PAGE_TECH_INSIGHTS': 'tech_insights',
        'NOTION_PAGE_TRENDING_AI': 'trending_ai',
        'NOTION_PAGE_AI_NEWS': 'ai_news',
        'NOTION_PAGE_ID': 'test',  # Generic test - will use NOTION_PAGE_TEST
    }
    task_id = task_id_map.get(env_var, 'test')

    # For NOTION_PAGE_ID case, set up NOTION_PAGE_TEST environment variable
    if env_var == 'NOTION_PAGE_ID':
        os.environ['NOTION_PAGE_TEST'] = parent_page_id
        print(f"\n🔧 Set NOTION_PAGE_TEST={parent_page_id} for testing")

    # Dry run first
    print("\n" + "="*60)
    print("Step 1: Dry Run Test")
    print("="*60)
    client.dry_run = True

    result = client.sync_markdown(task_id, test_content, test_date)
    if result:
        print("✓ Dry run successful")
    else:
        print("✗ Dry run failed")
        return 1

    # Ask for confirmation (skip if --real flag is used)
    print("\n" + "="*60)
    print("Step 2: Real Test")
    print("="*60)

    if args.real:
        print("\n🚀 Running real test (--real flag: skipping confirmation)")
    else:
        response = input(f"\nCreate a real test page under {parent_page_id}? (yes/no): ")

        if response.lower() != 'yes':
            print("\n❌ Test cancelled")
            return 0

    # Real run
    client.dry_run = False

    print("\nCreating test page...")
    result = client.sync_markdown(task_id, test_content, test_date)

    if result:
        print("\n✅ Test page created successfully!")
        print(f"\nCheck your Notion parent page for: '{test_date}'")
        print("\nThe test page should contain the test content above.")
        print("\nTo clean up, delete the test page manually in Notion.")

        # Test creating again (should delete old and create new)
        print("\n" + "="*60)
        print("Step 3: Test Duplicate Deletion")
        print("="*60)

        should_run_duplicate = False
        if args.real:
            print("\n🚀 Running duplicate deletion test (--real flag: skipping confirmation)")
            should_run_duplicate = True
        else:
            response = input("\nRun again to test duplicate deletion? (yes/no): ")
            should_run_duplicate = (response.lower() == 'yes')

        if should_run_duplicate:
            print("\nCreating again (should delete old page first)...")
            result = client.sync_markdown(task_id, test_content, test_date)

            if result:
                print("✅ Duplicate deletion test successful!")
                print("You should have only ONE test page with today's date.")
            else:
                print("✗ Duplicate deletion test failed")
                return 1
    else:
        print("\n❌ Failed to create test page")
        return 1

    print("\n" + "="*60)
    print("All tests passed!")
    print("="*60)

    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
