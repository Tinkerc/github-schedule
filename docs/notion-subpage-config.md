# Notion Sub-Page Configuration

## Overview

The Notion integration supports two sync modes:
- **Database mode**: Creates entries as rows in a Notion database
- **Sub-page mode**: Creates pages as children under a parent page

## Configuration

### Sub-Page Mode (Recommended for daily content)

Add to your `.env` file:

```bash
# Parent page IDs for sub-page mode
NOTION_PAGE_TECH_INSIGHTS=your-parent-page-id-1
NOTION_PAGE_TRENDING_AI=your-parent-page-id-2
NOTION_PAGE_AI_NEWS=your-parent-page-id-3
```

**To find a page ID:**
1. Open the page in Notion
2. Copy the URL
3. The page ID is the 32-character string after `/` and before `?`
   Example: `https://www.notion.so/your-workspace/PAGE-NAME-32charid?pvs=4`
                                                    ^^^^^^^^^^^^^^^^^^^^^^^^

### Database Mode (Legacy)

```bash
# Database IDs for database mode
NOTION_DB_TECH_INSIGHTS=database-id
NOTION_DB_TRENDING_AI=database-id
```

## Priority

Tasks check `NOTION_PAGE_*` first, then fall back to `NOTION_DB_*`.
If neither is configured, the task will fail with a configuration error.

## Environment Variables Reference

### Sub-Page Mode Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NOTION_PAGE_TECH_INSIGHTS` | Parent page ID for tech_insights task | 32-char string |
| `NOTION_PAGE_TRENDING_AI` | Parent page ID for trending_ai task | 32-char string |
| `NOTION_PAGE_AI_NEWS` | Parent page ID for ai_news task | 32-char string |

### Database Mode Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NOTION_DB_TECH_INSIGHTS` | Database ID for tech_insights task | 32-char string |
| `NOTION_DB_TRENDING_AI` | Database ID for trending_ai task | 32-char string |

## Migration

To migrate a task from database to sub-page:
1. Add the `NOTION_PAGE_*` variable to your `.env` with your page ID
2. (Optional) Remove the `NOTION_DB_*` variable from your `.env`
3. The next sync will create a sub-page instead of a database entry

Old database entries are not automatically deleted. Remove them manually if needed.

## Example Configuration

Complete `.env` example:

```bash
# Master switch
NOTION_ENABLED=true

# API credentials
NOTION_API_KEY=ntn_your_api_key_here

# Sub-page mode (recommended)
NOTION_PAGE_TECH_INSIGHTS=abc123def456abc123def456abc123de
NOTION_PAGE_TRENDING_AI=def456abc123def456abc123def456abc1

# Database mode (optional fallback)
NOTION_DB_AI_NEWS=456abc123def456abc123def456abc123de

# Optional settings
NOTION_DELETE_DUPLICATES=true
NOTION_DRY_RUN=false
NOTION_DEBUG=false
```
