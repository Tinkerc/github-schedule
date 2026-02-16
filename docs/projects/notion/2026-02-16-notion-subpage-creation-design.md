# Notion Sub-Page Creation Design

**Date:** 2026-02-16
**Author:** Claude
**Status:** Approved

## Overview

Extend the Notion integration to support creating sub-pages under parent pages, as an alternative to creating database entries. This allows better organization of daily content in a page hierarchy.

## Requirements

Create a sub-page sync mode that:
- Creates daily pages as children of a designated parent page
- Replaces old daily pages (delete_duplicates behavior)
- Supports specific tasks: `tech_insights`, `trending_ai`, `ai_news`
- Each task has its own parent page
- Page title = date (e.g., "2026-02-16")

## Design

### 1. Configuration Structure

**File:** `config/notion_config.json`

```json
{
  "databases": {
    "some_other_task": "database-id-here"
  },
  "parent_pages": {
    "tech_insights": "parent-page-id-123",
    "trending_ai": "parent-page-id-456",
    "ai_news": "parent-page-id-789"
  },
  "settings": {
    "enabled": true,
    "delete_duplicates": true
  }
}
```

**Priority lookup:**
1. Check `parent_pages[task_id]` first
2. Fall back to `databases[task_id]` if not found
3. Sync fails if neither is configured

### 2. NotionClient Changes

**File:** `core/notion_client.py`

**New Methods:**

```python
def _get_parent_page_id(self, task_id: str) -> Optional[str]:
    """
    Get parent page ID for a task.
    Priority: Config file > Environment variable > None
    """
    # Check config file
    config_page_id = self.config.get('parent_pages', {}).get(task_id)
    if config_page_id:
        return config_page_id

    # Check environment variable
    env_var_name = f'NOTION_PAGE_{task_id.upper()}'
    env_page_id = os.environ.get(env_var_name)
    if env_page_id:
        return env_page_id

    return None

def _delete_existing_sub_pages(self, parent_page_id: str, date: str):
    """
    Find and delete existing child pages with matching date title.
    Uses search API to find child pages.
    """

def _create_sub_page(self, parent_page_id: str, markdown_content: str, date: str):
    """
    Create a new page under a parent page.
    Page title = date, content = markdown_content as children blocks.
    """
```

**Modified Method:**

```python
def sync_markdown(self, task_id: str, markdown_content: str, date: str) -> bool:
    """
    Extended to support both database and sub-page modes.
    Flow:
    1. Check parent_page_id first
    2. If found → sub-page mode (delete + create)
    3. Else → existing database mode
    """
```

### 3. Page Creation Flow

```
sync_markdown(task_id, content, date)
  ↓
1. _get_parent_page_id(task_id)
   - Check config["parent_pages"][task_id]
   - Check env var NOTION_PAGE_{TASK_ID}
   - Return page_id or None
   ↓
2. If parent_page_id exists:
   a. _delete_existing_sub_pages(parent_page_id, date)
      - Search child pages of parent
      - Find pages where title == date
      - Archive all matches
   ↓
   b. _create_sub_page(parent_page_id, content, date)
      - Create page with parent={"page_id": parent_page_id}
      - Set title property = date
      - Add content as children blocks
      - Print success message
   ↓
3. Else fall back to database mode (existing logic)
```

**Key behaviors:**
- Atomic operation: delete first, then create
- If delete fails but create succeeds → sync still succeeds
- If create fails → old content preserved (can be deleted next run)
- Dry run mode supported (prints what would happen)

### 4. Error Handling

**Error scenarios:**

1. **Parent page not found or inaccessible**
   - Catch APIResponseError
   - Log error with page_id
   - Return False (sync failure)
   - Don't fall back to database mode

2. **Too many child pages**
   - Use pagination or filter by date
   - Log warning if pagination needed

3. **Page creation fails after delete**
   - Old content already deleted
   - Log error prominently
   - Return False
   - Next run will retry

4. **Dry run mode**
   - Skip all API calls
   - Print intended operations

**Consistent behaviors:**
- All errors caught and logged with `[Notion]` prefix
- Return True/False for success/failure
- Never raise exceptions (handled internally)

### 5. Testing Strategy

**Unit Tests** (`tests/test_notion_client.py`)
- Test `_get_parent_page_id()` priority lookup
- Mock NotionAPI responses
- Test error handling
- Test dry run mode

**Integration Test** (extend `tests/manual_notion_test.py`)
- Create test parent page
- Run actual sync
- Verify page creation and deletion
- Cleanup test pages

**Manual Test Script** (`scripts/test_sub_page_creation.py`)
- Load config and validate
- Dry run test
- Real run with confirmation
- Verification checklist

**Config Validation** (extend `scripts/verify_notion_config.py`)
- Validate parent_page_ids
- Check parent pages accessible
- Report mode per task (database vs page)

### 6. Migration Path

**Phase 1: Deploy Code Changes**
- Deploy NotionClient with sub-page support
- Config unchanged (only databases)
- Verify no regressions

**Phase 2: Add Parent Pages**
- Add `"parent_pages"` section to config
- Configure ONE task first (tech_insights)
- Deploy config

**Phase 3: Verify First Task**
- Run GitHub Actions
- Check sub-page creation in Notion UI
- Monitor for a few days

**Phase 4: Migrate Remaining Tasks**
- Add `trending_ai` to parent_pages
- Add `ai_news` to parent_pages
- Verify each

**Phase 5: Cleanup (Optional)**
- Manually delete old database entries
- Remove migrated tasks from databases config
- Keep delete_duplicates enabled

**Rollback:**
- Remove task from `parent_pages` config
- Task automatically falls back to database mode
- No code changes needed

## Implementation Notes

- No changes required to task code (tech_insights.py, trending_ai.py, ai_news.py)
- Tasks continue calling `notion_client.sync_markdown(task_id, content, date)`
- Mode selection is transparent to tasks
- Backward compatible with existing database mode
- Environment variables supported: `NOTION_PAGE_TECH_INSIGHTS`, etc.

## Success Criteria

- [ ] Tasks can create sub-pages under parent pages
- [ ] Old daily pages are deleted before creating new ones
- [ ] Config can specify database vs page mode per task
- [ ] Existing database mode continues to work
- [ ] Error handling is robust
- [ ] Dry run mode works
- [ ] Tests validate functionality
- [ ] Migration completes without data loss
