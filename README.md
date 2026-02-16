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

## Notion Integration (Optional)

The system can sync AI-generated markdown content to Notion for mobile access.

### Sync Modes

The Notion integration supports two sync modes:

**Sub-Page Mode (Recommended)**
- Creates daily pages as children under a parent page
- Better organization with hierarchical structure
- One parent page per task type

**Database Mode (Legacy)**
- Creates entries as rows in a Notion database
- Traditional table-based organization

### Setup

1. **Create Notion Integration**
   - Go to https://www.notion.so/my-integrations
   - Create a new integration and copy the "Internal Integration Token"
   - This is your `NOTION_API_KEY`

2. **Choose Your Sync Mode**

   **For Sub-Page Mode (Recommended):**
   - Create a parent page for each content type in Notion
   - Share each page with your integration (click "..." → "Add connections")
   - Get the page ID from the URL (32-character string after `/` and before `?`)

   **For Database Mode:**
   - Create a database for each content type
   - Add properties: `Title` (title), `Date` (date), `Source` (select with "github-schedule" option)
   - Add your integration to each database
   - Get the database ID from the URL (32-character string)

3. **Configure Environment Variables**
   Add to your `.env` file:

   ```bash
   # Enable Notion sync
   NOTION_ENABLED=true

   # Your Notion Integration credentials
   NOTION_API_KEY=ntn_your_token_here

   # Sub-Page Mode (recommended)
   NOTION_PAGE_TECH_INSIGHTS=32_char_page_id_here
   NOTION_PAGE_TRENDING_AI=32_char_page_id_here

   # OR Database Mode (legacy)
   NOTION_DB_TECH_INSIGHTS=32_char_db_id_here
   NOTION_DB_TRENDING_AI=32_char_db_id_here
   ```

   **Priority:** Tasks check `NOTION_PAGE_*` first, then fall back to `NOTION_DB_*`.

### Getting Page/Database IDs

1. Open your Notion page or database
2. Copy the 32-character ID from the URL: `notion.so/workspace/[ID]?v=...`

### Test Configuration

```bash
# Dry run (no API calls)
NOTION_DRY_RUN=true python main.py

# Real sync
python main.py
```

### Documentation

- [Sub-Page Configuration](docs/notion-subpage-config.md) - Detailed setup guide for both modes
- [Migration Guide](docs/notion-migration-guide.md) - Migrating from old config file format

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