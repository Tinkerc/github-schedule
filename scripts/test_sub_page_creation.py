#!/usr/bin/env python3
"""
Manual test script for Notion sub-page creation.

This script tests creating sub-pages under a parent page.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from core.notion_client import NotionClient

load_dotenv()

def main():
    print("="*60)
    print("Notion Sub-Page Creation Test")
    print("="*60)

    # Check if NOTION_PAGE_ID is set
    parent_page_id = os.environ.get('NOTION_PAGE_ID')
    if not parent_page_id:
        print("\n❌ Error: NOTION_PAGE_ID environment variable not set")
        print("\nTo run this test:")
        print("1. Create a test page in Notion")
        print("2. Get the page ID from the URL")
        print("3. Run: export NOTION_PAGE_ID=your-page-id-here")
        print("4. Run this script again")
        return 1

    print(f"\n📄 Parent Page ID: {parent_page_id}")

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

    # Dry run first
    print("\n" + "="*60)
    print("Step 1: Dry Run Test")
    print("="*60)
    client.dry_run = True

    # Set environment variable for test task
    os.environ['NOTION_PAGE_TEST'] = parent_page_id

    result = client.sync_markdown('test', test_content, test_date)
    if result:
        print("✓ Dry run successful")
    else:
        print("✗ Dry run failed")
        return 1

    # Ask for confirmation
    print("\n" + "="*60)
    print("Step 2: Real Test")
    print("="*60)
    response = input(f"\nCreate a real test page under {parent_page_id}? (yes/no): ")

    if response.lower() != 'yes':
        print("\n❌ Test cancelled")
        return 0

    # Real run
    client.dry_run = False

    print("\nCreating test page...")
    result = client.sync_markdown('test', test_content, test_date)

    if result:
        print("\n✅ Test page created successfully!")
        print(f"\nCheck your Notion parent page for: '{test_date}'")
        print("\nThe test page should contain the test content above.")
        print("\nTo clean up, delete the test page manually in Notion.")

        # Test creating again (should delete old and create new)
        print("\n" + "="*60)
        print("Step 3: Test Duplicate Deletion")
        print("="*60)
        response = input("\nRun again to test duplicate deletion? (yes/no): ")

        if response.lower() == 'yes':
            print("\nCreating again (should delete old page first)...")
            result = client.sync_markdown('test', test_content, test_date)

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
