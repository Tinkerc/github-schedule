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
├── github_trending.py   # Scrapes GitHub trending (PRIORITY: 20)
├── trending_ai.py       # AI analysis of trending (PRIORITY: 30)
└── wecom_robot.py       # WeChat Work notification (SUBSCRIBE_TO: ['ai_news'])
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
- Task framework uses `importlib.util` for dynamic task and notifier discovery
- Environment variables are loaded from `.env` file using `python-dotenv`
- Required environment variables:
  - `BIGMODEL_API_KEY`: For AI analysis in trending_ai task
  - `WECOM_WEBHOOK_URL`: For WeChat Work notifications
- Each task inherits helper methods from Task base class:
  - `get_output_path(filename)`: Get full path for output files
  - `get_today()`: Get current date as YYYY-MM-DD
  - `get_year()`: Get current year as YYYY
- Task execution is priority-based (lower PRIORITY value runs first)
- Notifiers only run if their subscribed tasks succeed
