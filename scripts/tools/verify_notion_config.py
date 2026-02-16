#!/usr/bin/env python3
"""
Notion Configuration Verification Script

This script checks if your Notion integration is properly configured.
Run this before testing the actual Notion sync.
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
from notion_client import Client as NotionAPI


def check_database_id_format(db_id: str) -> bool:
    """Check if database ID is in correct format (32 chars, alphanumeric)"""
    if not db_id:
        return False
    # Remove any dashes or spaces
    clean_id = db_id.replace('-', '').replace(' ', '')
    return len(clean_id) == 32 and clean_id.isalnum()


def verify_parent_pages(client, config):
    """Verify parent pages exist and are accessible"""
    print("\n=== Verifying Parent Pages ===")

    parent_pages = {}
    # Get all NOTION_PAGE_* environment variables
    for key, value in os.environ.items():
        if key.startswith('NOTION_PAGE_') and value:
            task_id = key.replace('NOTION_PAGE_', '').lower()
            parent_pages[task_id] = value

    if not parent_pages:
        print("No parent pages configured (NOTION_PAGE_* variables)")
        return

    notion = NotionAPI(auth=client.api_key)

    for task_id, page_id in parent_pages.items():
        if not page_id:
            print(f"⚠ {task_id}: Parent page ID empty (not configured)")
            continue

        try:
            page = notion.pages.retrieve(page_id)
            title = page['properties']['Name']['title'][0]['text']['content']
            print(f"✓ {task_id}: Parent page '{title}' accessible")
        except Exception as e:
            print(f"✗ {task_id}: Failed to access parent page - {e}")


def verify_configuration():
    """Verify Notion configuration"""
    print("=" * 70)
    print("Notion Configuration Verification")
    print("=" * 70)
    print()

    # Load environment variables
    load_dotenv()
    os.environ['NOTION_DEBUG'] = 'true'

    client = NotionClient()

    # Check 1: API Key
    print("✓ Step 1: Checking NOTION_API_KEY")
    if client.api_key:
        print(f"  Status: ✓ Configured")
        print(f"  Value: {client.api_key[:8]}...{client.api_key[-4:]}")
    else:
        print(f"  Status: ✗ NOT SET")
        print(f"  Action: Add NOTION_API_KEY to your .env file or GitHub Secrets")
        print(f"  Get it from: https://www.notion.so/my-integrations")
        return False
    print()

    # Check 2: Database IDs
    print("✓ Step 2: Checking Database IDs")
    print(f"  Priority: Environment variables > Config file")
    print()

    tasks = {
        'tech_insights': 'NOTION_DB_TECH_INSIGHTS',
        'trending_ai': 'NOTION_DB_TRENDING_AI',
        'ai_news': 'NOTION_DB_AI_NEWS'
    }

    all_configured = True
    for task_id, env_var in tasks.items():
        db_id = client._get_database_id(task_id)
        env_value = os.environ.get(env_var)

        print(f"  Task: {task_id}")
        print(f"    Environment var ({env_var}): ", end="")

        if env_value:
            if check_database_id_format(env_value):
                print(f"✓ {env_value}")
            else:
                print(f"✗ INVALID FORMAT")
                print(f"      Expected: 32-character alphanumeric ID")
                print(f"      Got: {env_value} (length: {len(env_value.replace('-', '').replace(' ', ''))})")
                all_configured = False
        else:
            print(f"✗ NOT SET")
            all_configured = False

        print(f"    Config file: ", end="")
        config_db_id = client.config.get('databases', {}).get(task_id)
        if config_db_id:
            if check_database_id_format(config_db_id):
                print(f"✓ {config_db_id}")
            else:
                print(f"✗ INVALID FORMAT ({config_db_id})")
        else:
            print(f"✗ NOT SET")

        print(f"    Resolved to: {db_id if db_id else 'NOT SET'}")
        print()

    if not all_configured:
        print("  ⚠️  Some database IDs are missing or invalid")
        print()
        print("  How to fix:")
        print("  1. Get your database ID from Notion:")
        print("     - Open your Notion database")
        print("     - Copy the URL: https://notion.so/workspace/[DATABASE_ID]?v=...")
        print("     - Extract the 32-character ID between the last / and ?")
        print()
        print("  2. Add to your .env file:")
        for task_id, env_var in tasks.items():
            print(f"     {env_var}=your_32_char_database_id_here")
        print()
        print("  3. Or add to GitHub Secrets (for CI/CD):")
        for task_id, env_var in tasks.items():
            print(f"     {env_var}")
        print()
        return False

    # Check 2.5: Parent Pages (if configured)
    verify_parent_pages(client, None)

    # Check 3: Client Availability
    print("✓ Step 3: Testing Client Availability")
    if client.is_available():
        print(f"  Status: ✓ Ready to sync")
    else:
        print(f"  Status: ✗ Not available")
        return False
    print()

    # Check 4: Test Dry Run
    print("✓ Step 4: Testing Dry Run (no API calls)")
    test_markdown = "# Test\n\nThis is a test."
    os.environ['NOTION_DRY_RUN'] = 'true'

    success = client.sync_markdown(
        task_id='tech_insights',
        markdown_content=test_markdown,
        date='2026-02-16'
    )

    if success:
        print(f"  Status: ✓ Dry run successful")
    else:
        print(f"  Status: ✗ Dry run failed")
        return False

    del os.environ['NOTION_DRY_RUN']
    print()

    # Summary
    print("=" * 70)
    print("✓ All checks passed! Your Notion configuration is ready.")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Run actual sync: python tests/manual_notion_test.py --task tech_insights --real")
    print("  2. Or run the full automation: python main.py")
    print()

    return True


if __name__ == '__main__':
    success = verify_configuration()
    sys.exit(0 if success else 1)
