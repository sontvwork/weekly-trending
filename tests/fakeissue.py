#!/usr/bin/env python3
"""Sinh một bản tin giả HỢP LỆ (qua được `trending.py validate`) trong <root>/content/<DATE>/ — không dùng mạng.

  python3 tests/fakeissue.py <root> <DATE> [số repo, mặc định 10]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CARD = {
    "tagline": "Công cụ dòng lệnh giúp tự động hoá các việc lặp đi lặp lại",
    "summary": "Repo giả dùng cho kiểm thử: một công cụ dòng lệnh nhỏ gọn giúp developer gom các thao tác "
               "lặp lại trong dự án thành vài lệnh ngắn, chạy được trên Python 3.12.",
    "use_cases": ["Tự động chạy kiểm tra trước khi commit", "Gom các script rời rạc thành một lệnh `tool run`"],
    "audience": "Developer muốn tiết kiệm thời gian cho việc vặt hằng ngày trong dự án.",
    "notable": "Không cần cấu hình phức tạp, cài xong là dùng được.",
    "refs": [],
}
HIGHLIGHTS = "🤖 Công cụ tự động hoá cho developer chiếm ưu thế trong tuần\n🧰 tool-1 dẫn đầu nhờ bộ lệnh gọn nhẹ\n"


def make_issue(root: Path, day: str, count: int = 10) -> Path:
    folder = root / "content" / day
    (folder / "sources").mkdir(parents=True, exist_ok=True)
    (folder / "cards").mkdir(parents=True, exist_ok=True)
    repos = []
    for rank in range(1, count + 1):
        name = f"owner{rank}/tool-{rank}"
        stem = f"{rank:02d}-{name.replace('/', '__')}"
        item = {
            "rank": rank, "repo": name, "url": f"https://github.com/{name}", "description": "A fake tool",
            "language": "Python", "language_color": "#3572A5", "stars": 1000 * rank, "forks": 10 * rank,
            "stars_week": 100 * rank, "readme_path": "README.md",
            "source": f"sources/{stem}.md", "card": f"cards/{stem}.json",
        }
        repos.append(item)
        (folder / item["source"]).write_text(f"# {name}\n\nREADME giả cho test. Hỗ trợ Python 3.12.\n", encoding="utf-8")
        card = dict(CARD, repo=name)
        (folder / item["card"]).write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    data = {"date": day, "source_url": "https://github.com/trending?since=weekly",
            "fetched_at": f"{day}T12:03:00Z", "repos": repos}
    (folder / "trending.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (folder / "highlights.txt").write_text(HIGHLIGHTS, encoding="utf-8")
    return folder


if __name__ == "__main__":
    make_issue(Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10)
