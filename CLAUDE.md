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
`main.py` is the orchestrator that uses `TaskRunner` to:
1. Discover all `Task` and `Notifier` classes in the `tasks/` directory
2. Execute tasks in PRIORITY order (ai_news → github_trending → trending_ai)
3. Collect task execution results
4. Execute notifiers based on subscribed task results
5. Print execution summary

### Task Framework
All tasks inherit from base classes in `core/base.py`:

**Task base class** - For data fetching and analysis jobs:
- `TASK_ID`: Unique task identifier
- `PRIORITY`: Execution order (lower numbers run first)
- `execute()`: Main task logic, returns True/False

**Notifier base class** - For notification modules:
- `NOTIFIER_ID`: Unique notifier identifier
- `SUBSCRIBE_TO`: List of task IDs to subscribe to
- `send(task_results)`: Send notification based on task results

### Task Structure
```
tasks/
├── ai_news.py           # Fetches AI news (PRIORITY: 10)
├── hackernews.py        # Fetches Hacker News Top 30 (PRIORITY: 15)
├── producthunt.py       # Scrapes Product Hunt Top 20 (PRIORITY: 16)
├── techblogs.py         # Fetches Dev.to trending articles (PRIORITY: 17)
├── github_trending.py   # Scrapes GitHub trending (PRIORITY: 20)
├── trending_ai.py       # AI analysis of trending (PRIORITY: 30)
├── tech_insights.py     # AI-powered tech industry brief (PRIORITY: 40)
└── wecom_robot.py       # WeChat Work notification (SUBSCRIBE_TO: ['ai_news', 'trending_ai', 'tech_insights'])
```

Each task can be run independently for testing:
```bash
python -m tasks.ai_news
python -m tasks.github_trending
python -m tasks.trending_ai
python -m tasks.wecom_robot
```

### Output Structure
```
output/
├── ai-news/              # Daily AI news JSON files (YYYY-MM-DD.json)
├── hackernews/           # Hacker News stories JSON (YYYY-MM-DD.json)
├── producthunt/          # Product Hunt products JSON (YYYY-MM-DD.json)
├── techblogs/            # Tech blog articles JSON (YYYY-MM-DD.json)
├── tech-insights/        # AI-generated industry brief (YYYY-MM-DD.md)
└── {year}/               # GitHub trending markdown by year
```

### GitHub Actions Workflow
The `.github/workflows/blank.yml` workflow:
- Runs daily at 00:00 UTC (cron: "0 2 * * *")
- Uses Python 3.8 on ubuntu-latest
- Installs dependencies from `requirements.txt`
- Runs `python main.py`
- Commits and pushes all changes back to the repository
- Expects secrets: `MAILUSERNAME`, `MAILPASSWORD`

### Tech Industry Insights System
The new tech insights tracking system (PRIORITY 15-40) aggregates data from multiple sources:

**Data Collection Tasks:**
- `hackernews.py` - Fetches Top 30 stories from Hacker News Official API
- `producthunt.py` - Scrapes Top 20 products (with fallback to mock data)
- `techblogs.py` - Fetches trending articles from Dev.to API

**AI Analysis Task:**
- `tech_insights.py` - Aggregates all data sources and generates AI-powered brief
- Uses Volcengine (豆包) API for AI analysis (same as trending_ai)
- Falls back to mock data if API unavailable
- Generates structured markdown with sections: hot topics, projects, trends, AI updates, tools, insights

**Notification:**
- `wecom_robot.py` - Extended to send tech_insights brief
- Implements message splitting for long content (>1900 bytes)
- Splits on ## headings for better readability

**Testing:**
- Run `python test_tech_insights.py` for comprehensive integration test
- All tasks independently testable via `python -m tasks.<task_name>`

## Dependencies
- `requests` - HTTP client
- `pyquery` - HTML parsing (jQuery-like API for Python)
- `lxml` - XML/HTML processing
- `schedule` - Job scheduling (not actively used in current implementation)
- `cssselect` - CSS selector support for lxml

## Development Notes
- The codebase uses Chinese for comments and user-facing messages
- Task framework uses `importlib.util` for dynamic task and notifier discovery
- Environment variables are loaded from `.env` file using `python-dotenv`
- Required environment variables:
  - `VOLCENGINE_API_KEY`: For AI analysis in trending_ai and tech_insights tasks
  - `VOLCENGINE_MODEL`: (optional) Volcengine model endpoint, defaults to 'ep-20250215154848-djsgr'
  - `WECOM_WEBHOOK_URL`: For WeChat Work notifications
- Each task inherits helper methods from Task base class:
  - `get_output_path(filename)`: Get full path for output files
  - `get_today()`: Get current date as YYYY-MM-DD
  - `get_year()`: Get current year as YYYY
- Task execution is priority-based (lower PRIORITY value runs first)
- Notifiers only run if their subscribed tasks succeed
