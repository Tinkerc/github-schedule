# 黄金观察飞书定时提醒方案

## 目标与范围

将 `personal-system` 中的三条黄金观察提醒迁入 GitHub Actions。飞书卡片在观察事项上方展示伦敦金美元报价、较上次采集的涨跌和根据固定金价锚点反推的参考汇率，并提供上金所 Au99.99 延时行情链接。

## 调度与接口

| 提醒 | 北京时间（周一至周五） | GitHub Actions cron（UTC） |
| --- | --- | --- |
| 早间观察 | 09:30 | `30 1 * * 1-5` |
| 午后观察 | 15:00 | `0 7 * * 1-5` |
| 晚间记录 | 21:00 | `0 13 * * 1-5` |

工作流 `.github/workflows/feishu-reminder.yml` 将触发事件中的 cron 原文传给 `scripts/feishu_reminder.py`，所以延迟执行时仍会匹配原定时段。手动运行可选择任一时段，默认发送一条明确标记为测试的卡片。发送脚本使用 Python 标准库，通过 `FEISHU_WEBHOOK_URL` 和 `FEISHU_SECRET` 获取凭据，按飞书自定义机器人的签名方式发送。

## 行情与历史比较

- 每次发送前查询免密钥接口 `GET https://api.gold-api.com/price/XAU`，读取美元每金衡盎司报价和采集时间 `updatedAt`。请求超时为 8 秒，卡片显示北京时间。
- 使用最近一条有效的 XAU/USD 快照作为基准。差价为本次价格减上次价格，涨跌幅为差价除以上次价格再乘 100%。卡片同时显示基准价格和采集时间。首次采集只建立基准。
- 定时运行与手动观察时段将有效的新报价保存为 `quote.json`，记录 `symbol`、`currency`、十进制价格字符串 `price` 和 UTC 采集时间 `updatedAt`。工作流用原生 GitHub 令牌恢复同一分支最新的 `feishu-gold-xau-quote` 文件产物。同分支观察运行按队列串行执行。文件产物使用仓库的保留期，每个运行保留一份快照。手动 `test` 可读基准并预览比较结果。
- 报价已超过 5 分钟、采集时间重复或倒退时，保留上次有效快照并跳过涨跌计算。行情接口或基准读取失败时继续发送卡片。新报价在尝试发送飞书前落盘，即使飞书发送失败也能保留这条采集记录。

## 固定锚点参考汇率

按伦敦金 3544 美元/金衡盎司、Au99.99 763 元/克和每金衡盎司 31.1034768 克，计算 `763 × 31.1034768 ÷ 3544 ≈ 6.6964` 元/美元。卡片每次都显示这组固定锚点及其隐含换算率。该数值包含两个市场的价差，只作金价口径换算参考。

## 启用与验证

1. 在飞书群自定义机器人的安全设置中开启签名校验。在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 添加两个仓库 Secret。
   - `FEISHU_WEBHOOK_URL` 填飞书机器人的完整 webhook 地址。
   - `FEISHU_SECRET` 填机器人签名密钥。
2. 将工作流合入仓库默认分支。在 **Actions → Feishu Gold Observation Reminder → Run workflow** 选择 `test`，确认群中收到测试卡片。选择观察时段或等定时运行后，可在该次运行页面下载 `feishu-gold-xau-quote` 文件产物。
3. 若原 Mac 任务继续向同群发送飞书提醒，两个定时任务会各发送一条。定时按周一至周五运行，遇到休市按卡片文案处理。GitHub 的调度可能延迟。

本地可通过 `python3 scripts/feishu_reminder.py --slot morning --dry-run` 离线预览卡片文案。验证时检查初次落盘、下次恢复并计算涨跌、旧报价不覆盖、固定参考汇率及测试运行对基准的影响。飞书请求超时后，先查看群记录，再决定是否手动重跑。

数据与单位出处见 [Gold API 说明](https://gold-api.com/faqs)、[NIST 贵金属单位换算](https://www.nist.gov/pml/owm/metric-si/unit-conversion/precious-metals-conversion-information)和[上金所 Au99.99 合约](https://www.sge.com.cn/cpfw/Product_service_details?cplx=7&parent_cplx=0&pro_id=793730879941324800)。运行配置见 [GitHub Actions 调度规则](https://docs.github.com/zh/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)、[文件产物接口](https://docs.github.com/en/rest/actions/artifacts)和[飞书自定义机器人使用指南](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot)。
