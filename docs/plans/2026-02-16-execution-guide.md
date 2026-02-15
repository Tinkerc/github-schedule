# 技术行业动态跟踪系统 - 执行指南

**Date:** 2026-02-16
**Branch:** refactor-project-architecture
**Status:** Ready to Execute

---

## 📋 项目概述

**目标：** 构建一个每日自动化的技术行业动态跟踪系统

**核心功能：**
- 从Hacker News、Product Hunt、技术博客收集数据
- 使用AI（ZhipuAI GLM-4）生成技术趋势简报
- 通过企业微信推送简报

**技术架构：**
- 基于Task/Notifier框架
- 4个新的Task类 + 扩展的WeComNotifier
- AI分析综合所有数据源

**预计完成时间：** 3-4小时

---

## 🚀 快速启动

### Step 1: 验证环境

```bash
# 确认在正确的分支
git branch
# 应该显示: * refactor-project-architecture

# 确认设计文档存在
ls -la docs/plans/2026-02-16-tech-industry-insights-*.md
# 应该看到两个文件:
# - 2026-02-16-tech-industry-insights-design.md
# - 2026-02-16-tech-industry-insights-implementation.md
```

### Step 2: 打开新的Claude Code会话

```bash
# 在当前项目目录打开新会话
claude .
```

### Step 3: 启动执行模式

在新会话中执行以下命令：

```
/superpowers:executing-plans
```

### Step 4: 告诉Claude执行计划

在新会话中输入：

> **"执行实施计划：docs/plans/2026-02-16-tech-industry-insights-implementation.md"**

---

## 📚 实施计划内容

实施计划包含10个主要任务，每个任务拆分为2-5分钟的小步骤：

### Task 1: 创建HackerNewsTask (30-45分钟)
- 创建tasks目录和hackernews.py
- 使用Hacker News Official API获取Top 30
- 保存到output/hackernews/YYYY-MM-DD.json
- 独立测试并提交

### Task 2: 创建TechInsightsTask基础框架 (30分钟)
- 创建tech_insights.py
- 使用Mock数据生成AI简报
- 验证输出格式
- 测试并提交

### Task 3: 集成ZhipuAI API (30分钟)
- 添加ZhipuAI客户端
- 实现真实API调用
- 处理API失败降级到Mock
- 测试并提交

### Task 4: 创建ProductHuntTask (45分钟)
- 创建producthunt.py
- 实现网页抓取
- 添加Mock数据fallback
- 测试并提交

### Task 5: 创建TechBlogsTask (30分钟)
- 创建techblogs.py
- 集成Dev.to API
- 获取热门文章
- 测试并提交

### Task 6: 扩展WeComNotifier (30分钟)
- 修改SUBSCRIBE_TO添加tech_insights
- 实现长消息分段发送
- 测试企业微信推送
- 提交

### Task 7: 创建集成测试 (30分钟)
- 编写test_tech_insights.py
- 测试完整流程
- 验证所有输出
- 提交

### Task 8: 运行完整流程 (15分钟)
- 执行main.py
- 验证所有7个任务
- 检查输出文件
- 提交

### Task 9: 更新文档 (15分钟)
- 更新CLAUDE.md
- 添加新任务说明
- 提交

### Task 10: 最终验证 (15分钟)
- 运行测试套件
- 清理和总结
- 最终提交

---

## ✅ 执行模式说明

在新会话中使用`executing-plans` skill时，Claude将：

### 自动化执行流程
- ✅ 按照任务顺序逐个执行
- ✅ 每个步骤包含完整代码和命令
- ✅ 遵循TDD原则（测试先行）
- ✅ 每个步骤后自动git commit

### 检查点暂停
在每个Task完成后会暂停，让你：
- 📊 查看git提交历史
- 🧪 运行测试验证功能
- ✅ 确认继续下一个任务
- 🔄 如有问题可以回退重做

### 示例对话流程

```
You: /superpowers:executing-plans

Claude: I'll help you execute the implementation plan step by step.
      Please provide the path to the implementation plan file.

You: docs/plans/2026-02-16-tech-industry-insights-implementation.md

Claude: Perfect! I found the plan with 10 tasks.
      Starting with Task 1: 创建HackerNewsTask基础框架

      [执行Task 1的所有步骤...]

      ✅ Task 1 completed! 3 commits made.

      📊 Git commits:
      - feat(tasks): add HackerNewsTask for fetching top 30 stories

      🧪 To verify: python -c "from tasks.hackernews import HackerNewsTask; ..."

      ⏸️ Checkpoint: Task 1完成。继续执行Task 2?

You: 是的，继续

Claude: Starting Task 2: 创建TechInsightsTask基础框架
      [...]
```

---

## 🔧 环境准备

### 必需的环境变量

```bash
# ZhipuAI API Key (用于AI分析)
export BIGMODEL_API_KEY="your_api_key_here"

# 企业微信Webhook (用于通知)
export WECHAT_WEBHOOK="your_webhook_url_here"
```

### Python依赖检查

```bash
# 确认已安装的包
pip list | grep -E "requests|pyquery|zhipuai"

# 应该看到:
# requests          X.X.X
# pyquery           X.X.X
# zhipuai           X.X.X
```

### 目录结构确认

```bash
# 应该存在以下目录
ls -la
# core/           - 框架代码
# tasks/          - 新任务将创建在这里（执行时创建）
# output/         - 输出目录
# script/         - 旧系统
# docs/           - 文档
```

---

## 📊 验收清单

完成所有任务后，确认以下内容：

### 功能验收
- [ ] HackerNewsTask能成功获取30条HN数据
- [ ] ProductHuntTask能成功获取Top 20产品
- [ ] TechBlogsTask能成功获取Dev.to文章
- [ ] TechInsightsTask能生成AI分析简报
- [ ] 简报包含所有必需章节
- [ ] WeComNotifier能推送简报到企业微信

### 测试验收
- [ ] `python test_tech_insights.py` 全部通过
- [ ] `python main.py` 完整流程执行成功
- [ ] 所有7个任务显示"成功执行"
- [ ] 输出文件格式正确

### 代码质量
- [ ] 遵循TDD原则（测试先行）
- [ ] 每个步骤都有git commit
- [ ] 提交信息符合conventional commits规范
- [ ] 代码有适当的错误处理

### 文档验收
- [ ] CLAUDE.md已更新
- [ ] 设计文档已提交
- [ ] 实施计划已执行
- [ ] Git历史清晰可追溯

---

## 🐛 故障排查

### 问题1: 无法启动executing-plans

**症状：** `/superpowers:executing-plans` 命令无效

**解决：**
```bash
# 确认使用的是Claude Code CLI
claude --version

# 或者在会话中直接输入
"使用superpowers:executing-plans skill执行docs/plans/2026-02-16-tech-industry-insights-implementation.md"
```

### 问题2: API调用失败

**症状：** TechInsightsTask报错"未找到BIGMODEL_API_KEY"

**解决：**
```bash
# 检查环境变量
echo $BIGMODEL_API_KEY

# 如果为空，设置它
export BIGMODEL_API_KEY="your_key"

# 或者在.env文件中添加
echo "BIGMODEL_API_KEY=your_key" >> .env
```

### 问题3: 任务执行顺序错误

**症状：** main.py执行时任务顺序不对

**解决：**
```bash
# 检查PRIORITY设置
grep -n "PRIORITY = " tasks/*.py

# 应该看到:
# hackernews.py:    PRIORITY = 15
# producthunt.py:   PRIORITY = 16
# techblogs.py:     PRIORITY = 17
# tech_insights.py: PRIORITY = 40
```

### 问题4: 企业微信推送失败

**症状：** WeComNotifier报错"webhook发送失败"

**解决：**
```bash
# 测试webhook
curl -X POST "$WECHAT_WEBHOOK" \
  -H 'Content-Type: application/json' \
  -d '{"msgtype":"text","text":{"content":"测试消息"}}'

# 检查返回结果，应该包含"errcode":0
```

---

## 📞 获取帮助

如果在执行过程中遇到问题：

### 1. 回顾设计文档
```bash
cat docs/plans/2026-02-16-tech-industry-insights-design.md
```

### 2. 查看实施计划的详细步骤
```bash
cat docs/plans/2026-02-16-tech-industry-insights-implementation.md
```

### 3. 检查Git历史了解已完成的工作
```bash
git log --oneline -10
```

### 4. 运行测试定位问题
```bash
python test_tech_insights.py
```

---

## 🎯 完成标准

当满足以下条件时，可以认为实施完成：

1. ✅ 所有10个任务执行完毕
2. ✅ 集成测试全部通过
3. ✅ `python main.py` 成功执行完整流程
4. ✅ 企业微信成功接收技术简报
5. ✅ 所有代码已提交到Git
6. ✅ 文档已更新
7. ✅ 输出文件格式正确且内容完整

---

## 📈 后续优化方向

完成基础实施后，可以考虑：

1. **添加更多数据源**
   - Reddit (r/programming, r/MachineLearning)
   - Medium热门技术文章
   - HackerNoon

2. **增强AI分析**
   - 添加历史数据对比
   - 生成趋势图表
   - 个性化推荐

3. **优化通知**
   - 支持Email、Slack、Discord
   - 添加摘要模式
   - 定时推送

4. **性能优化**
   - 并行执行数据收集
   - 添加缓存机制
   - 减少API调用

5. **监控和告警**
   - 任务执行时间监控
   - 失败率统计
   - 异常告警

---

## 📝 重要提示

### 执行原则
- ⏱️ 每个步骤控制在2-5分钟
- 🧪 遵循TDD（测试先行）
- 💾 频繁提交代码
- ✅ 在检查点验证再继续
- 🔄 遇到问题及时回退

### Git工作流
```bash
# 查看当前进度
git log --oneline --graph -10

# 查看未提交的更改
git status

# 如果需要回退到某个步骤
git reset --soft <commit-hash>
```

### 测试驱动
```python
# 每个Task都有独立测试方法
python -c "from tasks.xxx import XxxTask; task = XxxTask(); print(task.execute())"

# 完整流程测试
python test_tech_insights.py

# 主流程测试
python main.py
```

---

**祝执行顺利！** 🚀

如有问题，参考实施计划中的详细步骤或查看设计文档了解架构。
