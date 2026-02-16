#!/usr/bin/env python3
"""
Inspect Notion database structure to find correct property names.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from notion_client import Client as NotionAPI


def inspect_database(database_id: str):
    """Query database to show its structure"""
    api_key = os.environ.get('NOTION_API_KEY')

    if not api_key:
        print("✗ NOTION_API_KEY not set")
        return

    notion = NotionAPI(auth=api_key)

    print(f"=== Inspecting Database: {database_id} ===")
    print()

    try:
        # Get database info
        database = notion.databases.retrieve(database_id)

        print("Database Properties:")
        print("-" * 60)

        properties = database.get('properties', {})

        for prop_name, prop_config in properties.items():
            prop_type = prop_config.get('type', 'unknown')
            print(f"\n  Property: '{prop_name}'")
            print(f"    Type: {prop_type}")

            # Show additional details based on type
            if prop_type == 'title':
                print(f"    → This is the title property (use this for 'Title')")
            elif prop_type == 'date':
                print(f"    → This is a date property (use this for 'Date')")
            elif prop_type == 'select':
                options = prop_config.get('select', {}).get('options', [])
                if options:
                    print(f"    → Select options: {[opt['name'] for opt in options]}")
                print(f"    → This is a select property (use this for 'Source')")
            elif prop_type == 'rich_text':
                print(f"    → This is a text property")

        print()
        print("=" * 60)
        print("Configuration Example:")
        print("-" * 60)
        print("Update your notion_client.py _create_new_entry method to use:")
        print()

        # Find title property
        title_prop = None
        date_prop = None
        source_prop = None

        for prop_name, prop_config in properties.items():
            prop_type = prop_config.get('type')
            if prop_type == 'title':
                title_prop = prop_name
            elif prop_type == 'date':
                date_prop = prop_name
            elif prop_type == 'select':
                source_prop = prop_name

        if title_prop:
            print(f'  TITLE_PROPERTY = "{title_prop}"')
        else:
            print("  ✗ No title property found!")

        if date_prop:
            print(f'  DATE_PROPERTY = "{date_prop}"')
        else:
            print("  ✗ No date property found!")

        if source_prop:
            print(f'  SOURCE_PROPERTY = "{source_prop}"')
        else:
            print("  ⚠️  No select property found (optional)")

        print()
        print("=" * 60)

    except Exception as e:
        print(f"✗ Error inspecting database: {e}")
        print()
        print("Possible issues:")
        print("  1. Database ID is incorrect")
        print("  2. Integration doesn't have access to this database")
        print("  3. Network connection issue (check proxy settings)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python inspect_notion_database.py <database_id>")
        print()
        print("Example:")
        print("  python inspect_notion_database.py 30943ad321af80d3a5e7d6c17ce3a93a")
        print()
        print("Or use environment variable:")
        print("  NOTION_DB_TECH_INSIGHTS=30943ad321af80d3a5e7d6c17ce3a93a python inspect_notion_database.py tech_insights")
        sys.exit(1)

    arg = sys.argv[1]

    # Check if it's a task ID or actual database ID
    if len(arg) == 32 and arg.replace('-', '').isalnum():
        # It's a database ID
        inspect_database(arg)
    else:
        # It's a task ID, look up from environment
        env_var = f'NOTION_DB_{arg.upper()}'
        db_id = os.environ.get(env_var)
        if not db_id:
            print(f"✗ Environment variable {env_var} not set")
            sys.exit(1)
        inspect_database(db_id)
