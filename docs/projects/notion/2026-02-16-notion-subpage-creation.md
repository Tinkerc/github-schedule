# Notion Sub-Page Creation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend Notion integration to support creating sub-pages under parent pages as an alternative to database entries.

**Architecture:** Extend existing NotionClient class with sub-page mode. Config-based mode selection (parent_pages vs databases). No changes to task code - mode selection is transparent via existing sync_markdown() interface.

**Tech Stack:** Python 3.8+, notion-client library, pytest for testing

---

## Task 1: Add _get_parent_page_id() method to NotionClient

**Files:**
- Modify: `core/notion_client.py:56-76` (add after _get_database_id method)

**Step 1: Write the failing test**

Create file: `tests/test_notion_client.py`

```python
def test_get_parent_page_id_from_config():
    """Test getting parent page ID from config file"""
    import os
    from pathlib import Path
    import tempfile
    import json

    # Create temp config file
    config = {
        "parent_pages": {
            "tech_insights": "page-123"
        }
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_config_path = f.name

    try:
        client = NotionClient()
        # Patch config path
        client.config = config

        result = client._get_parent_page_id("tech_insights")
        assert result == "page-123"
    finally:
        os.unlink(temp_config_path)

def test_get_parent_page_id_from_env():
    """Test getting parent page ID from environment variable"""
    import os

    os.environ['NOTION_PAGE_TECH_INSIGHTS'] = 'page-456'

    client = NotionClient()
    client.config = {}  # Empty config

    result = client._get_parent_page_id("tech_insights")
    assert result == "page-456"

    del os.environ['NOTION_PAGE_TECH_INSIGHTS']

def test_get_parent_page_id_not_found():
    """Test returning None when parent page ID not configured"""
    client = NotionClient()
    client.config = {}

    result = client._get_parent_page_id("nonexistent")
    assert result is None
```

**Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_notion_client.py::test_get_parent_page_id_from_config -v
```

Expected: FAIL with "'NotionClient' object has no attribute '_get_parent_page_id'"

**Step 3: Write minimal implementation**

In `core/notion_client.py`, add after line 76 (after _get_database_id method):

```python
def _get_parent_page_id(self, task_id: str) -> Optional[str]:
    """
    Get parent page ID for a task.
    Priority: Config file > Environment variable > None

    Args:
        task_id: Task identifier (e.g., 'tech_insights')

    Returns:
        Parent page ID string or None
    """
    # 1. Check config file
    config_page_id = self.config.get('parent_pages', {}).get(task_id)
    if config_page_id:
        self._log(f"Using parent page ID from config for {task_id}")
        return config_page_id

    # 2. Check environment variable override
    env_var_name = f'NOTION_PAGE_{task_id.upper()}'
    env_page_id = os.environ.get(env_var_name)
    if env_page_id:
        self._log(f"Using parent page ID from env var {env_var_name}")
        return env_page_id

    # 3. Not found
    self._log(f"No parent page ID configured for {task_id}")
    return None
```

**Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_notion_client.py::test_get_parent_page_id_from_config -v
python -m pytest tests/test_notion_client.py::test_get_parent_page_id_from_env -v
python -m pytest tests/test_notion_client.py::test_get_parent_page_id_not_found -v
```

Expected: All PASS

**Step 5: Commit**

```bash
git add core/notion_client.py tests/test_notion_client.py
git commit -m "feat: add _get_parent_page_id method to NotionClient"
```

---

## Task 2: Add _create_sub_page() method to NotionClient

**Files:**
- Modify: `core/notion_client.py:230-233` (add after _create_new_entry method)

**Step 1: Write the failing test**

```python
@patch('core.notion_client.NotionAPI')
def test_create_sub_page(mock_notion_api):
    """Test creating a sub-page under a parent page"""
    # Setup mock
    mock_client = Mock()
    mock_notion_api.return_value = mock_client
    mock_client.pages.create.return_value = {"id": "new-page-123"}

    client = NotionClient()
    client.dry_run = False

    result = client._create_sub_page(
        parent_page_id="parent-123",
        markdown_content="# Test Content\n\nThis is test content.",
        date="2026-02-16"
    )

    assert result is True
    mock_client.pages.create.assert_called_once()

    # Verify the call arguments
    call_args = mock_client.pages.create.call_args
    assert call_args[1]['parent']['page_id'] == "parent-123"
    assert call_args[1]['properties']['Name']['title'][0]['text']['content'] == "2026-02-16"

def test_create_sub_page_dry_run():
    """Test dry run mode for sub-page creation"""
    client = NotionClient()
    client.dry_run = True

    result = client._create_sub_page(
        parent_page_id="parent-123",
        markdown_content="# Test",
        date="2026-02-16"
    )

    assert result is True
```

**Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_notion_client.py::test_create_sub_page -v
```

Expected: FAIL with method not found

**Step 3: Write minimal implementation**

In `core/notion_client.py`, add after line 232:

```python
def _create_sub_page(self, parent_page_id: str, markdown_content: str, date: str):
    """
    Create a new page under a parent page with markdown content.

    Args:
        parent_page_id: ID of the parent page
        markdown_content: Full markdown content
        date: Date string for page title

    Raises:
        Exception: If API call fails
    """
    try:
        notion = NotionAPI(auth=self.api_key)

        # Create new page under parent
        notion.pages.create(
            parent={"page_id": parent_page_id},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": date
                            }
                        }
                    ]
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": markdown_content
                                }
                            }
                        ]
                    }
                }
            ]
        )

        self._log(f"Created sub-page '{date}' under parent {parent_page_id}")

    except APIResponseError as e:
        print(f"[Notion] API error while creating sub-page: {e}")
        raise
    except Exception as e:
        print(f"[Notion] Failed to create sub-page: {e}")
        raise
```

**Step 4: Handle dry run mode**

Update the method to check dry_run at the start:

```python
def _create_sub_page(self, parent_page_id: str, markdown_content: str, date: str):
    """
    Create a new page under a parent page with markdown content.

    Args:
        parent_page_id: ID of the parent page
        markdown_content: Full markdown content
        date: Date string for page title

    Returns:
        bool: True if successful

    Raises:
        Exception: If API call fails (except in dry run)
    """
    # Dry run mode
    if self.dry_run:
        print(f"[Notion] DRY RUN: Would create sub-page '{date}' under parent {parent_page_id}")
        print(f"[Notion] Content length: {len(markdown_content)} chars")
        return True

    try:
        notion = NotionAPI(auth=self.api_key)

        # Create new page under parent
        notion.pages.create(
            parent={"page_id": parent_page_id},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": date
                            }
                        }
                    ]
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": markdown_content
                                }
                            }
                        ]
                    }
                }
            ]
        )

        self._log(f"Created sub-page '{date}' under parent {parent_page_id}")
        return True

    except APIResponseError as e:
        print(f"[Notion] API error while creating sub-page: {e}")
        raise
    except Exception as e:
        print(f"[Notion] Failed to create sub-page: {e}")
        raise
```

**Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_notion_client.py::test_create_sub_page -v
python -m pytest tests/test_notion_client.py::test_create_sub_page_dry_run -v
```

Expected: All PASS

**Step 6: Commit**

```bash
git add core/notion_client.py tests/test_notion_client.py
git commit -m "feat: add _create_sub_page method to NotionClient"
```

---

## Task 3: Add _delete_existing_sub_pages() method

**Files:**
- Modify: `core/notion_client.py` (add after _create_sub_page method)

**Step 1: Write the failing test**

```python
@patch('core.notion_client.NotionAPI')
def test_delete_existing_sub_pages(mock_notion_api):
    """Test deleting existing sub-pages with matching date"""
    # Setup mock
    mock_client = Mock()
    mock_notion_api.return_value = mock_client

    # Mock search response to find pages
    mock_client.pages.search.return_value = {
        'results': [
            {'id': 'page-1', 'properties': {'Name': {'title': [{'text': {'content': '2026-02-16'}}]}}},
            {'id': 'page-2', 'properties': {'Name': {'title': [{'text': {'content': '2026-02-16'}}]}}}
        ]
    }
    mock_client.pages.update.return_value = {}

    client = NotionClient()
    client.dry_run = False

    client._delete_existing_sub_pages(
        parent_page_id="parent-123",
        date="2026-02-16"
    )

    # Verify both pages were archived
    assert mock_client.pages.update.call_count == 2
    calls = mock_client.pages.update.call_args_list
    assert calls[0][1]['archived'] is True
    assert calls[1][1]['archived'] is True

def test_delete_existing_sub_pages_dry_run():
    """Test dry run mode doesn't delete"""
    client = NotionClient()
    client.dry_run = True

    # Should not raise any errors
    client._delete_existing_sub_pages("parent-123", "2026-02-16")
```

**Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_notion_client.py::test_delete_existing_sub_pages -v
```

Expected: FAIL with method not found

**Step 3: Write minimal implementation**

In `core/notion_client.py`, add after _create_sub_page method:

```python
def _delete_existing_sub_pages(self, parent_page_id: str, date: str):
    """
    Find and delete existing child pages with matching date title.

    Args:
        parent_page_id: ID of the parent page
        date: Date string to match in page titles

    Returns:
        None
    """
    # Dry run mode
    if self.dry_run:
        print(f"[Notion] DRY RUN: Would delete existing sub-pages '{date}' under parent {parent_page_id}")
        return

    try:
        notion = NotionAPI(auth=self.api_key)

        # Search for child pages with matching title
        # Note: Notion search API doesn't support filtering by parent directly
        # We'll search by title and verify parent in results
        response = notion.pages.search(
            query=date,
            filter={
                "property": "object",
                "value": "page"
            }
        )

        # Filter results to only pages under our parent
        child_pages = []
        for page in response.get('results', []):
            page_id = page['id']
            # Check if this page is a child of our parent
            # The parent info is in page['parent']
            if page.get('parent', {}).get('page_id') == parent_page_id:
                # Also verify the title matches
                title = page['properties']['Name']['title'][0]['text']['content']
                if title == date:
                    child_pages.append(page)

        # Delete each matching page (archive it)
        for page in child_pages:
            page_id = page['id']
            notion.pages.update(page_id, archived=True)
            self._log(f"Deleted existing sub-page: {page_id}")

    except APIResponseError as e:
        print(f"[Notion] API error while deleting sub-pages: {e}")
        # Don't raise - we want to continue to creation
    except Exception as e:
        print(f"[Notion] Failed to delete existing sub-pages: {e}")
        # Don't raise - we want to continue to creation
```

**Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_notion_client.py::test_delete_existing_sub_pages -v
python -m pytest tests/test_notion_client.py::test_delete_existing_sub_pages_dry_run -v
```

Expected: All PASS

**Step 5: Commit**

```bash
git add core/notion_client.py tests/test_notion_client.py
git commit -m "feat: add _delete_existing_sub_pages method to NotionClient"
```

---

## Task 4: Modify sync_markdown() to support sub-page mode

**Files:**
- Modify: `core/notion_client.py:83-142` (sync_markdown method)

**Step 1: Write the failing test**

```python
@patch('core.notion_client.NotionAPI')
def test_sync_markdown_uses_sub_page_mode(mock_notion_api):
    """Test sync_markdown uses sub-page mode when parent_page_id configured"""
    mock_client = Mock()
    mock_notion_api.return_value = mock_client
    mock_client.databases.retrieve.return_value = {}  # Not called in sub-page mode

    client = NotionClient()
    client.config = {
        'parent_pages': {
            'tech_insights': 'parent-123'
        }
    }
    client.dry_run = False

    # Mock delete and create methods
    with patch.object(client, '_delete_existing_sub_pages') as mock_delete:
        with patch.object(client, '_create_sub_page', return_value=True) as mock_create:
            result = client.sync_markdown(
                task_id='tech_insights',
                markdown_content='# Test',
                date='2026-02-16'
            )

            assert result is True
            mock_delete.assert_called_once_with('parent-123', '2026-02-16')
            mock_create.assert_called_once_with('parent-123', '# Test', '2026-02-16')

@patch('core.notion_client.NotionAPI')
def test_sync_markdown_falls_back_to_database(mock_notion_api):
    """Test sync_markdown falls back to database mode when no parent_page_id"""
    mock_client = Mock()
    mock_notion_api.return_value = mock_client
    mock_client.databases.retrieve.return_value = {
        'id': 'db-123',
        'data_sources': []
    }

    client = NotionClient()
    client.config = {
        'databases': {
            'tech_insights': 'db-123'
        }
    }
    client.dry_run = False

    result = client.sync_markdown(
        task_id='tech_insights',
        markdown_content='# Test',
        date='2026-02-16'
    )

    assert result is True
    # Verify database API was called (not sub-page methods)
    mock_client.databases.retrieve.assert_called()
```

**Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_notion_client.py::test_sync_markdown_uses_sub_page_mode -v
```

Expected: FAIL - sync_markdown doesn't check for parent_page_id yet

**Step 3: Modify sync_markdown() implementation**

Update the `sync_markdown` method in `core/notion_client.py:83-142`:

```python
def sync_markdown(self, task_id: str, markdown_content: str, date: str) -> bool:
    """
    Sync markdown content to Notion.
    Supports both database entries and sub-pages.

    Args:
        task_id: Task identifier (e.g., 'tech_insights')
        markdown_content: Full markdown content to sync
        date: Date string in YYYY-MM-DD format

    Returns:
        bool: True if sync succeeded, False otherwise
    """
    try:
        self._log(f"Syncing {task_id} for {date}")

        # Dry run mode
        if self.dry_run:
            print(f"[Notion] DRY RUN: Would sync {task_id} for {date}")
            print(f"[Notion] Content length: {len(markdown_content)} chars")
            return True

        # 1. Check API key
        if not self.api_key:
            print(f"[Notion] NOTION_API_KEY not configured")
            return False

        # 2. Check for parent page ID (sub-page mode)
        parent_page_id = self._get_parent_page_id(task_id)
        if parent_page_id:
            self._log("Using sub-page mode")
            # Delete existing entry for this date
            if self.config.get('settings', {}).get('delete_duplicates', True):
                self._delete_existing_sub_pages(parent_page_id, date)

            # Create new sub-page
            self._create_sub_page(parent_page_id, markdown_content, date)

            print(f"[Notion] ✓ Successfully synced {task_id} for {date} (sub-page)")
            return True

        # 3. Fall back to database mode
        database_id = self._get_database_id(task_id)
        if not database_id:
            print(f"[Notion] No parent page or database configured for {task_id}")
            return False

        self._log("Using database mode")

        # 4. Detect database type (Published Markdown vs standard)
        notion = NotionAPI(auth=self.api_key)
        db_info = notion.databases.retrieve(database_id)

        # Check if it's a Published Markdown database (has data_sources)
        is_published_markdown = 'data_sources' in db_info and db_info['data_sources']

        if is_published_markdown:
            self._log("Detected Published Markdown data source")
            # Extract data source ID
            ds_id = db_info['data_sources'][0]['id'].replace('-', '')
            return self._sync_to_published_markdown(ds_id, database_id, markdown_content, date)
        else:
            self._log("Detected standard database")
            # 4a. Delete existing entry for this date
            if self.config.get('settings', {}).get('delete_duplicates', True):
                self._find_and_delete_existing(database_id, date)

            # 4b. Create new entry
            self._create_new_entry(database_id, markdown_content, date)

            print(f"[Notion] ✓ Successfully synced {task_id} for {date}")
            return True

    except Exception as e:
        print(f"[Notion] ✗ Sync failed for {task_id}: {str(e)}")
        return False
```

**Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_notion_client.py::test_sync_markdown_uses_sub_page_mode -v
python -m pytest tests/test_notion_client.py::test_sync_markdown_falls_back_to_database -v
```

Expected: All PASS

**Step 5: Commit**

```bash
git add core/notion_client.py tests/test_notion_client.py
git commit -m "feat: add sub-page mode support to sync_markdown"
```

---

## Task 5: Update config file with parent_pages example

**Files:**
- Modify: `config/notion_config.json`

**Step 1: Create example config structure**

Update `config/notion_config.json` to include the parent_pages section (but leave it empty initially, users will add their IDs):

```json
{
  "databases": {
    "tech_insights": "30943ad321af80d3a5e7d6c17ce3a93a",
    "trending_ai": "30943ad321af80d3a5e7d6c17ce3a93a",
    "ai_news": "30943ad321af80d3a5e7d6c17ce3a93a"
  },
  "parent_pages": {
    "tech_insights": "",
    "trending_ai": "",
    "ai_news": ""
  },
  "settings": {
    "enabled": true,
    "delete_duplicates": true
  }
}
```

**Step 2: Document config format**

Create file: `docs/notion-subpage-config.md`

```markdown
# Notion Sub-Page Configuration

## Overview

The Notion integration supports two sync modes:
- **Database mode**: Creates entries as rows in a Notion database
- **Sub-page mode**: Creates pages as children under a parent page

## Configuration

### Sub-Page Mode (Recommended for daily content)

Edit `config/notion_config.json`:

```json
{
  "parent_pages": {
    "tech_insights": "your-parent-page-id-1",
    "trending_ai": "your-parent-page-id-2",
    "ai_news": "your-parent-page-id-3"
  }
}
```

**To find a page ID:**
1. Open the page in Notion
2. Copy the URL
3. The page ID is the 32-character string after `/` and before `?`
   Example: `https://www.notion.so/your-workspace/PAGE-NAME-32charid?pvs=4`
                                                    ^^^^^^^^^^^^^^^^^^^^^^^^

### Database Mode (Legacy)

```json
{
  "databases": {
    "task_name": "database-id"
  }
}
```

## Priority

Tasks check `parent_pages` first, then fall back to `databases`.
If neither is configured, the task will fail with a configuration error.

## Environment Variables

You can override config with environment variables:
- `NOTION_PAGE_TECH_INSIGHTS=page-id` for sub-page mode
- `NOTION_DB_TECH_INSIGHTS=db-id` for database mode

## Migration

To migrate a task from database to sub-page:
1. Add the task to `parent_pages` with your page ID
2. (Optional) Remove the task from `databases`
3. The next sync will create a sub-page instead of a database entry

Old database entries are not automatically deleted. Remove them manually if needed.
```

**Step 3: Commit**

```bash
git add config/notion_config.json docs/notion-subpage-config.md
git commit -m "docs: add parent_pages config and documentation"
```

---

## Task 6: Extend config validation script

**Files:**
- Modify: `scripts/verify_notion_config.py`

**Step 1: Read current script**

```bash
cat scripts/verify_notion_config.py
```

**Step 2: Add parent page validation**

Extend the script to validate parent_page_ids:

```python
def verify_parent_pages(client, config):
    """Verify parent pages exist and are accessible"""
    print("\n=== Verifying Parent Pages ===")

    parent_pages = config.get('parent_pages', {})
    if not parent_pages:
        print("No parent_pages configured")
        return

    from notion_client import Client as NotionAPI
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

# Add to main()
if __name__ == '__main__':
    # ... existing code ...
    verify_parent_pages(client, config)
```

**Step 3: Test the script**

```bash
python scripts/verify_notion_config.py
```

**Step 4: Commit**

```bash
git add scripts/verify_notion_config.py
git commit -m "feat: add parent page validation to config verifier"
```

---

## Task 7: Create manual test script for sub-pages

**Files:**
- Create: `scripts/test_sub_page_creation.py`

**Step 1: Write test script**

```python
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

    # Manually call sub-page methods
    client.config = {
        'parent_pages': {
            'test': parent_page_id
        },
        'settings': {
            'delete_duplicates': True
        }
    }

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
```

**Step 2: Make script executable**

```bash
chmod +x scripts/test_sub_page_creation.py
```

**Step 3: Test the script (dry run only)**

```bash
NOTION_PAGE_ID=test-page-id python scripts/test_sub_page_creation.py
```

**Step 4: Commit**

```bash
git add scripts/test_sub_page_creation.py
git commit -m "test: add manual sub-page creation test script"
```

---

## Task 8: Run full test suite

**Step 1: Run all unit tests**

```bash
python -m pytest tests/test_notion_client.py -v
```

Expected: All PASS

**Step 2: Run with dry run mode**

```bash
NOTION_DRY_RUN=true NOTION_DEBUG=true python -m tasks.tech_insights
```

Expected: Shows dry run output for sub-page mode if configured

**Step 3: Manual integration test**

Follow the manual test script:

```bash
# Set your test parent page ID
export NOTION_PAGE_ID=your-actual-page-id

# Run the test script
python scripts/test_sub_page_creation.py
```

Follow the prompts and verify in Notion UI.

**Step 4: Commit**

```bash
git add tests/test_notion_client.py
git commit -m "test: finalize sub-page creation tests"
```

---

## Task 9: Update documentation

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`

**Step 1: Update README.md**

Add section about Notion sub-page mode:

```markdown
## Notion Integration

The system supports two sync modes for Notion:

### Sub-Page Mode (Recommended)

Daily content is created as sub-pages under a parent page:
- Better for organizing daily content
- Hierarchical structure in Notion
- One parent page per task

Configuration in `config/notion_config.json`:

```json
{
  "parent_pages": {
    "tech_insights": "parent-page-id-1",
    "trending_ai": "parent-page-id-2",
    "ai_news": "parent-page-id-3"
  }
}
```

### Database Mode (Legacy)

Daily content is created as database entries.

See `docs/notion-subpage-config.md` for detailed configuration.
```

**Step 2: Update CLAUDE.md**

Add to the Notion integration section:

```markdown
### Notion Integration (Updated)

The Notion integration now supports two modes:

1. **Sub-Page Mode**: Creates pages under a parent page (recommended)
   - Configure `parent_pages` in `config/notion_config.json`
   - Each task gets its own parent page
   - Daily pages are created as children

2. **Database Mode**: Creates database entries (legacy)
   - Configure `databases` in `config/notion_config.json`
   - Pages appear as rows in a database

The `NotionClient.sync_markdown()` method automatically detects which mode to use based on config.
Tasks don't need to know which mode is active.

**Testing:**
- Run `python scripts/test_sub_page_creation.py` for manual testing
- Run `python scripts/verify_notion_config.py` to validate config
```

**Step 3: Commit**

```bash
git add README.md CLAUDE.md
git commit -m "docs: update documentation for sub-page mode"
```

---

## Task 10: Final verification and cleanup

**Step 1: Verify all tests pass**

```bash
python -m pytest tests/ -v
```

**Step 2: Verify config validation**

```bash
python scripts/verify_notion_config.py
```

**Step 3: Check git status**

```bash
git status
```

**Step 4: Create final summary commit**

```bash
git add -A
git commit -m "feat: complete Notion sub-page creation implementation

Implementation complete with:
- Sub-page mode support in NotionClient
- Configuration via parent_pages
- Automatic mode detection
- Comprehensive tests
- Documentation updates

All tasks (tech_insights, trending_ai, ai_news) can now create
sub-pages instead of database entries by configuring parent_pages.
"
```

**Step 5: Push to remote**

```bash
git push origin refactor-project-architecture
```

---

## Migration Checklist

When ready to enable sub-page mode in production:

- [ ] Deploy code changes to production
- [ ] Add parent page IDs to `config/notion_config.json`
- [ ] Run `scripts/verify_notion_config.py` to verify access
- [ ] Enable ONE task first (e.g., `tech_insights`)
- [ ] Monitor GitHub Actions workflow
- [ ] Verify sub-page appears in Notion UI
- [ ] Enable remaining tasks one at a time
- [ ] (Optional) Remove old database entries manually
- [ ] (Optional) Remove migrated tasks from `databases` config

---

## Rollback Plan

If issues arise:
1. Remove task from `parent_pages` in config
2. Task automatically falls back to `databases` mode
3. No code changes needed

---

## Success Criteria

- [ ] All unit tests pass
- [ ] Manual test script works end-to-end
- [ ] Config validation script checks parent pages
- [ ] Documentation is complete
- [ ] Dry run mode works correctly
- [ ] Error handling is robust
- [ ] Code committed and pushed

---

**End of Implementation Plan**
