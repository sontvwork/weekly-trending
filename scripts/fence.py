#!/usr/bin/env python3
"""Hook PreToolUse rào công cụ của routine Weekly Trending (chỉ stdlib, khai báo trong .claude/settings.json).

Bật khi WT_FENCE=1, hoặc trong cloud session (CLAUDE_CODE_REMOTE=true) trừ khi WT_FENCE=0. Phiên dev local
không đặt biến nào nên hook không làm gì. Khi bật, áp cho cả agent chính lẫn sub-agent:
  - Write/Edit/MultiEdit/NotebookEdit: chỉ được ghi trong content/ hoặc .cache/ của repo;
  - WebFetch: chỉ tới github.com và raw.githubusercontent.com;
  - WebSearch: chặn (dữ liệu chỉ lấy từ GitHub).
Đây là lớp rào thêm cho nội dung bên thứ ba (README); guard.sh vẫn là chốt chặn cuối trước commit/push.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
WRITABLE = ("content", ".cache")
WEB_HOSTS = {"github.com", "raw.githubusercontent.com"}
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def enabled() -> bool:
    flag = os.environ.get("WT_FENCE", "")
    if flag in ("0", "1"):
        return flag == "1"
    return os.environ.get("CLAUDE_CODE_REMOTE", "").lower() == "true"


def deny_reason(event: dict) -> str | None:
    """Lý do chặn tool call, hoặc None nếu cho phép."""
    tool = event.get("tool_name", "")
    args = event.get("tool_input") or {}
    if tool in WRITE_TOOLS:
        raw = str(args.get("file_path") or args.get("notebook_path") or "")
        if not raw:
            return "thiếu đường dẫn file"
        path = Path(raw).expanduser()
        if not path.is_absolute():
            path = Path(event.get("cwd") or ROOT) / path
        path = path.resolve()  # đi theo symlink: content/x → scripts/ vẫn bị chặn
        try:
            parts = path.relative_to(ROOT.resolve()).parts
        except ValueError:
            return f"chỉ được ghi trong content/ hoặc .cache/ của repo (đang ghi {path})"
        if len(parts) > 1 and parts[0] in WRITABLE:
            return None
        return f"chỉ được ghi trong content/ hoặc .cache/ (đang ghi {'/'.join(parts) or '.'})"
    if tool == "WebFetch":
        url = urlsplit(str(args.get("url", "")))
        if url.scheme in ("http", "https") and (url.hostname or "").lower() in WEB_HOSTS:
            return None
        return f"WebFetch chỉ được gọi tới github.com hoặc raw.githubusercontent.com (đang gọi {args.get('url')!r})"
    if tool == "WebSearch":
        return "WebSearch bị tắt: dữ liệu chỉ được lấy từ GitHub"
    return None


def main() -> None:
    if not enabled():
        return
    try:
        event = json.load(sys.stdin)
    except ValueError:
        print("fence.py: input của hook không phải JSON — chặn để an toàn", file=sys.stderr)
        sys.exit(2)
    reason = deny_reason(event if isinstance(event, dict) else {})
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"[fence] {reason}",
        }}, ensure_ascii=False))


if __name__ == "__main__":
    main()
