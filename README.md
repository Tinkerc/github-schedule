# GitHub Schedule

Python-based scheduled task automation system that runs daily via GitHub Actions. It fetches data from various sources (AI news, GitHub trending, etc.) and processes it.

## Features

- **AI News Scraping**: Daily fetches AI industry news from https://ai-bot.cn/daily-ai-news/
- **GitHub Trending**: Tracks trending repositories for multiple programming languages (Python, JavaScript, Go, Java)
- **WeChat Work Integration**: Sends daily AI news notifications to Enterprise WeChat
- **Automated Execution**: Runs daily at 00:00 UTC via GitHub Actions

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

**Optional:**
- `MAILUSERNAME`: Email username (for future use)
- `MAILPASSWORD`: Email password (for future use)
- `BIGMODEL_API_KEY`: ZhipuAI API key for GLM-4 model

### GitHub Actions Secrets

For GitHub Actions, configure these secrets in your repository settings (`Settings > Secrets and variables > Actions`):

- `WECOM_WEBHOOK_URL`
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

This will execute all scripts in the `script/` directory in alphabetical order:
1. `1.ai-news.py` - Fetches and saves AI news as JSON
2. `2.wecom-robot.py` - Posts news to WeChat Work webhook
3. `github-trending.py` - Scrapes GitHub trending repositories

### Individual Scripts

Run individual scripts directly:

```bash
python script/1.ai-news.py
python script/2.wecom-robot.py
python script/github-trending.py
```

## Output Structure

```
output/
├── ai-news/          # Daily AI news JSON files (YYYY-MM-DD.json)
└── {year}/           # GitHub trending markdown by year
```

## Development

### Script Conventions

Each script in `script/` must:
- Define a `job()` function as the entry point
- Use `datetime.datetime.now().strftime('%Y-%m-%d')` for date handling
- Output results to the `output/` directory
- Handle their own errors and print progress messages

### Git Proxy Configuration

If you need to use a proxy for Git operations:

```shell
git config http.proxy http://127.0.0.1:7890
git config https.proxy https://127.0.0.1:7890
```

## License

This project is open source and available under the MIT License.
