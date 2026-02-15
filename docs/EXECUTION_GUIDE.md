# Task Framework Execution Guide

**Start Date:** 2026-02-16
**Plan:** docs/plans/2026-02-16-task-framework-implementation.md

---

## 如何在新会话中执行

### 步骤 1: 启动新的 Claude Code 会话

在您的终端中：

```bash
cd /Users/tinker.chen/work/code/learning/github/github-schedule
# 如果需要创建新的 worktree（可选）
git worktree add ../github-schedule-implementation -b feature/task-framework
cd ../github-schedule-implementation
```

### 步骤 2: 在新会话中使用 executing-plans 技能

在新会话中告诉 Claude：

```
/superpowers:executing-plans
```

然后提供以下上下文：

```
I have an implementation plan at docs/plans/2026-02-16-task-framework-implementation.md

The plan refactors the numbered-script system into a task framework with:
- Task and Notifier base classes in core/
- Migrate 4 scripts to tasks/ directory
- Update main.py to use TaskRunner

Please execute the plan step-by-step. Follow the TDD approach:
1. Write test (if applicable)
2. Run test to verify it fails
3. Implement minimal code
4. Run test to verify it passes
5. Commit after each task

Pause after each phase for review.
```

### 步骤 3: 执行检查点

计划分为6个阶段，每个阶段完成后暂停：

**Phase 1: 创建框架核心** (Tasks 1-2)
- 创建 core/base.py 和 core/runner.py
- 验证基础结构

**Phase 2: 迁移任务** (Tasks 3-7)
- 创建 tasks/ai_news.py
- 创建 tasks/github_trending.py
- 创建 tasks/trending_ai.py
- 创建 tasks/wecom_robot.py

**Phase 3: 更新入口点** (Task 8)
- 更新 main.py 使用 TaskRunner

**Phase 4: 验证** (Task 9)
- 运行完整管道
- 验证所有输出文件

**Phase 5: 文档更新** (Tasks 10-11)
- 更新 CLAUDE.md
- 清理旧的 script/ 目录

**Phase 6: 最终验证** (Task 12)
- 完整端到端测试
- 推送到远程

### 步骤 4: 独立测试每个任务

在执行过程中，可以独立测试每个任务：

```bash
# 测试 AI 新闻任务
python -m tasks.ai_news

# 测试 GitHub Trending
python -m tasks.github_trending

# 测试 AI 分析
export BIGMODEL_API_KEY=your_key
python -m tasks.trending_ai

# 测试企业微信通知
export WECOM_WEBHOOK_URL=your_webhook_url
python -m tasks.wecom_robot

# 运行完整管道
python main.py
```

### 步骤 5: 验证清单

完成后验证：

- [ ] 所有任务可以独立运行
- [ ] 完整管道执行成功
- [ ] 输出文件格式正确
- [ ] 企业微信通知正常
- [ ] 旧的 script/ 目录已删除
- [ ] 文档已更新
- [ ] 所有提交已推送
- [ ] 已打标签 v2.0.0

---

## 环境变量

确保设置以下环境变量（在 .env 文件中）：

```bash
BIGMODEL_API_KEY=your_zhipuai_api_key
WECOM_WEBHOOK_URL=your_wecom_webhook_url
```

---

## 输出文件结构

执行完成后，应该有以下输出：

```
output/
├── ai-news/
│   └── 2026-02-16.json
└── 2026/
    ├── 2026-02-16.md
    └── 2026-02-16-analysis.md
```

---

## 如果遇到问题

### 问题 1: 任务发现失败

检查 tasks/ 目录是否存在 __init__.py

### 问题 2: 导入错误

确保项目根目录在 sys.path 中

### 问题 3: 权限错误

检查输出目录的写权限

---

## 完成后

执行完成后，合并到主分支：

```bash
git checkout main
git merge feature/task-framework
git push origin main
git tag -a v2.0.0 -m "Task Framework Migration"
git push origin v2.0.0
```

---

**Good luck! 🚀**
