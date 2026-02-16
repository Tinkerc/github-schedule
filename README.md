# GitHub Schedule

Python-based scheduled task automation system that runs daily via GitHub Actions. It fetches data from various sources (AI news, GitHub trending, etc.) and processes it.

## Features

- **AI News Scraping**: Daily fetches AI industry news from https://ai-bot.cn/daily-ai-news/
- **GitHub Trending**: Tracks trending repositories for multiple programming languages (Python, JavaScript, Go, Java)
- **AI-Powered Analysis**: Analyzes GitHub trending data using Volcengine Doubao model
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
- `VOLCENGINE_API_KEY`: Volcengine API key for AI analysis (get from https://console.volcengine.com/ark)
- `VOLCENGINE_MODEL`: (optional) Volcengine model endpoint, defaults to 'ep-20250215154848-djsgr'

**Optional:**
- `MAILUSERNAME`: Email username (for future use)
- `MAILPASSWORD`: Email password (for future use)

### GitHub Actions Secrets

For GitHub Actions, configure these secrets in your repository settings (`Settings > Secrets and variables > Actions`):

- `WECOM_WEBHOOK_URL` (required)
- `VOLCENGINE_API_KEY` (required)
- `VOLCENGINE_MODEL` (optional)
- `MAILUSERNAME` (optional)
- `MAILPASSWORD` (optional)

## Notion Integration

The system can sync AI-generated markdown content to Notion databases for mobile access.

### Setup

1. **Create Notion Integration**
   - Go to https://www.notion.so/my-integrations
   - Create a new integration and copy the "Internal Integration Token"
   - This is your `NOTION_API_KEY`

2. **Create Notion Databases**
   - Create a database for each content type (Tech Insights, GitHub Trending, etc.)
   - Add these properties to each database:
     - `Title` (title type)
     - `Date` (date type)
     - `Source` (select type, add option "github-schedule")

3. **Get Database IDs**
   - Open each database in Notion
   - Copy the database ID from the URL: `https://notion.so/workspace/[DATABASE_ID]?v=...`

4. **Configure the Project**
   - Copy `config/notion_config.json.example` to `config/notion_config.json`
   - Add your database IDs to the config file
   - Or set environment variables: `NOTION_DB_TECH_INSIGHTS`, etc.

5. **Add to .env file**
   ```bash
   NOTION_API_KEY=your_integration_token_here
   NOTION_DB_TECH_INSIGHTS=your_database_id_here
   ```

### Testing

Test with dry-run mode (no API calls):
```bash
NOTION_DRY_RUN=true python -m tasks.tech_insights
```

Test with actual sync:
```bash
python tests/manual_notion_test.py --task tech_insights --real
```

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