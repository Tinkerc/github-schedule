# Testing Guide

This document provides quick reference for testing the GitHub Schedule project.

## Quick Verification Tests

### Run Manual Tests
```bash
python test_manual.py
```

This runs a quick sanity check covering:
- Environment variable configuration
- Git helper module imports
- Script discovery and validation
- HTTP timeout configuration
- AI news script structure

### Run Comprehensive Tests
```bash
python test_verification.py
```

This runs detailed verification including:
- All manual test checks
- Requirements.txt validation
- GitHub Actions workflow configuration
- README documentation completeness

## Testing Individual Scripts

### Test AI News Fetching
```bash
# Fetch today's AI news and save as JSON
python script/1.ai-news.py
```

Output: `output/ai-news/YYYY-MM-DD.json`

### Test WeChat Notification
```bash
# Requires WECOM_WEBHOOK_URL environment variable
export WECOM_WEBHOOK_URL="your_webhook_url"
python script/2.wecom-robot.py
```

### Test GitHub Trending
```bash
# Scrape trending repos and save as markdown
python script/github-trending.py
```

Output: `{YEAR}/{DATE}.md`

### Run All Scripts
```bash
python main.py
```

This executes all scripts with `job()` functions in alphabetical order.

## Environment Setup

### 1. Create `.env` file
```bash
cp .env.example .env
# Edit .env with your actual values
```

### 2. Required Environment Variables
```bash
# For WeChat notifications
export WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"

# Optional: For ZhipuAI API
export BIGMODEL_API_KEY="your_api_key"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Common Issues

### Issue: "WECOM_WEBHOOK_URL not set"
**Solution**: Set the environment variable or create a `.env` file

```bash
export WECOM_WEBHOOK_URL="your_webhook_url"
```

### Issue: Script doesn't run
**Solution**: Check that the script has a `job()` function
```bash
grep "def job(" script/your-script.py
```

### Issue: Git helper import error
**Solution**: Ensure you're running from the project root directory
```bash
cd /path/to/github-schedule
python main.py
```

## CI/CD Testing

The project uses GitHub Actions for automated testing. The workflow runs daily at 00:00 UTC.

Required secrets:
- `WECOM_WEBHOOK_URL` - WeChat webhook URL
- `MAILUSERNAME` - Email username (optional)
- `MAILPASSWORD` - Email password (optional)

## Test Output

Expected output when running tests:
```
✓ PASS: Environment Variables
✓ PASS: Git Helper Module
✓ PASS: Script Loading
✓ PASS: HTTP Configuration
✓ PASS: AI News Script
Result: 5/5 tests passed
```

## Development Workflow

1. Make changes to scripts
2. Run `python test_manual.py` for quick verification
3. Run individual scripts to test functionality
4. Run `python main.py` to test the full workflow
5. Commit and push changes
