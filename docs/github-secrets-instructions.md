# GitHub Secrets Configuration for Notion Integration

This document describes the manual steps to add Notion integration secrets to GitHub Actions.

## Required Secrets

### NOTION_API_KEY
1. Go to https://www.notion.so/my-integrations
2. Find your integration
3. Copy the "Internal Integration Token"
4. Add to GitHub: Settings → Secrets and variables → Actions → New repository secret
   - Name: `NOTION_API_KEY`
   - Value: [paste your token]

## Optional Secrets

These secrets override the values in `config/notion_config.json`:

### NOTION_DB_TECH_INSIGHTS
- Database ID for Tech Insights
- Get from database URL: `https://notion.so/workspace/[DATABASE_ID]?v=...`

### NOTION_DB_TRENDING_AI
- Database ID for GitHub Trending AI analysis
- Get from database URL

### NOTION_DB_AI_NEWS
- Database ID for AI News
- Get from database URL

## Verification

After adding secrets, verify the workflow runs successfully:

```bash
# Check the Actions tab in your GitHub repository
# Look for successful workflow runs with Notion sync messages
```

The workflow will automatically pick up these secrets and use them for Notion synchronization.
