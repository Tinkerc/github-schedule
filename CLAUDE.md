# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python-based scheduled task automation system that runs daily via GitHub Actions. It fetches data from various sources (AI news, GitHub trending, etc.) and processes it.

## Running the Application

### Manual execution
```bash
python main.py
```

### Install dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Entry Point
`main.py` is the orchestrator that:
1. Discovers all `.py` files in the `script/` directory
2. Executes them in alphabetical order (sorted by filename)
3. Each script is dynamically loaded and its `job()` function is called
4. After all scripts complete, git operations are performed (currently commented out)

### Script Conventions
Each script in `script/` must:
- Define a `job()` function as the entry point
- Use `datetime.datetime.now().strftime('%Y-%m-%d')` for date handling
- Output results to the `output/` directory (organized by subdirectories)
- Handle their own errors and print progress messages

Scripts are executed in filename order:
- `1.ai-news.py` - Fetches AI news from https://ai-bot.cn/daily-ai-news/ and saves as JSON
- `2.wecom-robot.py` - Reads the news JSON and posts to WeChat Work webhook
- `github-trending.py` - Scrapes GitHub trending repositories for multiple languages
- `bigmodel-stream-official.py` - Makes API calls to ZhipuAI (GLM-4 model)
- `github-trending-ai-analysis.py` - Independent script for GitHub Trending AI analysis (uses GLM-4.7)

### Output Structure
```
output/
├── ai-news/          # Daily AI news JSON files (YYYY-MM-DD.json)
└── {year}/           # GitHub trending markdown by year
```

### GitHub Actions Workflow
The `.github/workflows/blank.yml` workflow:
- Runs daily at 00:00 UTC (cron: "0 2 * * *")
- Uses Python 3.8 on ubuntu-latest
- Installs dependencies from `requirements.txt`
- Runs `python main.py`
- Commits and pushes all changes back to the repository
- Expects secrets: `MAILUSERNAME`, `MAILPASSWORD`

## Dependencies
- `requests` - HTTP client
- `pyquery` - HTML parsing (jQuery-like API for Python)
- `lxml` - XML/HTML processing
- `schedule` - Job scheduling (not actively used in current implementation)
- `cssselect` - CSS selector support for lxml

## Development Notes
- The codebase uses Chinese for comments and user-facing messages
- Git operations in `main.py` are currently disabled (line 81: `#git_add_commit_push()`)
- Scripts use `importlib.util` for dynamic module loading to execute scripts in order
- The WeChat Work webhook URL is hardcoded in `2.wecom-robot.py:56` (should be externalized to secrets)
- API keys for external services (like BIGMODEL_API_KEY) are read from environment variables
- The `github-trending-ai-analysis.py` script runs independently via GitHub Actions workflow
- Output: `output/github-trending-ai-analysis/YYYY/YYYY-MM-DD.md`
- Requires `BIGMODEL_API_KEY` environment variable
