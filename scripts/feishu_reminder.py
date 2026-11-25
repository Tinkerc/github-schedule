#!/usr/bin/env python3
"""获取国际现货黄金参考报价并发送飞书黄金观察提醒。"""

import argparse
import base64
import hmac
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, DecimalException
from http.client import HTTPException
from pathlib import Path
from urllib import error, request
from zoneinfo import ZoneInfo


REMINDERS = {
    'morning': (
        '9:30 早间观察提醒',
        '先确认渠道开放，检查隔夜变化及风险或减仓条件，与上一交易日21:00报价比较；±2%只作复核。不补仓，无触发则记录后结束。',
    ),
    'afternoon': (
        '15:00 观察提醒',
        '查看日间变化及关键价位，与上一交易日21:00报价比较；±2%只作复核。先确认渠道开放，无触发则记录后结束，不因提醒而交易。',
    ),
    'evening': (
        '21:00 记录提醒',
        '与上一交易日21:00报价比较，±2%只作复核；记录同渠道金价、实际时间与来源，作为下一交易日基准。休市则注明，不因提醒而交易。',
    ),
    'test': (
        '飞书通知测试',
        '这是一条 GitHub Actions 测试消息。定时提醒在周一至周五北京时间 9:30、15:00、21:00 发送。',
    ),
}

SLOTS_BY_CRON = {
    '30 1 * * 1-5': 'morning',
    '0 7 * * 1-5': 'afternoon',
    '0 13 * * 1-5': 'evening',
}

GOLD_QUOTE_URL = 'https://api.gold-api.com/price/XAU'
SGE_DELAYED_QUOTES = '[查看上金所 Au99.99 延时行情](https://www.sge.com.cn/sjzx/yshqbg)'
GRAMS_PER_TROY_OUNCE = Decimal('31.1034768')
SHANGHAI_TZ = ZoneInfo('Asia/Shanghai')
ANCHOR_XAU_USD = Decimal('3544')
ANCHOR_AU9999_CNY_PER_GRAM = Decimal('763')
REFERENCE_RATE = ANCHOR_AU9999_CNY_PER_GRAM * GRAMS_PER_TROY_OUNCE / ANCHOR_XAU_USD
REFERENCE_RATE_TEXT = (
    f'**固定锚点参考汇率** 1 美元 ≈ {REFERENCE_RATE:.4f} 元'
    f'（伦敦金 {ANCHOR_XAU_USD} 美元/金衡盎司，Au99.99 {ANCHOR_AU9999_CNY_PER_GRAM} 元/克，含境内外金价差）'
)


@dataclass(frozen=True)
class GoldQuote:
    price: Decimal
    updated_at: datetime


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def read_gold_quote(stream):
    data = json.load(stream, parse_float=Decimal, parse_int=Decimal)
    if not isinstance(data, dict) or data.get('symbol') != 'XAU' or data.get('currency') != 'USD':
        raise ValueError('需要 XAU/USD 报价')

    raw_price = data['price']
    if not isinstance(raw_price, (Decimal, str)):
        raise ValueError('报价数值无效')
    price = Decimal(raw_price)
    if not price.is_finite() or price <= 0:
        raise ValueError('报价数值无效')
    updated_at = datetime.fromisoformat(data['updatedAt'])
    if updated_at.utcoffset() is None:
        raise ValueError('报价时间缺少时区')
    return GoldQuote(price, updated_at.astimezone(timezone.utc))


def fetch_gold_quote():
    req = request.Request(GOLD_QUOTE_URL, headers={'Accept': 'application/json'})
    with request.build_opener(NoRedirect).open(req, timeout=8) as response:
        return read_gold_quote(response)


def load_previous_quote(path):
    if path is None:
        return None
    try:
        with path.open(encoding='utf-8') as stream:
            return read_gold_quote(stream)
    except FileNotFoundError:
        return None
    except (OSError, KeyError, TypeError, ValueError, DecimalException):
        print('无法读取上次有效的 XAU/USD 快照。', file=sys.stderr)
        return None


def save_gold_quote(path, quote):
    snapshot = {
        'symbol': 'XAU',
        'currency': 'USD',
        'price': str(quote.price),
        'updatedAt': quote.updated_at.isoformat(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f'{path.name}.tmp')
    temporary.write_text(json.dumps(snapshot, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def beijing_time(quote):
    return quote.updated_at.astimezone(SHANGHAI_TZ).strftime('%Y-%m-%d %H:%M:%S')


def summarize_gold_quote(previous):
    try:
        quote = fetch_gold_quote()
        age = datetime.now(timezone.utc) - quote.updated_at
        if age < -timedelta(minutes=1):
            raise ValueError('报价时间晚于当前时间')
    except (OSError, HTTPException, KeyError, TypeError, ValueError, DecimalException):
        return '伦敦金行情暂不可用（Gold API）。', None

    lines = [
        f'**伦敦金（XAU/USD）** {quote.price:,.2f} 美元/金衡盎司',
        f'来源 Gold API · 采集于北京时间 {beijing_time(quote)}',
    ]
    if age > timedelta(minutes=5):
        lines.append('报价已超过 5 分钟，暂不计算涨跌。')
        return '\n'.join(lines), None
    if previous is None:
        lines.append('暂无上次有效报价可比较。')
    elif quote.updated_at <= previous.updated_at:
        lines.append('采集时间未晚于上次记录，暂不计算涨跌。')
        return '\n'.join(lines), None
    else:
        change = quote.price - previous.price
        percent = change / previous.price * 100
        lines.append(f'**较上次采集** {change:+,.2f} 美元/金衡盎司（{percent:+.2f}%）')
        lines.append(f'上次报价 {previous.price:,.2f} 美元/金衡盎司 · 北京时间 {beijing_time(previous)}')
    return '\n'.join(lines), quote


def send(webhook, secret, payload):
    timestamp = str(int(time.time()))
    key = f'{timestamp}\n{secret}'.encode('utf-8')
    digest = hmac.digest(key, b'', 'sha256')
    payload = {**payload, 'timestamp': timestamp, 'sign': base64.b64encode(digest).decode('ascii')}
    req = request.Request(
        webhook,
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='POST',
    )

    try:
        with request.build_opener(NoRedirect).open(req, timeout=15) as response:
            result = json.load(response)
    except error.HTTPError as exc:
        raise ValueError(f'飞书 HTTP 错误（状态码 {exc.code}）') from None
    except (OSError, HTTPException):
        raise ValueError('飞书请求失败或超时，接收状态不确定') from None
    except (json.JSONDecodeError, UnicodeError):
        raise ValueError('飞书响应无法解析，接收状态不确定') from None

    code = result.get('code', result.get('StatusCode')) if isinstance(result, dict) else None
    if type(code) is not int:
        raise ValueError('飞书响应缺少有效业务状态码，接收状态不确定')
    if code != 0:
        raise ValueError(f'飞书拒绝消息（业务码 {code}）')


def build_card(subtitle, text):
    return {
        'msg_type': 'interactive',
        'card': {
            'config': {'wide_screen_mode': True},
            'header': {
                'template': 'orange',
                'title': {'tag': 'plain_text', 'content': f'黄金观察提醒｜{subtitle}'},
            },
            'elements': [{'tag': 'div', 'text': {'tag': 'lark_md', 'content': text}}],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    trigger = parser.add_mutually_exclusive_group(required=True)
    trigger.add_argument('--slot', choices=REMINDERS)
    trigger.add_argument('--cron', choices=SLOTS_BY_CRON)
    parser.add_argument('--previous-quote', type=Path, help='上次有效的 XAU/USD JSON 快照')
    parser.add_argument('--save-quote', type=Path, help='新快照的 JSON 输出路径')
    parser.add_argument('--dry-run', action='store_true', help='离线预览基础卡片')
    args = parser.parse_args()

    slot = args.slot or SLOTS_BY_CRON[args.cron]
    subtitle, text = REMINDERS[slot]
    body = f'{REFERENCE_RATE_TEXT}\n{SGE_DELAYED_QUOTES}\n\n**观察事项**\n{text}'
    if args.dry_run:
        print(json.dumps(build_card(subtitle, body), ensure_ascii=False))
        return 0

    webhook = os.environ.get('FEISHU_WEBHOOK_URL', '').strip()
    secret = os.environ.get('FEISHU_SECRET', '').strip()
    if not re.fullmatch(r'https://open\.feishu\.cn/open-apis/bot/v2/hook/[A-Za-z0-9-]+', webhook):
        print('请通过 FEISHU_WEBHOOK_URL 配置有效的飞书机器人 webhook 地址。', file=sys.stderr)
        return 1
    if not secret:
        print('请通过 FEISHU_SECRET 配置飞书机器人签名密钥。', file=sys.stderr)
        return 1

    summary, snapshot = summarize_gold_quote(load_previous_quote(args.previous_quote))
    snapshot_failed = False
    if snapshot is not None and args.save_quote is not None and slot != 'test':
        try:
            save_gold_quote(args.save_quote, snapshot)
        except OSError:
            print('无法保存新的 XAU/USD 快照。', file=sys.stderr)
            snapshot_failed = True

    try:
        send(webhook, secret, build_card(subtitle, f'{summary}\n\n{body}'))
    except ValueError as exc:
        print(f'发送失败：{exc}', file=sys.stderr)
        return 1
    print('飞书接口已确认接收消息。')
    return int(snapshot_failed)


if __name__ == '__main__':
    sys.exit(main())
