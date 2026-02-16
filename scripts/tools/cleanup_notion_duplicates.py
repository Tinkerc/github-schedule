#!/usr/bin/env python3
"""
Clean up duplicate sub-pages with the same title.
Keeps only the most recent one (based on creation time).
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

    notion = NotionAPI(auth=api_key)

    print(f"🔍 Scanning for duplicate sub-pages under: {page_id}\n")

    # List all children
    response = notion.blocks.children.list(block_id=page_id)
    children = response.get('results', [])

    # Group child pages by title
    title_to_pages = {}

    for child in children:
        if child.get('type') == 'child_page':
            child_id = child['id']

            try:
                page = notion.pages.retrieve(child_id)
                title_prop = page.get('properties', {}).get('title', {})

                if title_prop.get('type') == 'title' and title_prop.get('title'):
                    title = title_prop['title'][0]['text']['content']

                    # Get created time for sorting
                    created_time = page.get('created_time', '')

                    if title not in title_to_pages:
                        title_to_pages[title] = []

                    title_to_pages[title].append({
                        'id': child_id,
                        'created': created_time
                    })

            except Exception as e:
                print(f"⚠️  Error reading page {child_id}: {e}")

    # Find and clean up duplicates
    print(f"Found {len(title_to_pages)} unique page titles\n")

    duplicates_found = 0
    total_deleted = 0

    for title, pages in title_to_pages.items():
        if len(pages) > 1:
            duplicates_found += 1
            print(f"📄 {title}: {len(pages)} duplicates")

            # Sort by created time (most recent last)
            pages.sort(key=lambda x: x['created'])

            # Keep the most recent one, delete the rest
            for i, page_info in enumerate(pages[:-1]):
                page_id_to_delete = page_info['id']
                try:
                    notion.pages.update(page_id_to_delete, archived=True)
                    print(f"   ✗ Deleted: {page_id_to_delete}")
                    total_deleted += 1
                except Exception as e:
                    print(f"   ⚠️  Failed to delete {page_id_to_delete}: {e}")

            # Keep the most recent one
            kept_page = pages[-1]
            print(f"   ✓ Kept: {kept_page['id']} (most recent)\n")

    if duplicates_found == 0:
        print("✅ No duplicates found!")
    else:
        print("="*50)
        print(f"✅ Cleanup complete!")
        print(f"   Titles with duplicates: {duplicates_found}")
        print(f"   Total pages deleted: {total_deleted}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
