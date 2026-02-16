#!/usr/bin/env python3
"""
List all child pages under a parent page.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from notion_client import Client as NotionAPI

load_dotenv()


def main():
    page_id = os.environ.get('NOTION_PAGE_TECH_INSIGHTS') or os.environ.get('NOTION_PAGE_ID')

    if not page_id:
        print("❌ No page ID set")
        return 1

    # Extract just the ID
    page_id = page_id.split('-')[-1] if '-' in page_id else page_id

    api_key = os.environ.get('NOTION_API_KEY')
    if not api_key:
        print("❌ NOTION_API_KEY not set")
        return 1

    print(f"🔍 Listing children of page: {page_id}\n")

    notion = NotionAPI(auth=api_key)

    # List all children
    children = notion.blocks.children.list(block_id=page_id)
    results = children.get('results', [])

    print(f"Found {len(results)} children:\n")

    for i, child in enumerate(results, 1):
        child_type = child.get('type', 'unknown')
        child_id = child.get('id', 'no-id')

        if child_type == 'child_page':
            # Get the actual page to read its title
            try:
                page = notion.pages.retrieve(child_id)
                title_prop = page.get('properties', {}).get('title', {})
                if title_prop.get('type') == 'title' and title_prop.get('title'):
                    title = title_prop['title'][0]['text']['content']
                else:
                    title = "(no title)"
            except:
                title = "(error reading title)"

            print(f"{i}. 📄 Child Page")
            print(f"   ID: {child_id}")
            print(f"   Title: {title}")
        else:
            print(f"{i}. {child_type}")
            print(f"   ID: {child_id}")

        print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
