"""
Manual test script for Notion integration.
Run this to test Notion sync functionality.
"""
import os
import sys
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.notion_client import NotionClient


def test_dry_run(task_id: str):
    """Test dry-run mode (no API calls)"""
    print("="*60)
    print(f"Testing dry-run mode for {task_id}")
    print("="*60)

    os.environ['NOTION_DRY_RUN'] = 'true'
    client = NotionClient()

    test_markdown = f"""# Test Content for {task_id}

This is a test markdown content generated at {datetime.now()}.

## Section 1
Test content here.

## Section 2
More test content.
"""

    success = client.sync_markdown(
        task_id=task_id,
        markdown_content=test_markdown,
        date=datetime.now().strftime('%Y-%m-%d')
    )

    print(f"\nResult: {'✓ PASS' if success else '✗ FAIL'}")
    del os.environ['NOTION_DRY_RUN']


def test_with_real_api(task_id: str, date: str):
    """Test with real Notion API calls"""
    print("="*60)
    print(f"Testing real API sync for {task_id}")
    print("="*60)

    if not os.environ.get('NOTION_API_KEY'):
        print("✗ NOTION_API_KEY not set")
        return

    client = NotionClient()

    if not client.is_available():
        print("✗ Notion client not available")
        print("  Check NOTION_API_KEY and database configuration")
        return

    test_markdown = f"""# Manual Test for {task_id}

Generated at: {datetime.now()}

This is a manual test of the Notion sync functionality.

## Test Results
- Configuration: ✓
- API Key: ✓
- Database ID: ✓

If you see this in Notion, the sync is working!
"""

    success = client.sync_markdown(
        task_id=task_id,
        markdown_content=test_markdown,
        date=date
    )

    print(f"\nResult: {'✓ PASS' if success else '✗ FAIL'}")


def main():
    parser = argparse.ArgumentParser(description='Test Notion integration')
    parser.add_argument('--task', required=True, help='Task ID (tech_insights, trending_ai)')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'), help='Date (YYYY-MM-DD)')
    parser.add_argument('--dry-run', action='store_true', help='Test without API calls')
    parser.add_argument('--real', action='store_true', help='Test with real API calls')

    args = parser.parse_args()

    if args.dry_run:
        test_dry_run(args.task)
    elif args.real:
        test_with_real_api(args.task, args.date)
    else:
        print("Please specify --dry-run or --real")
        parser.print_help()


if __name__ == '__main__':
    main()
