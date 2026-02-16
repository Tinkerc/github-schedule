#!/usr/bin/env python3
"""
Simple Notion sub-page creation test.
Quick way to verify your Notion integration is working.
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


def main():
    print("Simple Notion Sub-Page Test")
    print("=" * 40)

    # Check environment variables
    api_key = os.environ.get('NOTION_API_KEY')
    page_id = os.environ.get('NOTION_PAGE_TECH_INSIGHTS') or os.environ.get('NOTION_PAGE_ID')

    if not api_key:
        print("❌ NOTION_API_KEY not set in .env")
        print("\nGet your API key from: https://www.notion.so/my-integrations")
        return 1

    if not page_id:
        print("❌ No parent page ID found")
        print("\nSet one of these in .env:")
        print("  NOTION_PAGE_TECH_INSIGHTS=your-page-id")
        print("  NOTION_PAGE_ID=your-page-id")
        return 1

    print(f"✓ API Key configured")
    print(f"✓ Parent Page ID: {page_id}")

    # Create client
    os.environ['NOTION_ENABLED'] = 'true'
    client = NotionClient()

    # Test content
    today = "2026-02-16"
    content = """# Simple Test Page

Hello from the simple Notion test!

This page was created to verify your Notion integration is working.

## Test Checklist
- [x] Can connect to Notion API
- [x] Can create sub-pages
- [x] Can write markdown content

**If you see this in Notion, everything is working!** ✅
"""

    print(f"\n📝 Creating test page: {today}")

    # Create the page
    if page_id == os.environ.get('NOTION_PAGE_ID'):
        # Use generic test task_id
        os.environ['NOTION_PAGE_TEST'] = page_id
        result = client.sync_markdown('test', content, today)
    else:
        result = client.sync_markdown('tech_insights', content, today)

    if result:
        print("✅ Test page created successfully!")
        print(f"\nCheck your Notion page for: '{today}'")
        return 0
    else:
        print("❌ Failed to create test page")
        return 1


if __name__ == '__main__':
    sys.exit(main())
