#!/usr/bin/env python3
"""
Debug script to inspect a Notion page/database structure.
Helps identify the correct property names to use.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from notion_client import Client as NotionAPI

load_dotenv()


def main():
    print("Notion Page Structure Debugger")
    print("=" * 50)

    api_key = os.environ.get('NOTION_API_KEY')
    page_id = os.environ.get('NOTION_PAGE_TECH_INSIGHTS') or os.environ.get('NOTION_PAGE_ID')

    if not api_key:
        print("❌ NOTION_API_KEY not set")
        return 1

    if not page_id:
        print("❌ No page ID set")
        return 1

    # Extract just the ID if it contains the full URL format
    # Handle both formats: "Name-32chars" or just "32chars"
    page_id = page_id.split('-')[-1] if '-' in page_id else page_id

    print(f"📄 Page ID: {page_id}")
    print(f"🔍 Fetching page info...\n")

    try:
        notion = NotionAPI(auth=api_key)

        # Try to get page info
        try:
            page = notion.pages.retrieve(page_id)
            print("✅ This is a PAGE (not a database)")
            print(f"   Parent: {page.get('parent', {})}")
            print(f"   Archived: {page.get('archived', False)}")
            print(f"\n📋 Available properties:")
            for prop_name, prop_data in page.get('properties', {}).items():
                prop_type = prop_data.get('type', 'unknown')
                print(f"   - {prop_name} (type: {prop_type})")

        except Exception as page_error:
            print(f"❌ Not a page: {page_error}")

            # Try to get database info
            try:
                db = notion.databases.retrieve(page_id)
                print("\n✅ This is a DATABASE")
                print(f"   Title: {db.get('title', [])}")
                print(f"\n📋 Database properties:")
                for prop_name, prop_data in db.get('properties', {}).items():
                    prop_type = prop_data.get('type', 'unknown')
                    print(f"   - {prop_name} (type: {prop_type})")

                print(f"\n💡 For database mode, use:")
                print(f"   NOTION_DB_TECH_INSIGHTS={page_id}")
                print(f"   NOTION_DB_TRENDING_AI={page_id}")

            except Exception as db_error:
                print(f"❌ Not a database either: {db_error}")

        # Try listing children to see what's already there
        try:
            print(f"\n🔍 Listing children of {page_id}...")
            children = notion.blocks.children.list(block_id=page_id)

            results = children.get('results', [])
            print(f"   Found {len(results)} children")

            if results:
                print(f"\n📄 First few children:")
                for child in results[:5]:
                    child_type = child.get('type', 'unknown')
                    print(f"   - {child_type}: {child.get('id', 'no-id')}")
                    if child_type == 'child_page':
                        print(f"     (child page)")

        except Exception as children_error:
            print(f"⚠️  Could not list children: {children_error}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
