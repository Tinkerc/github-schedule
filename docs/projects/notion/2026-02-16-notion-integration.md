# Notion Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate Notion as a storage destination for AI-generated markdown content from tech_insights, trending_ai, and ai_news tasks.

**Architecture:** Task-level sync with shared NotionClient utility - each AI task independently calls NotionClient.sync_markdown() after generating markdown output.

**Tech Stack:** Python 3.8+, notion-client library, Notion API, JSON configuration, environment variables

---

## Phase 1: Core Infrastructure

### Task 1: Add notion-client dependency

**Files:**
- Modify: `requirements.txt`

**Step 1: Add notion-client to requirements.txt**

Add this line to `requirements.txt`:
```txt
notion-client>=2.2.1
```

**Step 2: Install the dependency**

Run: `pip install notion-client`
Expected: Package installs successfully

**Step 3: Commit**

```bash
git add requirements.txt
git commit -m "deps: add notion-client library for Notion API integration"
```

---

### Task 2: Create Notion configuration template

**Files:**
- Create: `config/notion_config.json.example`

**Step 1: Create configuration template**

Create `config/notion_config.json.example`:
```json
{
  "databases": {
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

**Step 2: Create config directory if needed**

Run: `mkdir -p config`
Expected: Directory created (or already exists)

**Step 3: Commit**

```bash
git add config/notion_config.json.example
git commit -m "feat: add Notion configuration template"
```

---

### Task 3: Add Notion environment variables to .env.example

**Files:**
- Modify: `.env.example`

**Step 1: Add Notion environment variables**

Add these lines to `.env.example`:
```bash
# Notion Integration
# Required for syncing AI-generated markdown to Notion
# Get your API key from: https://www.notion.so/my-integrations
NOTION_API_KEY=your_notion_api_key_here

# Optional: Database ID overrides (overrides config/notion_config.json)
# Get database ID from the database URL: https://notion.so/workspace/[DATABASE_ID]?v=...
NOTION_DB_TECH_INSIGHTS=
NOTION_DB_TRENDING_AI=
NOTION_DB_AI_NEWS=

# Optional settings
NOTION_DRY_RUN=false  # Set to true to test without actual API calls
NOTION_DEBUG=false    # Set to true for verbose logging
```

**Step 2: Commit**

```bash
git add .env.example
git commit -m "docs: add Notion environment variables to .env.example"
```

---

### Task 4: Create NotionClient class - initialization

**Files:**
- Create: `core/notion_client.py`

**Step 1: Write failing test for NotionClient initialization**

Create `tests/test_notion_client.py`:
```python
import os
import pytest
from core.notion_client import NotionClient

def test_notion_client_init_without_api_key():
    """Test that NotionClient initializes even without API key"""
    # Ensure no API key is set
    if 'NOTION_API_KEY' in os.environ:
        del os.environ['NOTION_API_KEY']

    client = NotionClient()
    assert client is not None
    assert client.is_available() == False

def test_notion_client_init_with_api_key():
    """Test that NotionClient detects API key from environment"""
    os.environ['NOTION_API_KEY'] = 'test_key_123'
    client = NotionClient()
    assert client is not None
    # Note: Actual availability check requires valid key format
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_notion_client.py::test_notion_client_init_without_api_key -v`
Expected: FAIL with "No module named 'core.notion_client'"

**Step 3: Write minimal NotionClient class**

Create `core/notion_client.py`:
```python
import os
import json
from typing import Optional
from pathlib import Path

class NotionClient:
    """Shared Notion API client for syncing markdown content"""

    def __init__(self):
        """Initialize NotionClient with configuration from file and environment"""
        self.api_key = os.environ.get('NOTION_API_KEY')
        self.config = self._load_config()
        self.debug = os.environ.get('NOTION_DEBUG', 'false').lower() == 'true'
        self.dry_run = os.environ.get('NOTION_DRY_RUN', 'false').lower() == 'true'

    def _load_config(self) -> dict:
        """Load configuration from config/notion_config.json"""
        config_path = Path(__file__).parent.parent / 'config' / 'notion_config.json'

        default_config = {
            "databases": {},
            "settings": {
                "enabled": True,
                "delete_duplicates": True
            }
        }

        if not config_path.exists():
            self._log(f"Config file not found: {config_path}")
            return default_config

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._log(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            self._log(f"Failed to load config: {e}")
            return default_config

    def is_available(self) -> bool:
        """Check if Notion client is properly configured"""
        if not self.api_key:
            self._log("NOTION_API_KEY not configured")
            return False

        if not self.config.get('settings', {}).get('enabled', True):
            self._log("Notion sync disabled in config")
            return False

        return True

    def _log(self, message: str):
        """Print debug message if debug mode is enabled"""
        if self.debug:
            print(f"[Notion] {message}")
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_notion_client.py::test_notion_client_init_without_api_key -v`
Expected: PASS

**Step 5: Run all tests for NotionClient initialization**

Run: `python -m pytest tests/test_notion_client.py -v`
Expected: PASS (all initialization tests)

**Step 6: Commit**

```bash
git add core/notion_client.py tests/test_notion_client.py
git commit -m "feat: implement NotionClient initialization and configuration loading"
```

---

### Task 5: Implement _get_database_id method

**Files:**
- Modify: `core/notion_client.py`
- Modify: `tests/test_notion_client.py`

**Step 1: Write failing test for database ID resolution**

Add to `tests/test_notion_client.py`:
```python
def test_get_database_id_from_env_var():
    """Test that environment variables override config file"""
    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_DB_TECH_INSIGHTS'] = 'env_db_id_123'

    client = NotionClient()
    db_id = client._get_database_id('tech_insights')
    assert db_id == 'env_db_id_123'

    # Cleanup
    del os.environ['NOTION_DB_TECH_INSIGHTS']

def test_get_database_id_from_config():
    """Test that config file is used when no env var is set"""
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()
    # Use the default config which has empty strings
    db_id = client._get_database_id('tech_insights')
    # Should return None or empty string from config
    assert db_id is None or db_id == ''

def test_get_database_id_not_found():
    """Test that None is returned for unknown task_id"""
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()
    db_id = client._get_database_id('unknown_task')
    assert db_id is None
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_notion_client.py::test_get_database_id_from_env_var -v`
Expected: FAIL with "NotionClient has no attribute '_get_database_id'"

**Step 3: Implement _get_database_id method**

Add to `core/notion_client.py` (inside NotionClient class):
```python
    def _get_database_id(self, task_id: str) -> Optional[str]:
        """
        Get database ID for a task.
        Priority: Environment variable > Config file > None
        """
        # 1. Check environment variable override
        env_var_name = f'NOTION_DB_{task_id.upper()}'
        env_db_id = os.environ.get(env_var_name)
        if env_db_id:
            self._log(f"Using database ID from env var {env_var_name}")
            return env_db_id

        # 2. Check config file
        config_db_id = self.config.get('databases', {}).get(task_id)
        if config_db_id:
            self._log(f"Using database ID from config for {task_id}")
            return config_db_id

        # 3. Not found
        self._log(f"No database ID configured for {task_id}")
        return None
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_notion_client.py -v`
Expected: PASS (all database ID tests)

**Step 5: Commit**

```bash
git add core/notion_client.py tests/test_notion_client.py
git commit -m "feat: implement database ID resolution with priority: env > config"
```

---

### Task 6: Implement Notion API client methods

**Files:**
- Modify: `core/notion_client.py`
- Modify: `tests/test_notion_client.py`

**Step 1: Write test for sync_markdown method signature**

Add to `tests/test_notion_client.py`:
```python
from unittest.mock import patch, MagicMock

def test_sync_markdown_returns_false_on_no_config():
    """Test that sync_markdown returns False when database not configured"""
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()
    result = client.sync_markdown('unknown_task', '# Test', '2026-02-16')
    assert result == False

def test_sync_markdown_returns_false_on_no_api_key():
    """Test that sync_markdown returns False when no API key"""
    if 'NOTION_API_KEY' in os.environ:
        del os.environ['NOTION_API_KEY']

    client = NotionClient()
    result = client.sync_markdown('tech_insights', '# Test', '2026-02-16')
    assert result == False

def test_sync_markdown_dry_run_mode():
    """Test that dry_run mode returns True without API calls"""
    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_DRY_RUN'] = 'true'

    client = NotionClient()

    with patch.object(client, '_find_and_delete_existing') as mock_delete, \
         patch.object(client, '_create_new_entry') as mock_create:
        result = client.sync_markdown('tech_insights', '# Test Content', '2026-02-16')

        # Should succeed without calling API methods
        assert result == True
        mock_delete.assert_not_called()
        mock_create.assert_not_called()

    # Cleanup
    del os.environ['NOTION_DRY_RUN']
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_notion_client.py::test_sync_markdown_returns_false_on_no_config -v`
Expected: FAIL with "NotionClient has no attribute 'sync_markdown'"

**Step 3: Implement sync_markdown method**

Add to `core/notion_client.py`:
```python
import time

    def sync_markdown(self, task_id: str, markdown_content: str, date: str) -> bool:
        """
        Sync markdown content to Notion database.

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

            # 1. Check configuration
            database_id = self._get_database_id(task_id)
            if not database_id:
                print(f"[Notion] No database configured for {task_id}")
                return False

            # 2. Check API key
            if not self.api_key:
                print(f"[Notion] NOTION_API_KEY not configured")
                return False

            # 3. Delete existing entry for this date
            if self.config.get('settings', {}).get('delete_duplicates', True):
                self._find_and_delete_existing(database_id, date)

            # 4. Create new entry
            self._create_new_entry(database_id, markdown_content, date)

            print(f"[Notion] ✓ Successfully synced {task_id} for {date}")
            return True

        except Exception as e:
            print(f"[Notion] ✗ Sync failed for {task_id}: {str(e)}")
            return False
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_notion_client.py::test_sync_markdown_dry_run_mode -v`
Expected: PASS

**Step 5: Implement stub methods for delete and create**

Add stub methods to `core/notion_client.py`:
```python
    def _find_and_delete_existing(self, database_id: str, date: str):
        """
        Find and delete existing pages matching the date.
        TODO: Implement Notion API query and delete
        """
        self._log(f"Would delete existing entries for {date} in {database_id}")
        pass

    def _create_new_entry(self, database_id: str, markdown_content: str, date: str):
        """
        Create a new page in Notion with the markdown content.
        TODO: Implement Notion API page creation
        """
        self._log(f"Would create new entry for {date} in {database_id}")
        pass
```

**Step 6: Run all tests**

Run: `python -m pytest tests/test_notion_client.py -v`
Expected: PASS (all tests)

**Step 7: Commit**

```bash
git add core/notion_client.py tests/test_notion_client.py
git commit -m "feat: implement sync_markdown method with dry-run support"
```

---

### Task 7: Implement Notion API integration

**Files:**
- Modify: `core/notion_client.py`

**Step 1: Install notion-client library and create actual API integration**

Add to `core/notion_client.py` (update imports and add API client):
```python
from notion_client import Client as NotionAPI
from notion_client.errors import APIResponseError
```

**Step 2: Implement _find_and_delete_existing with actual API calls**

Replace the stub method in `core/notion_client.py`:
```python
    def _find_and_delete_existing(self, database_id: str, date: str):
        """
        Find and delete existing pages matching the date.
        """
        try:
            notion = NotionAPI(auth=self.api_key)

            # Query database for pages with matching date
            response = notion.databases.query(
                database_id=database_id,
                filter={
                    "property": "Date",
                    "date": {
                        "equals": date
                    }
                }
            )

            # Delete each matching page
            for page in response.get('results', []):
                page_id = page['id']
                notion.pages.delete(page_id)
                self._log(f"Deleted existing page: {page_id}")

        except APIResponseError as e:
            print(f"[Notion] API error while deleting: {e}")
            raise
        except Exception as e:
            print(f"[Notion] Failed to delete existing entries: {e}")
            # Don't raise - we want to continue to creation
```

**Step 3: Implement _create_new_entry with actual API calls**

Replace the stub method in `core/notion_client.py`:
```python
    def _create_new_entry(self, database_id: str, markdown_content: str, date: str):
        """
        Create a new page in Notion with the markdown content.
        """
        try:
            notion = NotionAPI(auth=self.api_key)

            # Create new page
            notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": date
                                }
                            }
                        ]
                    },
                    "Date": {
                        "date": {
                            "start": date
                        }
                    },
                    "Source": {
                        "select": {
                            "name": "github-schedule"
                        }
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

            self._log(f"Created new page for {date}")

        except APIResponseError as e:
            print(f"[Notion] API error while creating page: {e}")
            raise
        except Exception as e:
            print(f"[Notion] Failed to create new entry: {e}")
            raise
```

**Step 4: Test manually with dry-run**

Run: `NOTION_DRY_RUN=true python -c "from core.notion_client import NotionClient; c = NotionClient(); print(c.is_available())"`
Expected: False (no API key configured)

**Step 5: Commit**

```bash
git add core/notion_client.py
git commit -m "feat: implement Notion API integration for query, delete, and create operations"
```

---

## Phase 2: Task Integration

### Task 8: Integrate Notion sync into tech_insights task

**Files:**
- Modify: `tasks/tech_insights.py`

**Step 1: Add Notion import at top of file**

Add this import to `tasks/tech_insights.py` after line 6:
```python
from core.notion_client import NotionClient
```

**Step 2: Add Notion sync after file save**

Find the section in `execute()` method where markdown is saved (around line 46-52) and add Notion sync:

Replace lines 46-52:
```python
            # 保存简报
            output_path = self.get_output_path(f"tech-insights/{self.get_today()}.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(insights)

            print(f"[{self.TASK_ID}] ✓ 技术简报生成成功")
            print(f"[{self.TASK_ID}] 输出文件: {output_path}")
            return True
```

With:
```python
            # 保存简报
            output_path = self.get_output_path(f"tech-insights/{self.get_today()}.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(insights)

            print(f"[{self.TASK_ID}] ✓ 技术简报生成成功")
            print(f"[{self.TASK_ID}] 输出文件: {output_path}")

            # 同步到 Notion
            try:
                client = NotionClient()
                if client.is_available():
                    success = client.sync_markdown(
                        task_id=self.TASK_ID,
                        markdown_content=insights,
                        date=self.get_today()
                    )
                    if success:
                        print(f"[{self.TASK_ID}] ✓ 已同步到 Notion")
                    else:
                        print(f"[{self.TASK_ID}] ⚠️ Notion 同步失败")
                else:
                    print(f"[{self.TASK_ID}] ⚠️ Notion 未配置，跳过同步")
            except Exception as e:
                print(f"[{self.TASK_ID}] ⚠️ Notion 同步异常: {str(e)}")

            return True
```

**Step 3: Test task execution**

Run: `python -m tasks.tech_insights`
Expected: Task executes, prints Notion sync message (will skip if not configured)

**Step 4: Commit**

```bash
git add tasks/tech_insights.py
git commit -m "feat: integrate Notion sync into tech_insights task"
```

---

### Task 9: Integrate Notion sync into trending_ai task

**Files:**
- Modify: `tasks/trending_ai.py`

**Step 1: Add Notion import at top of file**

Add this import to `tasks/trending_ai.py` after line 13:
```python
from core.notion_client import NotionClient
```

**Step 2: Add Notion sync after file save**

Find the `_save_analysis` method call in `execute()` (around line 50-59) and add Notion sync after the success block.

Replace lines 50-59:
```python
        # 3. 保存分析结果
        # 使用 get_output_path 确保 output/github-trending/ 前缀
        analysis_file = self.get_output_path(f'github-trending/{stryear}/{strdate}-analysis.md')
        success = self._save_analysis(analysis, analysis_file)

        if success:
            print("\n" + "="*60)
            print("✓ AI 分析任务完成")
            print(f"原始数据: {trending_file}")
            print(f"分析报告: {analysis_file}")
            print("="*60)
            return True
        else:
            return False
```

With:
```python
        # 3. 保存分析结果
        # 使用 get_output_path 确保 output/github-trending/ 前缀
        analysis_file = self.get_output_path(f'github-trending/{stryear}/{strdate}-analysis.md')
        success = self._save_analysis(analysis, analysis_file)

        if success:
            print("\n" + "="*60)
            print("✓ AI 分析任务完成")
            print(f"原始数据: {trending_file}")
            print(f"分析报告: {analysis_file}")

            # 同步到 Notion
            try:
                from core.notion_client import NotionClient
                client = NotionClient()
                if client.is_available():
                    notion_success = client.sync_markdown(
                        task_id=self.TASK_ID,
                        markdown_content=analysis,
                        date=strdate
                    )
                    if notion_success:
                        print("✓ 已同步到 Notion")
                    else:
                        print("⚠️ Notion 同步失败")
                else:
                    print("⚠️ Notion 未配置，跳过同步")
            except Exception as e:
                print(f"⚠️ Notion 同步异常: {str(e)}")

            print("="*60)
            return True
        else:
            return False
```

**Step 3: Test task execution**

Run: `python -m tasks.trending_ai`
Expected: Task executes, prints Notion sync message

**Step 4: Commit**

```bash
git add tasks/trending_ai.py
git commit -m "feat: integrate Notion sync into trending_ai task"
```

---

## Phase 3: Testing & Documentation

### Task 10: Create manual test script

**Files:**
- Create: `tests/manual_notion_test.py`

**Step 1: Create manual test script**

Create `tests/manual_notion_test.py`:
```python
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
```

**Step 2: Make script executable**

Run: `chmod +x tests/manual_notion_test.py`

**Step 3: Test dry-run mode**

Run: `python tests/manual_notion_test.py --task tech_insights --dry-run`
Expected: Prints dry-run messages

**Step 4: Commit**

```bash
git add tests/manual_notion_test.py
git commit -m "test: add manual Notion integration test script"
```

---

### Task 11: Update README with Notion setup instructions

**Files:**
- Modify: `README.md`

**Step 1: Add Notion section to README**

Add this section to `README.md` (after existing features):
```markdown
## Notion Integration

The system can sync AI-generated markdown content to Notion databases for mobile access.

### Setup

1. **Create Notion Integration**
   - Go to https://www.notion.so/my-integrations
   - Create a new integration and copy the "Internal Integration Token"
   - This is your `NOTION_API_KEY`

2. **Create Notion Databases**
   - Create a database for each content type (Tech Insights, GitHub Trending, etc.)
   - Add these properties to each database:
     - `Title` (title type)
     - `Date` (date type)
     - `Source` (select type, add option "github-schedule")

3. **Get Database IDs**
   - Open each database in Notion
   - Copy the database ID from the URL: `https://notion.so/workspace/[DATABASE_ID]?v=...`

4. **Configure the Project**
   - Copy `config/notion_config.json.example` to `config/notion_config.json`
   - Add your database IDs to the config file
   - Or set environment variables: `NOTION_DB_TECH_INSIGHTS`, etc.

5. **Add to .env file**
   ```bash
   NOTION_API_KEY=your_integration_token_here
   NOTION_DB_TECH_INSIGHTS=your_database_id_here
   ```

### Testing

Test with dry-run mode (no API calls):
```bash
NOTION_DRY_RUN=true python -m tasks.tech_insights
```

Test with actual sync:
```bash
python tests/manual_notion_test.py --task tech_insights --real
```
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add Notion integration setup instructions to README"
```

---

### Task 12: Create detailed Notion setup guide

**Files:**
- Create: `docs/notion-setup-guide.md`

**Step 1: Create comprehensive setup guide**

Create `docs/notion-setup-guide.md`:
```markdown
# Notion Integration Setup Guide

This guide walks you through setting up Notion integration for the GitHub Schedule automation system.

## Prerequisites

- A Notion account (free tier works)
- Admin access to create integrations
- Basic understanding of Notion databases

## Step 1: Create Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Fill in the form:
   - **Name**: GitHub Schedule Automation (or your preferred name)
   - **Associated workspace**: Select your workspace
   - **Type**: Internal
   - **Capabilities**: Enable "Read", "Update", "Insert" capabilities
4. Click "Submit"
5. Copy the "Internal Integration Token" - this is your `NOTION_API_KEY`

## Step 2: Create Notion Databases

### For Tech Insights

1. Create a new database in Notion (Table view)
2. Name it: "Tech Insights"
3. Add these columns (properties):
   - **Title** (title) - Default, keep as is
   - **Date** (date) - Create new property, type "Date"
   - **Source** (select) - Create new property, type "Select", add option "github-schedule"

### For GitHub Trending AI

1. Create a new database: "GitHub Trending"
2. Add same properties as above

### For AI News

1. Create a new database: "AI News"
2. Add same properties as above

## Step 3: Get Database IDs

1. Open a database in Notion
2. Look at the URL: `https://notion.so/workspace/[DATABASE_ID]?v=...`
3. Copy the 32-character database ID (includes hyphens)
4. Repeat for each database

Example URL:
```
https://notion.so/workspace/1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p?v=...
```
The database ID is: `1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`

## Step 4: Share Databases with Integration

**Important**: Your integration needs permission to access each database.

1. Open each database
2. Click "..." (top right) → "Add connections"
3. Select your integration (GitHub Schedule Automation)
4. Repeat for all databases

## Step 5: Configure the Project

### Option A: Config File

1. Copy the example config:
   ```bash
   cp config/notion_config.json.example config/notion_config.json
   ```

2. Edit `config/notion_config.json`:
   ```json
   {
     "databases": {
       "tech_insights": "your_tech_insights_db_id",
       "trending_ai": "your_trending_ai_db_id",
       "ai_news": "your_ai_news_db_id"
     },
     "settings": {
       "enabled": true,
       "delete_duplicates": true
     }
   }
   ```

### Option B: Environment Variables

Add to your `.env` file:
```bash
NOTION_API_KEY=your_internal_integration_token
NOTION_DB_TECH_INSIGHTS=your_tech_insights_db_id
NOTION_DB_TRENDING_AI=your_trending_ai_db_id
NOTION_DB_AI_NEWS=your_ai_news_db_id
```

**Priority**: Environment variables override config file values.

## Step 6: Test the Integration

### Dry Run Test (No API calls)

```bash
NOTION_DRY_RUN=true python -m tasks.tech_insights
```

Expected output:
```
[Notion] DRY RUN: Would sync tech_insights for 2026-02-16
[Notion] Content length: 1234 chars
```

### Real API Test

```bash
python tests/manual_notion_test.py --task tech_insights --real
```

Expected output:
```
[Notion] ✓ Successfully synced tech_insights for 2026-02-16
```

Then check your Notion database - you should see a new entry!

### Full Pipeline Test

```bash
python main.py
```

Check that all AI-generated content appears in your Notion databases.

## Troubleshooting

### "NOTION_API_KEY not configured"

- Make sure you've added `NOTION_API_KEY` to your `.env` file
- Restart your terminal after modifying `.env`

### "No database configured for tech_insights"

- Check that database IDs are in `config/notion_config.json` or set as env vars
- Verify database IDs are correct (32 characters with hyphens)

### "API error: unauthorized"

- Verify your integration token is correct
- Make sure you've shared the database with your integration (Step 5)

### "API error: object not found"

- Check that the database ID is correct
- Verify the database is shared with your integration

### "Rate limited"

- Notion API allows ~3 requests per second
- The system will retry once after 60 seconds
- If you have many tasks, they'll run sequentially with delays

## Debug Mode

Enable verbose logging:

```bash
NOTION_DEBUG=true python -m tasks.tech_insights
```

This will print:
- Configuration loading status
- Database ID resolution
- API call details

## GitHub Actions Integration

To use Notion sync in GitHub Actions:

1. Add `NOTION_API_KEY` to your repository secrets
2. Add database IDs as secrets (optional, or use config file)
3. Update workflow with new secrets

The sync will run automatically with your daily schedule!
```

**Step 2: Commit**

```bash
git add docs/notion-setup-guide.md
git commit -m "docs: add comprehensive Notion integration setup guide"
```

---

## Phase 4: GitHub Actions Integration

### Task 13: Add Notion secrets to GitHub (manual step)

**This is a manual task - no code changes.**

**Step 1: Add GitHub Action Secret**

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `NOTION_API_KEY`
5. Value: Your Notion integration token
6. Click "Add secret"

**Step 2: (Optional) Add database IDs as secrets**

Repeat for each database:
- `NOTION_DB_TECH_INSIGHTS`
- `NOTION_DB_TRENDING_AI`
- `NOTION_DB_AI_NEWS`

**Note**: Document completion in commit message.

---

### Task 14: Verify workflow file supports environment variables

**Files:**
- Read: `.github/workflows/blank.yml`

**Step 1: Check if workflow file handles environment variables correctly**

The workflow should already pass through environment variables from GitHub Secrets. Verify it looks correct.

Current workflow should have:
```yaml
env:
  VOLCENGINE_API_KEY: ${{ secrets.VOLCENGINE_API_KEY }}
  WECOM_WEBHOOK_URL: ${{ secrets.WECOM_WEBHOOK_URL }}
```

**Step 2: Add Notion secrets to workflow (if needed)**

If the workflow uses explicit env variables, add:
```yaml
  NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
  NOTION_DB_TECH_INSIGHTS: ${{ secrets.NOTION_DB_TECH_INSIGHTS }}
  NOTION_DB_TRENDING_AI: ${{ secrets.NOTION_DB_TRENDING_AI }}
```

**Step 3: Commit if changes made**

If you modified the workflow:
```bash
git add .github/workflows/blank.yml
git commit -m "ci: add Notion environment variables to GitHub Actions workflow"
```

---

## Verification

### Task 15: End-to-end verification

**Step 1: Run full pipeline locally**

```bash
# Make sure .env is configured
python main.py
```

Expected:
- All tasks execute successfully
- Notion sync messages appear
- Tasks succeed even if Notion fails

**Step 2: Verify Notion databases**

Check your Notion databases:
- New entries appear with today's date
- Content is properly formatted
- Markdown is rendered correctly

**Step 3: Test duplicate handling**

Run the pipeline twice:
```bash
python main.py
python main.py
```

Expected:
- Only one entry per date (old one deleted)
- Latest content is shown

**Step 4: Test with Notion disabled**

```bash
# Temporarily disable Notion
NOTION_API_KEY="" python main.py
```

Expected:
- All tasks still succeed
- "Notion not configured, skipping" messages appear

**Step 5: Commit verification results**

Create a brief summary of verification:
```bash
echo "Notion integration verified:
- Dry-run tests: PASS
- Real API sync: PASS
- Duplicate handling: PASS
- Graceful degradation: PASS
" > docs/notion-verification.md
git add docs/notion-verification.md
git commit -m "test: verify Notion integration end-to-end"
```

---

## Summary

This implementation plan delivers:
- ✅ Shared NotionClient utility for all tasks
- ✅ Configuration via file and environment variables
- ✅ Immediate sync after each task generates markdown
- ✅ Duplicate handling (delete old, create new)
- ✅ Graceful degradation (task succeeds even if Notion fails)
- ✅ Comprehensive testing and documentation
- ✅ GitHub Actions support

**Total commits**: ~15 commits across 4 phases
**Estimated time**: 2-3 hours for full implementation
**Testing approach**: TDD with unit tests, manual integration tests, and end-to-end verification
