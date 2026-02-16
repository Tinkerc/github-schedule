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
