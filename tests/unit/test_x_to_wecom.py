import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))

from x_to_wecom import (
    XToWeComError,
    build_digest,
    fetch_recent_posts,
    main,
    send_to_wecom,
    split_markdown,
)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def raise_for_status(self):
        if self.status_code >= 400:
            from requests import HTTPError

            raise HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, get_payload=None, post_payload=None):
        self.get_payload = get_payload or {}
        self.post_payload = post_payload or {"errcode": 0, "errmsg": "ok"}
        self.get_calls = []
        self.post_calls = []

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        return FakeResponse(self.get_payload)

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        return FakeResponse(self.post_payload)


def sample_payload():
    return {
        "data": [
            {
                "id": "123",
                "author_id": "42",
                "created_at": "2026-09-19T01:02:03Z",
                "text": "Codex <launch> `today`",
                "public_metrics": {
                    "like_count": 7,
                    "repost_count": 3,
                    "reply_count": 2,
                },
            }
        ],
        "includes": {"users": [{"id": "42", "name": "OpenAI", "username": "OpenAI"}]},
    }


def test_fetch_recent_posts_uses_bearer_auth_and_current_fields():
    session = FakeSession(get_payload=sample_payload())

    result = fetch_recent_posts("secret", "from:OpenAI -is:retweet", 10, session=session)

    assert result == sample_payload()
    _, kwargs = session.get_calls[0]
    assert kwargs["headers"] == {"Authorization": "Bearer secret"}
    assert kwargs["params"]["post.fields"] == "author_id,created_at,lang,public_metrics,text"
    assert kwargs["params"]["expansions"] == "author_id"


def test_build_digest_includes_author_link_metrics_and_escaped_text():
    digest = build_digest(sample_payload(), "from:OpenAI")

    assert "OpenAI (@OpenAI)" in digest
    assert "Codex &lt;launch&gt; \\`today\\`" in digest
    assert "https://x.com/OpenAI/status/123" in digest
    assert "👍 7 · 🔁 3 · 💬 2" in digest


def test_build_digest_returns_none_when_no_posts_match():
    assert build_digest({"meta": {"result_count": 0}}, "nothing") is None


def test_split_markdown_preserves_utf8_and_byte_limit():
    content = "标题\n\n" + "中文内容" * 30

    chunks = split_markdown(content, max_bytes=40)

    assert "".join(chunks).replace("\n\n", "") == content.replace("\n\n", "")
    assert all(len(chunk.encode("utf-8")) <= 40 for chunk in chunks)


def test_send_to_wecom_uses_markdown_payload():
    session = FakeSession()

    send_to_wecom("https://example.test/hook", "hello", session=session)

    _, kwargs = session.post_calls[0]
    assert kwargs["json"] == {"msgtype": "markdown", "markdown": {"content": "hello"}}


def test_send_to_wecom_rejects_bot_error():
    session = FakeSession(post_payload={"errcode": 93000, "errmsg": "invalid webhook"})

    with pytest.raises(XToWeComError, match="invalid webhook"):
        send_to_wecom("https://example.test/hook", "hello", session=session)


def test_main_reports_missing_configuration(monkeypatch, capsys):
    for name in ("X_BEARER_TOKEN", "WECOM_X_WEBHOOK_URL", "WECOM_WEBHOOK_URL", "X_QUERY"):
        monkeypatch.delenv(name, raising=False)

    assert main() == 2
    assert "X_BEARER_TOKEN" in capsys.readouterr().err
