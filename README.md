# GitHub Schedule Automation System

自动化数据采集与分析系统，通过 GitHub Actions 定时执行，聚合多源数据并生成智能洞察。

## ⚡ 快速开始

### 环境要求
- Python 3.8+
- 依赖包见 `requirements.txt`

### 安装
```bash
# 克隆仓库
git clone <repository-url>
cd github-schedule

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的 API keys
```

### 运行
```bash
# 手动执行
python main.py
```

## 📁 项目结构

```
github-schedule/
├── src/                    # 应用源代码
│   ├── core/              # 核心框架（Task/Notifier基类）
│   └── tasks/             # 业务任务（数据采集、AI分析）
├── scripts/               # 工具脚本
│   ├── tools/            # 实用工具（验证、调试、清理）
│   ├── demos/            # 功能演示
│   └── manual/           # 手动测试脚本
├── tests/                 # 测试代码
├── docs/                  # 完整文档
└── output/                # 数据输出
```

## 📚 文档

完整文档请查看 [`docs/`](./docs/) 目录：

- **[使用指南](./docs/guides/)** - 快速开始、配置说明、测试指南
- **[开发文档](./docs/development/)** - 开发者指南、代码规范
- **[项目文档](./docs/projects/)** - 各功能模块的设计与实现文档

## 🔧 核心功能

### 数据采集任务（PRIORITY 10-20）
- **AI News** - 每日AI新闻聚合
- **HackerNews** - Top 30热门文章
- **ProductHunt** - Top 20新产品
- **TechBlogs** - 技术博客趋势
- **GitHub Trending** - 多语言趋势项目

### AI分析任务（PRIORITY 30-40）
- **Trending AI** - AI驱动的趋势分析
- **Tech Insights** - 综合技术行业简报

### 通知渠道
- **WeChat Work** - 企业微信机器人推送
- **Notion** - 自动同步到Notion数据库/页面

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行特定测试
pytest tests/integration/notion/test_notion_client.py -v
```

## ⚙️ 配置

主要环境变量（见 `.env.example`）：

```bash
# AI分析（必需）
VOLCENGINE_API_KEY=your_api_key_here
VOLCENGINE_MODEL=ep-20250215154848-djsgr

# 企业微信通知（必需）
WECOM_WEBHOOK_URL=your_webhook_url

# Notion集成（可选）
NOTION_ENABLED=true
NOTION_API_KEY=your_notion_token
NOTION_PAGE_TECH_INSIGHTS=page_id_here
NOTION_PAGE_TRENDING_AI=page_id_here
```

## 📊 输出数据

数据按日期和类型保存在 `output/` 目录：

```
output/
├── ai-news/{year}/{date}.json      # AI新闻
├── hackernews/{date}.json          # HN数据
├── producthunt/{date}.json         # PH数据
├── techblogs/{date}.json           # 技术博客
├── tech-insights/{date}.md         # AI分析报告
└── github-trending/{year}/{date}.md # GitHub趋势
```

## 🚀 GitHub Actions

项目配置了每日自动执行（UTC 00:00），工作流定义在 `.github/workflows/blank.yml`。

## 🛠️ 开发

### 添加新任务

1. 在 `src/tasks/` 创建新任务类，继承 `Task`
2. 设置 `TASK_ID` 和 `PRIORITY`
3. 实现 `execute()` 方法
4. 运行 `python -m tasks.your_task` 测试

### 添加新通知器

1. 在 `src/tasks/` 创建通知器类，继承 `Notifier`
2. 设置 `NOTIFIER_ID` 和 `SUBSCRIBE_TO`
3. 实现 `send()` 方法

详细开发指南见 [CLAUDE.md](./docs/development/CLAUDE.md)

## 📝 更新日志

### 2026-02-16
- ✨ 迁移到 `src/` 布局（现代Python项目结构）
- ✨ 重组文档目录（简化结构）
- ✨ 完全分类测试文件
- ✨ 新增工具脚本分类

详见：[MIGRATION_TO_SRC_LAYOUT.md](./MIGRATION_TO_SRC_LAYOUT.md)

## 📄 许可证

[请添加您的许可证信息]

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**快速链接：**
- 📖 [完整文档](./docs/)
- 🔧 [配置指南](./docs/guides/getting-started.md)
- 🧪 [测试指南](./docs/guides/testing.md)
- 💡 [开发规范](./docs/development/CLAUDE.md)
