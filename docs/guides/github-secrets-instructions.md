# GitHub Secrets Configuration for Notion Integration

This document describes the manual steps to add Notion integration secrets to GitHub Actions.

## Overview

Notion integration is **disabled by default**. To enable Notion sync in GitHub Actions, you need to configure the following secrets.

## Required Secrets (when enabling Notion)

### NOTION_ENABLED
- **Required to enable Notion sync**
- Set to `true` to enable, `false` to disable
- Add to GitHub: Settings → Secrets and variables → Actions → New repository secret
  - Name: `NOTION_ENABLED`
  - Value: `true`

### NOTION_API_KEY
1. Go to https://www.notion.so/my-integrations
2. Find your integration
3. Copy the "Internal Integration Token"
4. Add to GitHub: Settings → Secrets and variables → Actions → New repository secret
   - Name: `NOTION_API_KEY`
   - Value: [paste your token starting with `ntn_`]

### NOTION_DB_TECH_INSIGHTS
- **Required** if `NOTION_ENABLED=true`
- Database ID for Tech Insights
- Get from database URL: `https://notion.so/workspace/[DATABASE_ID]?v=...`
- The DATABASE_ID is a 32-character string
- Add to GitHub as a new secret

### NOTION_DB_TRENDING_AI
- **Required** if `NOTION_ENABLED=true`
- Database ID for GitHub Trending AI analysis
- Get from database URL: `https://notion.so/workspace/[DATABASE_ID]?v=...`
- Add to GitHub as a new secret

## Optional Secrets

### NOTION_DELETE_DUPLICATES
- Controls whether to delete existing entries for the same date before syncing
- Default: `true`
- Set to `false` to keep duplicate entries

### NOTION_DRY_RUN
- Test mode that logs what would be synced without actual API calls
- Default: `false`
- Set to `true` for testing

### NOTION_DEBUG
- Enable verbose logging for Notion operations
- Default: `false`
- Set to `true` for debugging

## Setup Steps

1. **Create Notion Integration** (if not already created)
   - Go to https://www.notion.so/my-integrations
   - Create a new integration
   - Copy the Internal Integration Token

2. **Create Notion Databases**
   - Create databases in Notion for each content type
   - Add properties: `Title` (title), `Date` (date), `Source` (select)
   - Add your integration to each database (click "..." → "Add connections")

3. **Get Database IDs**
   - Open each database in Notion
   - Copy the 32-character ID from the URL

4. **Add Secrets to GitHub**
   - Go to: Settings → Secrets and variables → Actions → New repository secret
   - Add each secret with the correct name and value

5. **Enable Notion Sync**
   - Add `NOTION_ENABLED` secret with value `true`
   - Workflow will pick up all secrets automatically

## Verification

After adding secrets, verify the workflow runs successfully:

```bash
# Check the Actions tab in your GitHub repository
# Look for successful workflow runs
# Check logs for Notion sync messages
```

You should see messages like:
- `[Notion] Syncing tech_insights for 2026-02-16`
- `[Notion] ✓ Successfully synced to Notion`

## Quick Test

To test without actual API calls, temporarily set:
- `NOTION_DRY_RUN=true`
- Run the workflow manually
- Check logs for "DRY RUN: Would sync..." messages

## Troubleshooting

**Problem**: Notion sync doesn't run
- **Solution**: Check `NOTION_ENABLED` is set to `true`

**Problem**: "NOTION_API_KEY not configured"
- **Solution**: Verify the secret name matches exactly (case-sensitive)

**Problem**: "No database ID configured"
- **Solution**: Add the required `NOTION_DB_*` secrets

## Migration from Config File

If you were previously using `config/notion_config.json`, see [notion-migration-guide.md](notion-migration-guide.md) for migration instructions.
