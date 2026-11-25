#!/usr/bin/env python3
"""Fetch recent X posts and push a compact digest to a WeCom bot."""

import html
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

import requests


X_RECENT_SEARCH_URL = "https://api.x.com/2/tweets/search/recent"
WECOM_MESSAGE_MAX_BYTES = 3500


class XToWeComError(RuntimeError):
    """Raised when X retrieval or WeCom delivery fails."""


def fetch_recent_posts(
    bearer_token: str,
    query: str,
    max_results: int,
    session: Any = requests,
) -> Dict[str, Any]:
    """Fetch recent posts matching an X API v2 query."""
    if not 10 <= max_results <= 100:
        raise ValueError("X_MAX_RESULTS 必须在 10 到 100 之间")

    try:
        response = session.get(
            X_RECENT_SEARCH_URL,
            headers={"Authorization": f"Bearer {bearer_token}"},
            params={
                "query": query,
                "max_results": max_results,
                "sort_order": "recency",
                "post.fields": "author_id,created_at,lang,public_metrics,text",
                "expansions": "author_id",
                "user.fields": "name,username",
            },
            timeout=30,
        )
    except requests.RequestException as exc:
        raise XToWeComError(f"X API 网络请求失败: {exc}") from exc
    try:
        response.raise_for_status()
    except requests.RequestException as exc:
        detail = _response_error_detail(response)
        raise XToWeComError(f"X API 请求失败（HTTP {response.status_code}）: {detail}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise XToWeComError("X API 返回了无法解析的 JSON") from exc

    if payload.get("errors") and not payload.get("data"):
        raise XToWeComError(f"X API 返回错误: {payload['errors']}")
    return payload


def build_digest(payload: Mapping[str, Any], query: str) -> Optional[str]:
    """Render an X search response as WeCom-flavoured Markdown."""
    posts = payload.get("data") or []
    if not posts:
        return None

    users = {
        user.get("id"): user
        for user in (payload.get("includes", {}).get("users") or [])
        if user.get("id")
    }
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections = [
        "# X 信息速递",
        f"> 查询：{_escape_markdown(query)}  ",
        f"> 生成时间：{generated_at}",
    ]

    for post in posts:
        user = users.get(post.get("author_id"), {})
        username = user.get("username") or "i"
        display_name = user.get("name") or username
        created_at = _format_created_at(post.get("created_at"))
        text = _escape_markdown(post.get("text") or "")
        metrics = post.get("public_metrics") or {}
        reposts = metrics.get("repost_count", metrics.get("retweet_count", 0))
        url = f"https://x.com/{username}/status/{post.get('id', '')}"
        sections.append(
            "\n".join(
                [
                    f"## {_escape_markdown(display_name)} (@{_escape_markdown(username)})",
                    f"> {created_at}",
                    text,
                    (
                        f"[查看原文]({url}) · 👍 {metrics.get('like_count', 0)}"
                        f" · 🔁 {reposts} · 💬 {metrics.get('reply_count', 0)}"
                    ),
                ]
            )
        )

    return "\n\n".join(sections)


def split_markdown(content: str, max_bytes: int = WECOM_MESSAGE_MAX_BYTES) -> List[str]:
    """Split Markdown on section boundaries without breaking UTF-8 characters."""
    if len(content.encode("utf-8")) <= max_bytes:
        return [content]

    blocks = content.split("\n\n")
    chunks: List[str] = []
    current = ""
    for block in blocks:
        candidate = f"{current}\n\n{block}" if current else block
        if len(candidate.encode("utf-8")) <= max_bytes:
            current = candidate
            continue

        if current:
            chunks.append(current)
        if len(block.encode("utf-8")) <= max_bytes:
            current = block
        else:
            block_chunks = _split_utf8(block, max_bytes)
            chunks.extend(block_chunks[:-1])
            current = block_chunks[-1]

    if current:
        chunks.append(current)
    return chunks


def send_to_wecom(webhook_url: str, content: str, session: Any = requests) -> None:
    """Send one or more Markdown messages to a WeCom group bot."""
    chunks = split_markdown(content)
    for index, chunk in enumerate(chunks, start=1):
        prefix = f"**X 信息速递（{index}/{len(chunks)}）**\n\n" if len(chunks) > 1 else ""
        try:
            response = session.post(
                webhook_url,
                json={"msgtype": "markdown", "markdown": {"content": prefix + chunk}},
                timeout=15,
            )
        except requests.RequestException as exc:
            raise XToWeComError(f"企业微信机器人网络请求失败: {exc}") from exc
        try:
            response.raise_for_status()
            result = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise XToWeComError(f"企业微信机器人请求失败（HTTP {response.status_code}）") from exc
        if result.get("errcode") != 0:
            raise XToWeComError(
                f"企业微信机器人返回错误: {result.get('errmsg', 'unknown error')}"
            )
        if index < len(chunks):
            time.sleep(1)


def main() -> int:
    bearer_token = os.environ.get("X_BEARER_TOKEN", "").strip()
    webhook_url = (
        os.environ.get("WECOM_X_WEBHOOK_URL")
        or os.environ.get("WECOM_WEBHOOK_URL")
        or ""
    ).strip()
    query = os.environ.get("X_QUERY", "").strip()

    missing = [
        name
        for name, value in (
            ("X_BEARER_TOKEN", bearer_token),
            ("WECOM_X_WEBHOOK_URL", webhook_url),
            ("X_QUERY", query),
        )
        if not value
    ]
    if missing:
        print(f"缺少必需配置: {', '.join(missing)}", file=sys.stderr)
        return 2

    try:
        max_results = int(os.environ.get("X_MAX_RESULTS", "10"))
        payload = fetch_recent_posts(bearer_token, query, max_results)
        digest = build_digest(payload, query)
        if digest is None:
            print("没有找到匹配的 X 信息，本次不推送。")
            return 0
        send_to_wecom(webhook_url, digest)
    except (ValueError, XToWeComError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"已向企业微信推送 {len(payload.get('data') or [])} 条 X 信息。")
    return 0


def _format_created_at(value: Optional[str]) -> str:
    if not value:
        return "时间未知"
    return value.replace("T", " ").replace("Z", " UTC")


def _escape_markdown(value: str) -> str:
    return html.escape(value, quote=False).replace("`", "\\`")


def _split_utf8(value: str, max_bytes: int) -> List[str]:
    chunks: List[str] = []
    remaining = value
    while remaining:
        raw = remaining.encode("utf-8")
        if len(raw) <= max_bytes:
            chunks.append(remaining)
            break
        chunk = raw[:max_bytes].decode("utf-8", errors="ignore")
        if not chunk:
            raise ValueError("max_bytes 太小，无法容纳一个 UTF-8 字符")
        chunks.append(chunk)
        remaining = remaining[len(chunk) :]
    return chunks


def _response_error_detail(response: Any) -> str:
    try:
        payload = response.json()
    except ValueError:
        return (response.text or "unknown error")[:500]
    return str(payload.get("detail") or payload.get("title") or payload.get("errors") or payload)[:500]


if __name__ == "__main__":
    sys.exit(main())
