# 🎉 Notion 集成 - 快速参考

## ✅ 状态：完全正常工作

所有问题已修复并测试通过！

---

## 🚀 快速使用

### 验证配置
```bash
python scripts/verify_notion_config.py
```

### 测试推送
```bash
# 干运行（安全测试）
python tests/manual_notion_test.py --task tech_insights --dry-run

# 真实推送
python tests/manual_notion_test.py --task tech_insights --real
```

### 运行完整自动化
```bash
python main.py
```

---

## 📋 配置检查清单

- ✅ `.env` 文件已配置（`NOTION_API_KEY`, `NOTION_DB_TECH_INSIGHTS` 等）
- ✅ Notion Integration 已添加到数据库
- ✅ SOCKS 代理支持已安装（`pip install "httpx[socks]"`）
- ✅ 数据库 ID 为 32 字符格式（例如 `30943ad321af80d3a5e7d6c17ce3a93a`）

---

## 🔧 故障排查

| 错误 | 解决方案 |
|------|----------|
| `Could not find database` | 在 Notion 中添加 Integration 到数据库 |
| `socksio package not installed` | `pip install "httpx[socks]"` |
| `NOTION_API_KEY not set` | 检查 `.env` 文件是否存在并配置 |
| `'DatabasesEndpoint' object has no attribute 'query'` | 已修复 - 使用 `data_sources` API |
| `Title is expected to be rich_text` | 已修复 - 使用正确的属性类型 |

---

## 📚 完整文档

- **完整修复报告:** `docs/notion-integration-success-report.md`
- **设置指南:** `docs/notion-integration-setup-guide.md`
- **调试报告:** `docs/notion-debug-report.md`

---

## 🎯 测试结果

```bash
$ python tests/manual_notion_test.py --task tech_insights --real
============================================================
Testing real API sync for tech_insights
============================================================
[Notion] ✓ Successfully synced to Published Markdown for 2026-02-16

Result: ✓ PASS
```

✅ 内容已成功添加到 Notion！

---

**最后更新:** 2026-02-16
