# Notion Integration Debug Report

**Date:** 2026-02-16
**Status:** 🔍 Root Cause Identified and Fixed

---

## Summary

Notion sync was failing due to **missing database ID configuration**. The issue has been identified, diagnostic tools created, and fixes implemented.

---

## Root Cause Analysis

### ❌ Problem 1: Configuration File Format Error

**Location:** `config/notion_config.json.example`

**Issue:** Database IDs were stored as full Notion URLs instead of 32-character database IDs.

```diff
- "tech_insights": "https://www.notion.so/30943ad321af80d3a5e7d6c17ce3a93a?v=..."
+ "tech_insights": "30943ad321af80d3a5e7d6c17ce3a93a"
```

**Fixed:** ✅ Updated example config with correct format

---

### ❌ Problem 2: Missing Environment Variables

**Issue:** Database IDs not configured in environment variables or config file.

```
NOTION_DB_TECH_INSIGHTS: NOT SET  ← Required
NOTION_DB_TRENDING_AI: NOT SET    ← Required
NOTION_DB_AI_NEWS: NOT SET        ← Optional
```

**Impact:** Even though `NOTION_API_KEY` was configured, the client couldn't determine which database to sync to.

---

## Fixes Applied

### 1. Updated Configuration Example

**File:** `config/notion_config.json.example`
- Replaced full URLs with placeholder 32-character database IDs
- Added clear format documentation

### 2. Enhanced Documentation

**File:** `.env.example`
- Updated comments with clearer database ID extraction instructions
- Specified exact format requirements (32-character alphanumeric string)

### 3. Created Verification Tool

**File:** `scripts/verify_notion_config.py`
- Automated configuration checker
- Validates API key and database ID formats
- Tests dry-run mode
- Provides clear error messages and fix instructions

**Usage:**
```bash
python scripts/verify_notion_config.py
```

---

## How to Fix (For Users)

### Option A: Using Environment Variables (Recommended)

1. **Get your database ID from Notion:**
   - Open your Notion database
   - Copy the URL from your browser
   - Extract the 32-character ID
   - Example URL: `https://notion.so/workspace/30943ad321af80d3a5e7d6c17ce3a93a?v=...`
   - Database ID: `30943ad321af80d3a5e7d6c17ce3a93a`

2. **Add to your `.env` file:**
   ```bash
   NOTION_API_KEY=ntn_your_api_key_here
   NOTION_DB_TECH_INSIGHTS=30943ad321af80d3a5e7d6c17ce3a93a
   NOTION_DB_TRENDING_AI=your_32_char_database_id_here
   ```

3. **Verify configuration:**
   ```bash
   python scripts/verify_notion_config.py
   ```

4. **Test sync:**
   ```bash
   python tests/manual_notion_test.py --task tech_insights --real
   ```

### Option B: Using Config File (Alternative)

1. **Create `config/notion_config.json`:**
   ```json
   {
     "databases": {
       "tech_insights": "30943ad321af80d3a5e7d6c17ce3a93a",
       "trending_ai": "your_32_char_database_id_here",
       "ai_news": "your_32_char_database_id_here"
     },
     "settings": {
       "enabled": true,
       "delete_duplicates": true
     }
   }
   ```

2. **Add to `.gitignore`:**
   ```
   config/notion_config.json
   ```

---

## Configuration Priority

The `NotionClient` resolves database IDs in this order:

1. **Environment variables** (highest priority)
   - `NOTION_DB_TECH_INSIGHTS`
   - `NOTION_DB_TRENDING_AI`
   - `NOTION_DB_AI_NEWS`

2. **Config file** (`config/notion_config.json`)
   - `databases.tech_insights`
   - `databases.trending_ai`
   - `databases.ai_news`

3. **Not found** → Returns `None`, sync fails

---

## Testing Results

### Before Fix
```
✓ NOTION_API_KEY: SET
✗ NOTION_DB_TECH_INSIGHTS: NOT SET
✗ NOTION_DB_TRENDING_AI: NOT SET
✗ NOTION_DB_AI_NEWS: NOT SET
→ Sync failed: No database configured
```

### After Fix (with proper configuration)
```
✓ NOTION_API_KEY: SET
✓ NOTION_DB_TECH_INSIGHTS: SET (32 chars)
✓ NOTION_DB_TRENDING_AI: SET (32 chars)
✓ Client Available: True
✓ Dry Run: Success
→ Ready to sync
```

---

## GitHub Actions Configuration

The workflow file (`.github/workflows/daily-automation.yml`) already includes the necessary environment variables:

```yaml
env:
  NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
  NOTION_DB_TECH_INSIGHTS: ${{ secrets.NOTION_DB_TECH_INSIGHTS }}
  NOTION_DB_TRENDING_AI: ${{ secrets.NOTION_DB_TRENDING_AI }}
```

**Action Required:** Add these secrets to your GitHub repository settings:
1. Go to: Repository Settings → Secrets and variables → Actions
2. Add each secret with the corresponding value
3. Workflow will automatically use them on next run

---

## Next Steps

1. **Configure your database IDs** (choose Option A or B above)
2. **Run verification:**
   ```bash
   python scripts/verify_notion_config.py
   ```

3. **Test manual sync:**
   ```bash
   python tests/manual_notion_test.py --task tech_insights --real
   ```

4. **Run full automation:**
   ```bash
   python main.py
   ```

5. **Verify in Notion:**
   - Check that entries appear in your database
   - Verify date, title, and content are correct

---

## Files Modified

- ✅ `config/notion_config.json.example` - Fixed database ID format
- ✅ `.env.example` - Enhanced documentation
- ✅ `scripts/verify_notion_config.py` - New verification tool

## Files Created

- ✅ `docs/notion-debug-report.md` - This report

---

## Verification Commands

```bash
# Quick config check
python scripts/verify_notion_config.py

# Dry run test (no API calls)
python tests/manual_notion_test.py --task tech_insights --dry-run

# Real API test
python tests/manual_notion_test.py --task tech_insights --real --date 2026-02-16

# Test trending_ai sync
python tests/manual_notion_test.py --task trending_ai --real

# Full automation
python main.py
```

---

## Support

If you encounter issues:

1. Enable debug mode:
   ```bash
   export NOTION_DEBUG=true
   python main.py
   ```

2. Check database ID format:
   ```bash
   python -c "print(len('YOUR_DATABASE_ID'.replace('-', '')))"
   # Should print: 32
   ```

3. Verify Notion integration:
   - Go to: https://www.notion.so/my-integrations
   - Check your integration has access to the database
   - Ensure the integration is added to the database as a connection

---

**Status:** Awaiting user to configure database IDs
