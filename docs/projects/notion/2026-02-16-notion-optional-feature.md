# Notion as Optional Feature - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Simplify Notion integration to use pure environment variables with a single master switch, removing config file complexity.

**Architecture:** Remove `config/notion_config.json`, load all settings from environment variables, add graceful migration warnings, simplify `NotionClient` logic.

**Tech Stack:** Python 3.8+, python-dotenv, notion-client, pytest

---

## Context for Engineer

This is a GitHub Actions automation system that fetches AI news, GitHub trending, and tech insights. Notion sync is currently optional but configured via both JSON file and env vars - we're simplifying to env vars only.

**Key files you'll work with:**
- `core/notion_client.py` - Main Notion integration (needs major refactoring)
- `tasks/trending_ai.py` - Uses NotionClient (no changes needed, but verify it works)
- `tasks/tech_insights.py` - Uses NotionClient (no changes needed, but verify it works)
- `.env.example` - Update with new env var structure
- `docs/notion-migration-guide.md` - NEW: Migration documentation
- `README.md` - Update Notion setup section

**Testing philosophy:** We use TDD. Write failing test first, then implement, then verify. Each atomic change gets committed.

---

## Task 1: Establish Baseline Tests

**Goal:** Verify current NotionClient behavior before refactoring

**Files:**
- Test: `tests/test_notion_client.py`
- Reference: `core/notion_client.py` (read only)

**Step 1: Run existing tests to establish baseline**

```bash
cd /Users/tinker.chen/work/code/learning/github/github-schedule
pytest tests/test_notion_client.py -v
```

Expected: All current tests pass (or note which fail - this is our baseline)

**Step 2: Document current behavior**

Create a test file to capture current NotionClient initialization behavior:

```python
# tests/test_notion_client_current_behavior.py
"""Document current NotionClient behavior before refactoring"""
import os
import pytest
from core.notion_client import NotionClient

def test_current_init_with_no_config():
    """Test that NotionClient initializes even without config file"""
    # Ensure no env vars set
    for key in list(os.environ.keys()):
        if 'NOTION' in key:
            del os.environ[key]

    client = NotionClient()
    # Current behavior: Should have default config
    assert hasattr(client, 'config')
    assert client.config.get('settings', {}).get('enabled') == True

def test_current_is_available_checks_config_file():
    """Test that is_available currently checks config file"""
    # This test documents current behavior
    client = NotionClient()
    # Current: Returns True even without API key if config.enabled=True
    result = client.is_available()
    # Document what happens currently
    print(f"Current is_available result: {result}")
```

**Step 3: Run baseline documentation test**

```bash
pytest tests/test_notion_client_current_behavior.py::test_current_init_with_no_config -v -s
```

**Step 4: Commit baseline test**

```bash
git add tests/test_notion_client_current_behavior.py
git commit -m "test: add baseline documentation for current NotionClient behavior"
```

---

## Task 2: Add Obsolete Config File Warning

**Goal:** Warn users if old config file exists

**Files:**
- Modify: `core/notion_client.py:12-43` (the `__init__` method)

**Step 1: Write test for warning message**

```python
# tests/test_notion_client_obsolete_config_warning.py
import os
import tempfile
import pytest
from pathlib import Path
from core.notion_client import NotionClient
from io import StringIO
import sys

def test_warns_about_obsolete_config_file():
    """Test that NotionClient warns when config/notion_config.json exists"""
    # Create a temporary config file
    original_path = Path(__file__).parent.parent / 'config' / 'notion_config.json'
    temp_config = Path(__file__).parent.parent / 'config' / 'notion_config.json.temp'

    # Backup existing config if present
    had_backup = False
    if original_path.exists():
        original_path.rename(temp_config)
        had_backup = True

    try:
        # Create test config file
        original_path.parent.mkdir(exist_ok=True)
        original_path.write_text('{"test": "data"}')

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        client = NotionClient()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Should contain warning
        assert 'WARNING: config/notion_config.json is no longer used' in output
        assert 'Please use environment variables instead' in output

    finally:
        # Cleanup
        if original_path.exists():
            original_path.unlink()
        if had_backup and temp_config.exists():
            temp_config.rename(original_path)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_notion_client_obsolete_config_warning.py::test_warns_about_obsolete_config_file -v
```

Expected: FAIL - warning code doesn't exist yet

**Step 3: Implement warning logic in `__init__`**

Open `core/notion_client.py` and modify the `__init__` method (around line 12):

```python
def __init__(self):
    """Initialize NotionClient with configuration from file and environment"""
    # Warn about obsolete config file
    config_path = Path(__file__).parent.parent / 'config' / 'notion_config.json'
    if config_path.exists():
        print("[Notion] ⚠️ WARNING: config/notion_config.json is no longer used")
        print("[Notion] ⚠️ Please use environment variables instead")
        print("[Notion] ⚠️ See docs/notion-migration-guide.md for help")

    self.api_key = os.environ.get('NOTION_API_KEY')
    self.debug = os.environ.get('NOTION_DEBUG', 'false').lower() == 'true'
    self.dry_run = os.environ.get('NOTION_DRY_RUN', 'false').lower() == 'true'
    self.config = self._load_config()  # Keep this for now, remove in Task 3
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_notion_client_obsolete_config_warning.py::test_warns_about_obsolete_config_file -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add core/notion_client.py tests/test_notion_client_obsolete_config_warning.py
git commit -m "feat: add warning for obsolete config/notion_config.json"
```

---

## Task 3: Refactor `__init__()` to Remove Config File Loading

**Goal:** Load all settings from environment variables only

**Files:**
- Modify: `core/notion_client.py:12-43` (entire `__init__` and `_load_config`)

**Step 1: Write test for env var initialization**

```python
# tests/test_notion_client_env_vars.py
import os
import pytest
from core.notion_client import NotionClient

def test_init_loads_from_env_vars():
    """Test that NotionClient loads settings from environment variables"""
    # Set env vars
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key_123'
    os.environ['NOTION_DEBUG'] = 'true'
    os.environ['NOTION_DRY_RUN'] = 'false'
    os.environ['NOTION_DELETE_DUPLICATES'] = 'false'

    client = NotionClient()

    assert client.enabled == True
    assert client.api_key == 'test_key_123'
    assert client.debug == True
    assert client.dry_run == False
    assert client.delete_duplicates == False

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']
    del os.environ['NOTION_DEBUG']
    del os.environ['NOTION_DRY_RUN']
    del os.environ['NOTION_DELETE_DUPLICATES']

def test_init_defaults_to_disabled():
    """Test that NotionClient defaults to disabled when NOTION_ENABLED not set"""
    # Ensure NOTION_ENABLED is not set
    if 'NOTION_ENABLED' in os.environ:
        del os.environ['NOTION_ENABLED']

    client = NotionClient()

    assert client.enabled == False
    assert client.api_key is None  # Should not load if disabled

def test_init_skips_api_key_when_disabled():
    """Test that API key is not loaded when NOTION_ENABLED=false"""
    os.environ['NOTION_ENABLED'] = 'false'
    os.environ['NOTION_API_KEY'] = 'should_not_load'

    client = NotionClient()

    assert client.enabled == False
    # API key might be set during env var processing, but is_available will return False

    del os.environ['NOTION_ENABLED']
    if 'NOTION_API_KEY' in os.environ:
        del os.environ['NOTION_API_KEY']
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_notion_client_env_vars.py -v
```

Expected: FAIL - new attributes don't exist yet

**Step 3: Implement new `__init__()` logic**

Replace the entire `__init__()` method in `core/notion_client.py` (around lines 12-18):

```python
def __init__(self):
    """Initialize NotionClient from environment variables only"""
    # Warn about obsolete config file
    config_path = Path(__file__).parent.parent / 'config' / 'notion_config.json'
    if config_path.exists():
        print("[Notion] ⚠️ WARNING: config/notion_config.json is no longer used")
        print("[Notion] ⚠️ Please use environment variables instead")
        print("[Notion] ⚠️ See docs/notion-migration-guide.md for help")

    # Load master switch
    self.enabled = os.environ.get('NOTION_ENABLED', 'false').lower() == 'true'

    if not self.enabled:
        self._log("Notion sync disabled (NOTION_ENABLED=false)")
        self.api_key = None
        self.debug = False
        self.dry_run = False
        self.delete_duplicates = True
        return  # Early return, skip other initialization

    # Only load these if enabled
    self.api_key = os.environ.get('NOTION_API_KEY')
    self.debug = os.environ.get('NOTION_DEBUG', 'false').lower() == 'true'
    self.dry_run = os.environ.get('NOTION_DRY_RUN', 'false').lower() == 'true'
    self.delete_duplicates = os.environ.get('NOTION_DELETE_DUPLICATES', 'true').lower() == 'true'

    # Validate API key if enabled
    if not self.api_key:
        print("[Notion] ⚠️ NOTION_ENABLED=true but NOTION_API_KEY not set")
        print("[Notion] ⚠️ Notion sync will be skipped")
```

**Step 4: Delete `_load_config()` method**

Delete the entire `_load_config()` method (around lines 19-43 in current file).

**Step 5: Remove `self.config` reference**

Search the file for `self.config` and remove those references (we'll update the usage sites in next tasks).

**Step 6: Run tests to verify they pass**

```bash
pytest tests/test_notion_client_env_vars.py -v
```

Expected: PASS

**Step 7: Run all NotionClient tests to check for breakage**

```bash
pytest tests/test_notion_client.py -v
```

Note: Some tests may fail - this is expected. We'll fix them in subsequent tasks.

**Step 8: Commit**

```bash
git add core/notion_client.py tests/test_notion_client_env_vars.py
git commit -m "refactor: load NotionClient settings from env vars only, remove config file"
```

---

## Task 4: Simplify `is_available()` Method

**Goal:** Simplify to only check `enabled` and `api_key`

**Files:**
- Modify: `core/notion_client.py:44-54` (the `is_available` method)

**Step 1: Write test for simplified is_available**

```python
# tests/test_notion_client_is_available.py
import os
import pytest
from core.notion_client import NotionClient

def test_is_available_returns_false_when_disabled():
    """Test that is_available returns False when NOTION_ENABLED=false"""
    os.environ['NOTION_ENABLED'] = 'false'

    client = NotionClient()
    result = client.is_available()

    assert result == False

    del os.environ['NOTION_ENABLED']

def test_is_available_returns_false_when_no_api_key():
    """Test that is_available returns False when enabled but no API key"""
    os.environ['NOTION_ENABLED'] = 'true'
    if 'NOTION_API_KEY' in os.environ:
        del os.environ['NOTION_API_KEY']

    client = NotionClient()
    result = client.is_available()

    assert result == False

    del os.environ['NOTION_ENABLED']

def test_is_available_returns_true_when_configured():
    """Test that is_available returns True when properly configured"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key_123'

    client = NotionClient()
    result = client.is_available()

    assert result == True

    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_notion_client_is_available.py -v
```

Expected: FAIL - current `is_available()` still checks `self.config`

**Step 3: Implement simplified `is_available()`**

Replace the `is_available()` method in `core/notion_client.py` (around line 44):

```python
def is_available(self) -> bool:
    """Check if Notion client is properly configured"""
    # Check master switch
    if not self.enabled:
        self._log("Notion sync disabled by NOTION_ENABLED")
        return False

    # Check API key
    if not self.api_key:
        self._log("NOTION_API_KEY not configured")
        return False

    return True
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_notion_client_is_available.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add core/notion_client.py tests/test_notion_client_is_available.py
git commit -m "refactor: simplify is_available() to check only enabled and api_key"
```

---

## Task 5: Simplify `_get_database_id()` Method

**Goal:** Only check environment variables, no config file fallback

**Files:**
- Modify: `core/notion_client.py:56-76` (the `_get_database_id` method)

**Step 1: Write test for _get_database_id**

```python
# tests/test_notion_client_database_id.py
import os
import pytest
from core.notion_client import NotionClient

def test_get_database_id_from_env_var():
    """Test that database ID is loaded from environment variable"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()

    # Set database ID for tech_insights
    os.environ['NOTION_DB_TECH_INSIGHTS'] = 'abc123def456'

    db_id = client._get_database_id('tech_insights')

    assert db_id == 'abc123def456'

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']
    del os.environ['NOTION_DB_TECH_INSIGHTS']

def test_get_database_id_returns_none_when_not_set():
    """Test that _get_database_id returns None when env var not set"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()

    # Ensure database ID is not set
    if 'NOTION_DB_TECH_INSIGHTS' in os.environ:
        del os.environ['NOTION_DB_TECH_INSIGHTS']

    db_id = client._get_database_id('tech_insights')

    assert db_id is None

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']

def test_get_database_id_task_id_case_conversion():
    """Test that task_id is correctly converted to env var name"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'

    client = NotionClient()

    # Set with underscores
    os.environ['NOTION_DB_TRENDING_AI'] = 'xyz789'

    # Query with underscores
    db_id = client._get_database_id('trending_ai')

    assert db_id == 'xyz789'

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']
    del os.environ['NOTION_DB_TRENDING_AI']
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_notion_client_database_id.py -v
```

Expected: FAIL - current method still checks config file

**Step 3: Implement simplified `_get_database_id()`**

Replace the `_get_database_id()` method in `core/notion_client.py` (around line 56):

```python
def _get_database_id(self, task_id: str) -> Optional[str]:
    """
    Get database ID for a task from environment variable.

    Args:
        task_id: Task identifier (e.g., 'tech_insights')

    Returns:
        Database ID string or None if not configured
    """
    # Check environment variable
    env_var_name = f'NOTION_DB_{task_id.upper()}'
    db_id = os.environ.get(env_var_name)

    if db_id:
        self._log(f"Using database ID from {env_var_name}")
        return db_id

    # Not found
    self._log(f"No database ID configured for {task_id} (NOTION_DB_{task_id.upper()})")
    return None
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_notion_client_database_id.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add core/notion_client.py tests/test_notion_client_database_id.py
git commit -m "refactor: simplify _get_database_id() to use env vars only"
```

---

## Task 6: Update `sync_markdown()` to Use `self.delete_duplicates`

**Goal:** Replace `self.config.get()` calls with `self.delete_duplicates`

**Files:**
- Modify: `core/notion_client.py:131-133` and `core/notion_client.py:243` (delete_duplicates usage)

**Step 1: Find all config.get() usages**

```bash
cd /Users/tinker.chen/work/code/learning/github/github-schedule
grep -n "self.config" core/notion_client.py
```

Expected: Lines 131, 243 (delete_duplicates checks)

**Step 2: Write test for delete_duplicates behavior**

```python
# tests/test_notion_client_delete_duplicates.py
import os
import pytest
from core.notion_client import NotionClient

def test_delete_duplicates_defaults_to_true():
    """Test that delete_duplicates defaults to True"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'

    # Don't set NOTION_DELETE_DUPLICATES
    if 'NOTION_DELETE_DUPLICATES' in os.environ:
        del os.environ['NOTION_DELETE_DUPLICATES']

    client = NotionClient()

    assert client.delete_duplicates == True

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']

def test_delete_duplicates_can_be_disabled():
    """Test that delete_duplicates can be set to False"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_DELETE_DUPLICATES'] = 'false'

    client = NotionClient()

    assert client.delete_duplicates == False

    # Cleanup
    del os.environ['NOTION_ENABLED']
    del os.environ['NOTION_API_KEY']
    del os.environ['NOTION_DELETE_DUPLICATES']
```

**Step 3: Run tests to verify they pass**

```bash
pytest tests/test_notion_client_delete_duplicates.py -v
```

Expected: PASS (we already set this in `__init__`)

**Step 4: Replace config.get() calls in sync_markdown()**

In `core/notion_client.py`, around line 131, replace:
```python
# Old code:
if self.config.get('settings', {}).get('delete_duplicates', True):
    self._find_and_delete_existing(database_id, date)

# New code:
if self.delete_duplicates:
    self._find_and_delete_existing(database_id, date)
```

And around line 243, replace:
```python
# Old code:
if self.config.get('settings', {}).get('delete_duplicates', True):
    self._find_and_delete_in_published_markdown(data_source_id, date)

# New code:
if self.delete_duplicates:
    self._find_and_delete_in_published_markdown(data_source_id, date)
```

**Step 5: Run all NotionClient tests**

```bash
pytest tests/test_notion_client*.py -v
```

Expected: Most tests pass

**Step 6: Commit**

```bash
git add core/notion_client.py
git commit -m "refactor: use self.delete_duplicates instead of self.config.get()"
```

---

## Task 7: Integration Test - Notion Disabled

**Goal:** Verify that all tasks run successfully when Notion is disabled

**Files:**
- Test: `tests/integration/test_notion_disabled.py`
- Run: `main.py`

**Step 1: Write integration test**

```python
# tests/integration/test_notion_disabled.py
"""Integration test: Verify tasks work when Notion is disabled"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_tasks_run_with_notion_disabled():
    """Test that all tasks complete successfully when Notion is disabled"""
    # Ensure Notion is disabled
    os.environ['NOTION_ENABLED'] = 'false'

    # Remove API key to ensure it's not used
    if 'NOTION_API_KEY' in os.environ:
        del os.environ['NOTION_API_KEY']

    # Import and run main
    from main import main

    exit_code = main()

    # Should succeed (tasks run, Notion is skipped)
    assert exit_code == 0

    # Cleanup
    del os.environ['NOTION_ENABLED']

if __name__ == '__main__':
    test_tasks_run_with_notion_disabled()
    print("✓ Integration test passed: Tasks run successfully with Notion disabled")
```

**Step 2: Run integration test**

```bash
python tests/integration/test_notion_disabled.py
```

Expected: Tasks run, Notion sync is skipped, exit code is 0

**Step 3: Verify output contains expected messages**

Look for: `"Notion 未配置，跳过同步"` or similar Notion skip messages

**Step 4: Commit**

```bash
git add tests/integration/test_notion_disabled.py
git commit -m "test: add integration test for Notion disabled scenario"
```

---

## Task 8: Integration Test - Notion Enabled But Missing Config

**Goal:** Verify graceful degradation when Notion enabled but missing API key

**Files:**
- Test: `tests/integration/test_notion_missing_config.py`

**Step 1: Write test**

```python
# tests/integration/test_notion_missing_config.py
"""Integration test: Verify graceful handling when Notion enabled but missing config"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_graceful_skip_when_missing_api_key():
    """Test that tasks gracefully skip Notion when API key is missing"""
    # Enable Notion but don't set API key
    os.environ['NOTION_ENABLED'] = 'true'

    # Ensure API key is NOT set
    if 'NOTION_API_KEY' in os.environ:
        del os.environ['NOTION_API_KEY']

    from main import main

    exit_code = main()

    # Should still succeed (tasks run, Notion is gracefully skipped)
    assert exit_code == 0

    # Cleanup
    del os.environ['NOTION_ENABLED']

if __name__ == '__main__':
    test_graceful_skip_when_missing_api_key()
    print("✓ Integration test passed: Graceful skip when API key missing")
```

**Step 2: Run test**

```bash
python tests/integration/test_notion_missing_config.py
```

Expected: Tasks succeed, Notion sync skipped with warning

**Step 3: Commit**

```bash
git add tests/integration/test_notion_missing_config.py
git commit -m "test: add integration test for missing Notion config"
```

---

## Task 9: Update `.env.example` with New Structure

**Goal:** Document the new environment variable structure

**Files:**
- Modify: `.env.example:21-36` (Notion section)

**Step 1: Read current .env.example**

```bash
cat .env.example
```

**Step 2: Update Notion section**

Replace the Notion section with:

```bash
# Notion Integration (optional)
# Set to true to enable Notion sync
NOTION_ENABLED=false

# Required when NOTION_ENABLED=true
# Get your API key from: https://www.notion.so/my-integrations
NOTION_API_KEY=your_notion_api_key_here

# Database IDs for each task that syncs to Notion
# Extract from your Notion database URL: https://notion.so/workspace/[DATABASE_ID]?v=...
NOTION_DB_TECH_INSIGHTS=your_32_char_database_id_here
NOTION_DB_TRENDING_AI=your_32_char_database_id_here

# Optional: Add ai_news sync to Notion
# NOTION_DB_AI_NEWS=your_32_char_database_id_here

# Optional settings
NOTION_DRY_RUN=false  # Set to true to test without actual API calls
NOTION_DEBUG=false    # Set to true for verbose logging
NOTION_DELETE_DUPLICATES=true  # Delete existing entries for same date before syncing
```

**Step 3: Verify changes**

```bash
git diff .env.example
```

**Step 4: Commit**

```bash
git add .env.example
git commit -m "docs: update .env.example with new Notion env var structure"
```

---

## Task 10: Delete Obsolete Config Files

**Goal:** Remove old config file and example

**Files:**
- Delete: `config/notion_config.json`
- Delete: `config/notion_config.json.example` (if exists)

**Step 1: Check if files exist**

```bash
ls -la config/notion_config.json*
```

**Step 2: Delete files**

```bash
rm config/notion_config.json
rm -f config/notion_config.json.example
```

**Step 3: Verify deletion**

```bash
git status
```

Should show deletions

**Step 4: Commit**

```bash
git add config/
git commit -m "refactor: remove obsolete config/notion_config.json files"
```

---

## Task 11: Create Migration Guide

**Goal:** Help existing users migrate from config file to env vars

**Files:**
- Create: `docs/notion-migration-guide.md`

**Step 1: Write migration guide**

```markdown
# Notion Configuration Migration Guide

## Overview

We've simplified Notion integration to use **environment variables only**, removing the `config/notion_config.json` file. This guide helps you migrate.

## Why This Change?

The old system had config in two places:
- `config/notion_config.json` file
- Environment variables (`NOTION_API_KEY`, etc.)

This was confusing and hard to manage. Now **everything is in environment variables**.

## Before (Old Config)

### Old file structure:
```
config/
└── notion_config.json
```

### Old `config/notion_config.json`:
```json
{
  "databases": {
    "tech_insights": "30943ad321af80d3a5e7d6c17ce3a93a",
    "trending_ai": "another_32_char_id_here"
  },
  "settings": {
    "enabled": true,
    "delete_duplicates": true
  }
}
```

## After (New Env Vars)

### New `.env` file:
```bash
# Master switch
NOTION_ENABLED=true

# API credentials
NOTION_API_KEY=ntn_your_api_key_here

# Database IDs (one per task)
NOTION_DB_TECH_INSIGHTS=30943ad321af80d3a5e7d6c17ce3a93a
NOTION_DB_TRENDING_AI=another_32_char_id_here

# Optional settings
NOTION_DELETE_DUPLICATES=true
NOTION_DRY_RUN=false
NOTION_DEBUG=false
```

## Migration Steps

### Step 1: Open your old config file

```bash
cat config/notion_config.json
```

### Step 2: Copy values to .env

For each database ID in your old config:

```json
{
  "databases": {
    "tech_insights": "30943ad321af80d3a5e7d6c17ce3a93a"  // Copy this
  }
}
```

Add to your `.env`:

```bash
NOTION_DB_TECH_INSIGHTS=30943ad321af80d3a5e7d6c17ce3a93a
```

### Step 3: Set master switch

If you want to continue using Notion:

```bash
NOTION_ENABLED=true
```

If you want to disable Notion:

```bash
NOTION_ENABLED=false
```

### Step 4: Migrate settings

Old setting | New env var
-----------|------------
`settings.enabled: true` | `NOTION_ENABLED=true`
`settings.delete_duplicates: true` | `NOTION_DELETE_DUPLICATES=true`

### Step 5: Test before deploying

Enable dry-run mode first:

```bash
# .env
NOTION_ENABLED=true
NOTION_DRY_RUN=true
```

Run the script:

```bash
python main.py
```

You should see: `[Notion] DRY RUN: Would sync...`

### Step 6: Delete old config file

Once everything works:

```bash
rm config/notion_config.json
```

### Step 7: Commit your changes

```bash
git add .env
git commit -m "chore: migrate Notion config to env vars"
```

## How to Get Database IDs

If you don't have a config file to migrate from, here's how to find your database IDs:

1. Open your Notion database
2. Look at the URL in your browser
3. Find the 32-character ID after `/workspace/` and before `?`

Example URL:
```
https://notion.so/workspace/30943ad321af80d3a5e7d6c17ce3a93a?v=...
```

The database ID is: `30943ad321af80d3a5e7d6c17ce3a93a`

## Environment Variable Reference

### Required (when NOTION_ENABLED=true)

| Variable | Description | Example |
|----------|-------------|---------|
| `NOTION_ENABLED` | Master switch to enable/disable Notion | `true` or `false` |
| `NOTION_API_KEY` | Your Notion Integration token | `ntn_1816...` |
| `NOTION_DB_TECH_INSIGHTS` | Database ID for tech_insights task | 32-char string |
| `NOTION_DB_TRENDING_AI` | Database ID for trending_ai task | 32-char string |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `NOTION_DELETE_DUPLICATES` | Delete existing entries for same date | `true` |
| `NOTION_DRY_RUN` | Test without actual API calls | `false` |
| `NOTION_DEBUG` | Verbose logging | `false` |
| `NOTION_DB_AI_NEWS` | Database ID for ai_news task (not used currently) | - |

## Troubleshooting

### Problem: "config/notion_config.json is no longer used"

**Solution:** Delete the old config file and migrate to env vars (see steps above).

### Problem: "NOTION_ENABLED=true but NOTION_API_KEY not set"

**Solution:** Add your API key to `.env`:
```bash
NOTION_API_KEY=ntn_your_actual_key_here
```

### Problem: "No database ID configured for tech_insights"

**Solution:** Add the database ID to `.env`:
```bash
NOTION_DB_TECH_INSIGHTS=your_32_char_database_id
```

### Problem: I don't know my database IDs

**Solution:** See "How to Get Database IDs" section above.

## Need Help?

If you encounter issues:

1. Check your `.env` file has all required variables
2. Enable debug mode: `NOTION_DEBUG=true`
3. Try dry-run mode: `NOTION_DRY_RUN=true`
4. Check the logs for specific error messages

## Benefits of New System

✅ Single source of truth (only env vars)
✅ Works great with Docker/GitHub Actions
✅ Clearer separation of config
✅ Easier to understand and maintain
✅ Default to disabled (opt-in via NOTION_ENABLED)
```

**Step 2: Commit migration guide**

```bash
git add docs/notion-migration-guide.md
git commit -m "docs: add Notion configuration migration guide"
```

---

## Task 12: Update README.md

**Goal:** Remove references to config file, update Notion setup section

**Files:**
- Modify: `README.md`

**Step 1: Find Notion sections in README**

```bash
grep -n -i "notion" README.md
```

**Step 2: Update Notion configuration section**

Find the section that mentions `config/notion_config.json` and replace with env var documentation.

Example replacement:

```markdown
## Notion Integration (Optional)

This project can sync AI-generated content to Notion databases.

### Setup

1. Create a Notion Integration at https://www.notion.so/my-integrations
2. Copy your Integration Token (Internal Integration Token)
3. Create databases in Notion for each task you want to sync
4. Add your Integration to each database (click "..." → "Add connections")
5. Configure environment variables in your `.env` file:

```bash
# Enable Notion sync
NOTION_ENABLED=true

# Your Notion Integration credentials
NOTION_API_KEY=ntn_your_token_here

# Database IDs (from your Notion database URLs)
NOTION_DB_TECH_INSIGHTS=32_char_id_here
NOTION_DB_TRENDING_AI=32_char_id_here
```

### Getting Database IDs

1. Open your Notion database
2. Copy the 32-character ID from the URL: `notion.so/workspace/[DATABASE_ID]?v=...`

### Test Configuration

```bash
# Dry run (no API calls)
NOTION_DRY_RUN=true python main.py

# Real sync
python main.py
```
```

**Step 3: Verify changes**

```bash
git diff README.md
```

**Step 4: Commit**

```bash
git add README.md
git commit -m "docs: update README with new Notion env var configuration"
```

---

## Task 13: Update GitHub Actions Documentation

**Goal:** Show that secrets are now the only config needed

**Files:**
- Check: `.github/workflows/daily-automation.yml`
- Update if needed: `docs/github-secrets-instructions.md`

**Step 1: Check current workflow**

```bash
cat .github/workflows/daily-automation.yml
```

**Step 2: Verify workflow uses env vars**

The workflow should already pass secrets as env vars. Verify it looks correct.

**Step 3: Update GitHub secrets docs if needed**

If there's documentation about GitHub secrets, update it to show:

```yaml
env:
  NOTION_ENABLED: ${{ secrets.NOTION_ENABLED }}
  NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
  NOTION_DB_TECH_INSIGHTS: ${{ secrets.NOTION_DB_TECH_INSIGHTS }}
  NOTION_DB_TRENDING_AI: ${{ secrets.NOTION_DB_TRENDING_AI }}
```

**Step 4: Commit if changes made**

```bash
git add .github/workflows/ docs/
git commit -m "docs: update GitHub Actions documentation for Notion env vars"
```

---

## Task 14: Final Integration Test

**Goal:** Verify complete system works end-to-end

**Files:**
- Run: `main.py`
- Test: Manual verification

**Step 1: Test with Notion disabled**

```bash
# .env: NOTION_ENABLED=false
python main.py
```

Expected: All tasks run, no Notion sync attempts

**Step 2: Test with Notion enabled (dry run)**

```bash
# .env:
# NOTION_ENABLED=true
# NOTION_API_KEY=test
# NOTION_DB_TECH_INSIGHTS=test123
# NOTION_DRY_RUN=true

python main.py
```

Expected: Dry run messages, no actual API calls

**Step 3: Test with real Notion credentials (if available)**

```bash
# .env:
# NOTION_ENABLED=true
# NOTION_API_KEY=your_real_key
# NOTION_DB_TECH_INSIGHTS=your_real_db_id
# NOTION_DRY_RUN=false

python main.py
```

Expected: Successful sync to Notion

**Step 4: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests pass

**Step 5: Create summary test file**

```python
# tests/integration/test_complete_notion_refactor.py
"""Final integration test to verify Notion refactor is complete"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_notion_disabled():
    """Test system works with Notion disabled"""
    os.environ['NOTION_ENABLED'] = 'false'
    from main import main
    assert main() == 0
    del os.environ['NOTION_ENABLED']
    print("✓ Notion disabled: PASS")

def test_notion_enabled_dry_run():
    """Test system works with Notion enabled in dry-run mode"""
    os.environ['NOTION_ENABLED'] = 'true'
    os.environ['NOTION_API_KEY'] = 'test_key'
    os.environ['NOTION_DB_TECH_INSIGHTS'] = 'test_db_id'
    os.environ['NOTION_DRY_RUN'] = 'true'

    from main import main
    assert main() == 0

    # Cleanup
    for key in ['NOTION_ENABLED', 'NOTION_API_KEY', 'NOTION_DB_TECH_INSIGHTS', 'NOTION_DRY_RUN']:
        if key in os.environ:
            del os.environ[key]

    print("✓ Notion enabled dry-run: PASS")

if __name__ == '__main__':
    test_notion_disabled()
    test_notion_enabled_dry_run()
    print("\n✓ All integration tests passed!")
```

**Step 6: Run final integration test**

```bash
python tests/integration/test_complete_notion_refactor.py
```

**Step 7: Commit**

```bash
git add tests/integration/test_complete_notion_refactor.py
git commit -m "test: add final integration test for Notion refactor"
```

---

## Task 15: Cleanup and Final Verification

**Goal:** Clean up test files, verify git history

**Files:**
- Cleanup: Temporary test files
- Verify: Git log

**Step 1: Review all commits**

```bash
git log --oneline --graph
```

Should see clean progression of commits

**Step 2: Check for any remaining references to config file**

```bash
grep -r "notion_config.json" --include="*.py" --include="*.md" .
```

Expected: Only in migration guide (as example)

**Step 3: Remove temporary test files if desired**

```bash
# Remove baseline documentation test
rm tests/test_notion_client_current_behavior.py
```

**Step 4: Final git status**

```bash
git status
```

Should be clean (no uncommitted changes)

**Step 5: Create summary commit if needed**

```bash
git add .
git commit -m "chore: cleanup temporary test files after Notion refactor"
```

---

## Verification Checklist

Before considering this complete, verify:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Main script runs with Notion disabled: `python main.py`
- [ ] Main script runs with Notion dry-run: `NOTION_DRY_RUN=true python main.py`
- [ ] No references to `config/notion_config.json` in code (except migration guide)
- [ ] `.env.example` updated with new structure
- [ ] `README.md` updated
- [ ] Migration guide created
- [ ] GitHub Actions docs updated (if applicable)
- [ ] Git history shows clean progression

---

## Success Criteria

You'll know this is complete when:

1. ✅ Notion sync is disabled by default (`NOTION_ENABLED=false`)
2. ✅ All configuration via environment variables
3. ✅ No `config/notion_config.json` file
4. ✅ Clear warnings if old config file exists
5. ✅ Graceful degradation when missing config
6. ✅ All existing tasks work without modification
7. ✅ Comprehensive migration guide for existing users
8. ✅ All tests pass

---

**Implementation plan complete!** Ready to execute.

**Next:** Choose execution approach (subagent-driven in this session, or parallel session with executing-plans skill).
