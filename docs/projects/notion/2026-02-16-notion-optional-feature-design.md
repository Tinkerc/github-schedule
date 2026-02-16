# Notion as Optional Feature - Design Document

**Date:** 2026-02-16
**Status:** Approved
**Approach:** Pure Environment Variables (Approach 2)

## Overview

Simplify Notion integration to use pure environment variables with a single master switch, removing the config file completely. This makes Notion truly optional - when disabled, no Notion code runs.

## Problem Statement

The current Notion integration has configuration complexity:
- Multiple config locations: `config/notion_config.json` + environment variables
- Complex `is_available()` logic checking multiple sources
- Unclear single source of truth
- Harder to use with Docker/GitHub Actions

## Solution: Pure Environment Variables

### Configuration Structure

All configuration via environment variables:

```bash
# Master switch (required, default: false)
NOTION_ENABLED=false              # Set to true to enable Notion sync

# Required when NOTION_ENABLED=true
NOTION_API_KEY=ntn_your_key_here  # Your Notion Integration API key

# Required for each task that syncs to Notion
NOTION_DB_TECH_INSIGHTS=32_char_id_here
NOTION_DB_TRENDING_AI=32_char_id_here
NOTION_DB_AI_NEWS=32_char_id_here   # Optional (if you want ai_news sync)

# Optional settings
NOTION_DRY_RUN=false               # Test mode without actual API calls
NOTION_DEBUG=false                 # Verbose logging
NOTION_DELETE_DUPLICATES=true      # Delete existing entries for same date
```

## Architecture Changes

### 1. `core/notion_client.py` Refactoring

#### Remove
- `_load_config()` method entirely
- `self.config` attribute
- Config file loading logic

#### Simplified `__init__()`

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

#### Simplified `is_available()`

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

#### Simplified `_get_database_id()`

```python
def _get_database_id(self, task_id: str) -> Optional[str]:
    """Get database ID from environment variable"""
    env_var_name = f'NOTION_DB_{task_id.upper()}'
    db_id = os.environ.get(env_var_name)

    if db_id:
        self._log(f"Using database ID from {env_var_name}")
        return db_id

    self._log(f"No database ID configured for {task_id} (NOTION_DB_{task_id.upper()})")
    return None
```

#### Update `sync_markdown()`

Replace `self.config.get('settings', {}).get('delete_duplicates', True)` with `self.delete_duplicates`.

### 2. Task Files

**No changes needed!** ✅

Existing tasks (`trending_ai.py`, `tech_insights.py`) already:
- Create `NotionClient()` instance
- Call `is_available()` before attempting sync
- Handle graceful degradation when Notion is unavailable

The simplified `is_available()` will work perfectly with existing code.

### 3. Delete Obsolete Files

- `config/notion_config.json`
- `config/notion_config.json.example`

### 4. Documentation Updates

#### `.env.example`

```bash
# Notion Integration (optional)
# Set to true to enable Notion sync
NOTION_ENABLED=false

# Required when NOTION_ENABLED=true
NOTION_API_KEY=your_notion_api_key_here
NOTION_DB_TECH_INSIGHTS=your_32_char_database_id_here
NOTION_DB_TRENDING_AI=your_32_char_database_id_here

# Optional: Add ai_news sync to Notion
# NOTION_DB_AI_NEWS=your_32_char_database_id_here

# Optional settings
NOTION_DRY_RUN=false
NOTION_DEBUG=false
NOTION_DELETE_DUPLICATES=true
```

#### `docs/notion-migration-guide.md` (NEW)

Explain migration from config file to env vars:
- Why we made this change (simplicity)
- Before/after comparison
- Step-by-step migration instructions
- How to get database IDs from Notion URLs

#### `README.md`

- Remove references to `config/notion_config.json`
- Update Notion setup section to use env vars only
- Simplify the "Configuration" section

#### GitHub Actions docs

- Show that secrets are now the only config needed
- Update workflow example if needed

## Migration Strategy

### Breaking Changes

This is a **breaking change** for existing users.

### Before (Old Config)

```json
// config/notion_config.json
{
  "databases": {
    "tech_insights": "30943ad321af80d3a5e7d6c17ce3a93a",
    "trending_ai": "another_id_here"
  },
  "settings": {
    "enabled": true,
    "delete_duplicates": true
  }
}
```

### After (New Env Vars)

```bash
# .env
NOTION_ENABLED=true
NOTION_API_KEY=ntn_your_key_here
NOTION_DB_TECH_INSIGHTS=30943ad321af80d3a5e7d6c17ce3a93a
NOTION_DB_TRENDING_AI=another_id_here
NOTION_DELETE_DUPLICATES=true
```

### Migration Steps

1. Open your `config/notion_config.json`
2. Copy each database ID to corresponding environment variable
3. Set `NOTION_ENABLED=true` if you want to continue using Notion
4. Delete `config/notion_config.json`
5. Test with `NOTION_DRY_RUN=true` first

## Error Handling

### Startup Validation

When `NotionClient()` is instantiated:
- Warn if obsolete config file exists
- Validate API key when enabled
- Clear error messages for missing configuration

### Missing Configuration Examples

**Notion disabled (default):**
```
[Notion] Notion sync disabled (NOTION_ENABLED=false)
```

**Enabled but missing API key:**
```
[Notion] ⚠️ NOTION_ENABLED=true but NOTION_API_KEY not set
[Notion] ⚠️ Notion sync will be skipped
```

**Missing database ID:**
```
[Notion] ⚠️ No database ID for trending_ai
[Notion] ⚠️ Set NOTION_DB_TRENDING_AI to enable sync
```

**Old config file detected:**
```
[Notion] ⚠️ WARNING: config/notion_config.json is no longer used
[Notion] ⚠️ Please use environment variables instead
[Notion] ⚠️ See docs/notion-migration-guide.md for help
```

## Testing Plan

### Test 1: Notion Disabled (Default)
```bash
# .env: NOTION_ENABLED=false (or not set)
python main.py
# Expected: All tasks run, no Notion sync attempts
```

### Test 2: Notion Enabled, Missing API Key
```bash
# .env: NOTION_ENABLED=true (no NOTION_API_KEY)
python main.py
# Expected: Graceful skip with warning message
```

### Test 3: Notion Fully Configured
```bash
# .env: NOTION_ENABLED=true + API key + database IDs
python main.py
# Expected: Successful sync to Notion
```

### Test 4: Dry Run Mode
```bash
# .env: NOTION_DRY_RUN=true
python main.py
# Expected: Prints what would sync, no API calls
```

### Test 5: Old Config File Warning
```bash
# config/notion_config.json exists
python main.py
# Expected: Warning about obsolete file, env vars take precedence
```

## Benefits

✅ **Single source of truth** - environment variables only
✅ **Simple master switch** - `NOTION_ENABLED=false` = nothing happens
✅ **Clear separation** - env vars for config, no file management
✅ **Docker/GitHub Actions friendly** - works great with containerized deployments
✅ **Easy to understand** - one place to look for all Notion config
✅ **Optional by default** - when disabled, no Notion code runs
✅ **Graceful degradation** - missing config is handled cleanly

## Drawbacks

⚠️ **Breaking change** - existing users must migrate
⚠️ **More env vars** - longer .env file (but clearer structure)

## Implementation Order

1. Update `core/notion_client.py` with simplified logic
2. Add warning for obsolete config file
3. Update `.env.example`
4. Delete `config/notion_config.json` and `.example`
5. Create `docs/notion-migration-guide.md`
6. Update `README.md`
7. Update GitHub Actions documentation
8. Run all tests to verify behavior
9. Test migration path manually

## Future Considerations

- Could add `NOTION_ENABLED_PER_TASK=true/false` for per-task control (if needed)
- Could add validation script to check Notion configuration
- Could add health check endpoint to verify Notion connectivity

---

**Design approved:** 2026-02-16
**Next step:** Create implementation plan using writing-plans skill
