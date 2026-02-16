# Notion Integration Design

**Date:** 2026-02-16
**Author:** Design Document
**Status:** Approved

## Overview

Integrate Notion as a storage destination for AI-generated markdown content, enabling mobile access to daily tech insights, GitHub trending analysis, and other AI-generated reports.

## Goals

1. **Immediate Sync:** Sync content to Notion immediately after each AI task generates markdown
2. **Task-level Control:** Each task independently syncs its own content
3. **Duplicate Handling:** Delete old entries and create new ones (ensure only latest version exists)
4. **Graceful Degradation:** Task succeeds even if Notion sync fails
5. **Flexible Configuration:** Support both config file and environment variables

## Architecture

### Approach: Task-level Sync with Shared Client

Each AI task calls a shared `NotionClient` utility to sync its markdown content after generating the output file.

```
┌─────────────────────────────────────────────────────────────┐
│                     Task Execution                          │
│  ┌────────────────┐      ┌─────────────────┐               │
│  │ AI Task        │──────│ Markdown File   │               │
│  │ (tech_insights)│      │ output/...md    │               │
│  └────────────────┘      └─────────────────┘               │
│          │                                                     │
│          ▼                                                     │
│  ┌────────────────┐                                           │
│  │ NotionClient   │                                           │
│  │ .sync_markdown │                                           │
│  └────────┬───────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Notion API                                             │  │
│  │  1. Query by date                                       │  │
│  │  2. Delete existing                                     │  │
│  │  3. Create new page with markdown content               │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Shared NotionClient (`core/notion_client.py`)

**Responsibilities:**
- Handle Notion API authentication
- Provide `sync_markdown()` method for tasks
- Manage database ID mappings
- Handle duplicate deletion
- Error handling and retries

**Key Methods:**
```python
class NotionClient:
    def __init__(self):
        # Load config from file and env vars
        # Validate API key

    def is_available(self) -> bool:
        # Check if properly configured

    def sync_markdown(self, task_id: str, markdown_content: str, date: str) -> bool:
        # Main sync method
        # 1. Get database ID for task_id
        # 2. Delete existing entry for date
        # 3. Create new entry with markdown

    def _get_database_id(self, task_id: str) -> Optional[str]:
        # Priority: env var > config file > None

    def _find_and_delete_existing(self, database_id: str, date: str):
        # Query database for matching date
        # Delete all matching pages

    def _create_new_entry(self, database_id: str, markdown_content: str, date: str):
        # Create new page with title (date) and content (markdown)
```

**Error Handling:**
- Never raise exceptions (return bool success)
- Log clear error messages
- Retry on rate limit errors (wait 60s)
- Graceful degradation if Notion unavailable

### 2. Configuration

**Config File** (`config/notion_config.json`):
```json
{
  "databases": {
    "tech_insights": "database-id-1",
    "trending_ai": "database-id-2",
    "ai_news": "database-id-3"
  },
  "settings": {
    "enabled": true,
    "delete_duplicates": true
  }
}
```

**Environment Variables** (`.env`):
```bash
# Required
NOTION_API_KEY=secret_xxx

# Optional overrides
NOTION_DB_TECH_INSIGHTS=database-id-1
NOTION_DB_TRENDING_AI=database-id-2

# Optional settings
NOTION_DRY_RUN=true
NOTION_DEBUG=true
```

**Priority:** Environment variables > Config file > Defaults

### 3. Notion Database Schema

Each content type has its own Notion database:

**Properties:**
- `Title` (title) - Date string: "2026-02-16"
- `Date` (date) - Actual date: 2026-02-16
- `Content` (rich text) - Full markdown content (in page body, not property)
- `Synced At` (created_time) - Auto timestamp
- `Source` (select) - "github-schedule"

**Note:** Markdown content is stored in the page body, not a property, to allow full formatting.

### 4. Task Integration Pattern

Each AI task integrates sync at end of `execute()`:

```python
# tasks/tech_insights.py

from core.notion_client import NotionClient

class TechInsightsTask(Task):
    TASK_ID = "tech_insights"
    PRIORITY = 40

    def execute(self) -> bool:
        try:
            # ... existing code to generate markdown ...

            # Save markdown file (existing)
            output_path = self.get_output_path(f"tech-insights/{self.get_today()}.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(insights)

            # NEW: Sync to Notion
            client = NotionClient()
            if client.is_available():
                success = client.sync_markdown(
                    task_id=self.TASK_ID,
                    markdown_content=insights,
                    date=self.get_today()
                )
                if success:
                    print(f"[{self.TASK_ID}] ✓ Synced to Notion")
                else:
                    print(f"[{self.TASK_ID}] ⚠️ Notion sync failed")
            else:
                print(f"[{self.TASK_ID}] ⚠️ Notion not configured, skipping")

            return True  # Task succeeds even if Notion fails

        except Exception as e:
            print(f"[{self.TASK_ID}] ✗ Error: {str(e)}")
            return False
```

**Key points:**
- Sync happens immediately after file save
- Task returns `True` even if Notion sync fails
- Clear logging for debugging
- Notion sync is optional (graceful skip if not configured)

## Implementation Tasks

### Phase 1: Core Infrastructure
1. Create `core/notion_client.py` - Shared Notion API client
2. Create `config/notion_config.json.example` - Database ID mappings template
3. Add `notion-client` to `requirements.txt`
4. Add Notion environment variables to `.env.example`

### Phase 2: Task Integration
5. Modify `tasks/tech_insights.py` - Add Notion sync
6. Modify `tasks/trending_ai.py` - Add Notion sync
7. Modify `tasks/ai_news.py` - Add Notion sync (if applicable)

### Phase 3: Testing & Documentation
8. Create `tests/test_notion_client.py` - Unit tests
9. Create standalone test script `tests/manual_notion_test.py`
10. Update `README.md` with Notion setup instructions
11. Create `docs/notion-setup-guide.md` - Detailed setup guide

### Phase 4: GitHub Actions Integration
12. Add `NOTION_API_KEY` to GitHub repository secrets
13. Update `.github/workflows/blank.yml` to support Notion sync

## Testing Strategy

### Unit Tests
- Mock Notion API responses
- Test config file parsing
- Test environment variable fallback
- Test error scenarios (missing config, API failures)

### Integration Tests
- Create test databases in Notion
- Run actual sync operations
- Verify duplicate deletion
- Test markdown rendering

### Manual Testing
```bash
# Standalone test
python -m core.notion_client --task tech_insights --dry-run

# Test with actual sync
python -m core.notion_client --task tech_insights --date 2026-02-16

# Run full pipeline
python main.py
```

## Dependencies

```txt
# requirements.txt
notion-client>=2.2.1
```

## Security Considerations

1. **API Key Storage:**
   - Never commit `NOTION_API_KEY` to git
   - Use GitHub Actions secrets for CI/CD
   - Document `.env` file in `.gitignore`

2. **Database IDs:**
   - Database IDs are not sensitive (can be in config)
   - Environment variables allow per-environment overrides

3. **Rate Limiting:**
   - Notion API: ~3 requests/second
   - Implement retry with backoff for rate limits
   - Batch requests if syncing multiple tasks

## Future Enhancements

1. **Sync Status Tracking:** Add property to track sync success/failure
2. **Image Support:** Handle embedded images in markdown
3. **Backfill:** Script to sync historical data
4. **Bi-directional Sync:** Update markdown if Notion page is edited
5. **Multiple Workspaces:** Support multiple Notion workspaces

## Success Criteria

- ✅ All AI-generated markdown content syncs to Notion
- ✅ Duplicate entries are properly deleted
- ✅ Tasks succeed even if Notion sync fails
- ✅ Configuration via both file and environment variables
- ✅ Clear error logging for debugging
- ✅ Works in GitHub Actions environment
