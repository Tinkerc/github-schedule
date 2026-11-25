import io
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / 'scripts'))

import feishu_reminder as reminder


@pytest.fixture
def quote_opener(monkeypatch):
    opener = Mock()
    monkeypatch.setattr(reminder.request, 'build_opener', Mock(return_value=opener))
    return opener.open


def quote_response(timestamp, price):
    quote = {
        'symbol': 'XAU',
        'currency': 'USD',
        'price': price,
        'updatedAt': timestamp.isoformat().replace('+00:00', 'Z'),
    }
    return io.BytesIO(json.dumps(quote).encode())


@pytest.fixture
def feishu_send(monkeypatch):
    monkeypatch.setenv('FEISHU_WEBHOOK_URL', 'https://open.feishu.cn/open-apis/bot/v2/hook/fake-hook')
    monkeypatch.setenv('FEISHU_SECRET', 'fake-secret')
    send = Mock()
    monkeypatch.setattr(reminder, 'send', send)
    return send


@pytest.mark.parametrize('next_price,expected_delta', [(3547.85, '+3.85'), (3540.15, '-3.85')])
def test_observations_save_and_compare_consecutive_quotes(
    quote_opener, feishu_send, monkeypatch, tmp_path, next_price, expected_delta,
):
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    first_time = timestamp - timedelta(minutes=1)
    quote_opener.side_effect = [quote_response(first_time, 3544), quote_response(timestamp, next_price)]
    baseline = tmp_path / 'initial' / 'quote.json'
    current = tmp_path / 'current' / 'quote.json'

    monkeypatch.setattr(sys, 'argv', ['feishu_reminder.py', '--cron', '30 1 * * 1-5', '--save-quote', str(baseline)])
    assert reminder.main() == 0
    assert '暂无上次有效报价' in feishu_send.call_args.args[2]['card']['elements'][0]['text']['content']
    assert json.loads(baseline.read_text()) == {
        'symbol': 'XAU', 'currency': 'USD', 'price': '3544', 'updatedAt': first_time.isoformat(),
    }

    monkeypatch.setattr(sys, 'argv', [
        'feishu_reminder.py', '--slot', 'afternoon', '--previous-quote', str(baseline), '--save-quote', str(current),
    ])
    assert reminder.main() == 0
    body = feishu_send.call_args.args[2]['card']['elements'][0]['text']['content']
    assert f'{next_price:,.2f} 美元/金衡盎司' in body
    assert f'{expected_delta} 美元/金衡盎司（{expected_delta[0]}0.11%）' in body
    assert first_time.astimezone(reminder.SHANGHAI_TZ).strftime('%Y-%m-%d %H:%M:%S') in body
    assert '6.6964' in body and '含境内外金价差' in body
    assert json.loads(current.read_text())['price'] == str(next_price)
    for call in quote_opener.call_args_list:
        assert call.args[0].full_url == reminder.GOLD_QUOTE_URL
        assert call.kwargs['timeout'] == 8


@pytest.mark.parametrize('age_minutes', [1, 2, 6])
def test_old_or_duplicate_quotes_do_not_replace_baseline(quote_opener, monkeypatch, feishu_send, tmp_path, age_minutes):
    timestamp = datetime.now(timezone.utc)
    baseline = tmp_path / 'quote.json'
    previous = quote_response(timestamp - timedelta(minutes=1), 3544).getvalue()
    baseline.write_bytes(previous)
    quote_opener.return_value = quote_response(timestamp - timedelta(minutes=age_minutes), 3547.85)
    monkeypatch.setattr(sys, 'argv', [
        'feishu_reminder.py', '--slot', 'morning', '--previous-quote', str(baseline), '--save-quote', str(baseline),
    ])

    assert reminder.main() == 0

    body = feishu_send.call_args.args[2]['card']['elements'][0]['text']['content']
    assert '暂不计算涨跌' in body
    assert baseline.read_bytes() == previous


def test_reminder_still_sends_when_quote_fails(quote_opener, monkeypatch, feishu_send, tmp_path):
    quote_opener.side_effect = TimeoutError('source offline')
    output = tmp_path / 'quote.json'
    monkeypatch.setattr(sys, 'argv', ['feishu_reminder.py', '--slot', 'morning', '--save-quote', str(output)])

    assert reminder.main() == 0

    body = feishu_send.call_args.args[2]['card']['elements'][0]['text']['content']
    assert '伦敦金行情暂不可用' in body and '6.6964' in body
    assert not output.exists()
    quote_opener.assert_called_once()


def test_manual_test_reads_previous_quote_without_saving(quote_opener, monkeypatch, feishu_send, tmp_path):
    timestamp = datetime.now(timezone.utc)
    baseline = tmp_path / 'previous.json'
    baseline.write_bytes(quote_response(timestamp - timedelta(minutes=1), 3544).getvalue())
    output = tmp_path / 'quote.json'
    quote_opener.return_value = quote_response(timestamp, 3547.85)
    monkeypatch.setattr(sys, 'argv', [
        'feishu_reminder.py', '--slot', 'test', '--previous-quote', str(baseline), '--save-quote', str(output),
    ])

    assert reminder.main() == 0

    assert '+0.11%' in feishu_send.call_args.args[2]['card']['elements'][0]['text']['content']
    assert not output.exists()


def test_snapshot_survives_feishu_failure(quote_opener, monkeypatch, feishu_send, tmp_path):
    quote_opener.return_value = quote_response(datetime.now(timezone.utc), 3547.85)
    feishu_send.side_effect = ValueError('bot rejected')
    output = tmp_path / 'quote.json'
    monkeypatch.setattr(sys, 'argv', ['feishu_reminder.py', '--slot', 'morning', '--save-quote', str(output)])

    assert reminder.main() == 1
    assert json.loads(output.read_text())['price'] == '3547.85'


def test_dry_run_does_not_fetch_quotes(quote_opener, monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['feishu_reminder.py', '--slot', 'morning', '--dry-run'])

    assert reminder.main() == 0

    payload = json.loads(capsys.readouterr().out)
    body = payload['card']['elements'][0]['text']['content']
    assert reminder.REMINDERS['morning'][1] in body
    assert '6.6964' in body
    quote_opener.assert_not_called()
