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
