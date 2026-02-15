# GitHub Schedule

Python-based scheduled task automation system that runs daily via GitHub Actions. It fetches data from various sources (AI news, GitHub trending, etc.) and processes it.

## Features

- **AI News Scraping**: Daily fetches AI industry news from https://ai-bot.cn/daily-ai-news/
- **GitHub Trending**: Tracks trending repositories for multiple programming languages (Python, JavaScript, Go, Java)
- **AI-Powered Analysis**: Analyzes GitHub trending data using ZhipuAI GLM-4 model
- **WeChat Work Integration**: Sends daily AI news notifications to Enterprise WeChat
- **Automated Execution**: Runs daily at 00:00 UTC via GitHub Actions

## Requirements

- **Python 3.11 or higher** (required by lxml 5.3.0+)
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/github-schedule.git
cd github-schedule
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Required Environment Variables

Create a `.env` file (or set in GitHub Actions secrets) with the following variables:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual values
```

**Required:**
- `WECOM_WEBHOOK_URL`: Enterprise WeChat webhook URL for sending notifications
- `BIGMODEL_API_KEY`: ZhipuAI API key for AI analysis (get from https://open.bigmodel.cn/)
- `VOLCENGINE_API_KEY`: VolcEngine API key for alternative AI model support
- `VOLCENGINE_MODEL`: VolcEngine model identifier (e.g., ep-20241205153016-l8qhs)

**Optional:**
- `MAILUSERNAME`: Email username (for future use)
- `MAILPASSWORD`: Email password (for future use)

### GitHub Actions Secrets

For GitHub Actions, configure these secrets in your repository settings (`Settings > Secrets and variables > Actions`):

- `WECOM_WEBHOOK_URL` (required)
- `BIGMODEL_API_KEY` (required)
- `VOLCENGINE_API_KEY` (required)
- `VOLCENGINE_MODEL` (required)
- `MAILUSERNAME` (optional)
- `MAILPASSWORD` (optional)

## Usage

### Quick Verification

Before running the automation, verify your setup:

```bash
# Run quick verification tests
python test_manual.py
```

See [TESTING.md](TESTING.md) for detailed testing instructions.

### Manual Execution

Run the main script to execute all scheduled tasks:

```bash
python main.py
```

This will execute all tasks in priority order:
1. `ai_news` (PRIORITY: 10) - Fetches and saves AI news as JSON
2. `github_trending` (PRIORITY: 20) - Scrapes GitHub trending repositories and saves as markdown
3. `trending_ai` (PRIORITY: 30) - Analyzes trending data using AI and generates insights
4. `wecom` (Notifier) - Posts news to WeChat Work webhook

### Individual Tasks

Run individual tasks directly for testing:

```bash
python -m tasks.ai_news           # Fetch AI news
python -m tasks.github_trending   # Scrape GitHub trending
python -m tasks.trending_ai       # Analyze trending with AI
python -m tasks.wecom_robot       # Send notifications
```

## Output Structure

```
output/
├── ai-news/                    # Daily AI news JSON files (YYYY-MM-DD.json)
├── github-trending/            # GitHub trending data organized by year
│   └── {year}/                 # Yearly subdirectories
│       └── {date}.md           # Raw trending data
└── github-analysis/            # AI-generated analysis reports organized by year
    └── {year}/                 # Yearly subdirectories
        └── {date}-analysis.md  # AI-generated analysis report
```

## Development

### Task Framework

This project uses a task-based architecture with base classes:

**Task Base Class** - For data fetching and analysis jobs:
- Inherit from `core.base.Task`
- Set `TASK_ID` and `PRIORITY` attributes
- Implement `execute()` method returning True/False

**Notifier Base Class** - For notification modules:
- Inherit from `core.base.Notifier`
- Set `NOTIFIER_ID` and `SUBSCRIBE_TO` attributes
- Implement `send(task_results)` method

### Adding New Tasks

1. Create a new file in `tasks/` directory
2. Inherit from `Task` or `Notifier` base class
3. Set required attributes (TASK_ID/NOTIFIER_ID, PRIORITY/SUBSCRIBE_TO)
4. Implement the required method (execute() or send())
5. Test independently: `python -m tasks.<your_task>`

Example:
```python
# tasks/my_task.py
from core.base import Task

class MyTask(Task):
    TASK_ID = "my_task"
    PRIORITY = 15

    def execute(self) -> bool:
        # Your task logic here
        return True
```

### Git Proxy Configuration

If you need to use a proxy for Git operations:

```shell
git config http.proxy http://127.0.0.1:7890
git config https.proxy https://127.0.0.1:7890
```

## License

This project is open source and available under the MIT License.