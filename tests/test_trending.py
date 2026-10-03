"""Test pipeline Weekly Trending (unittest, chỉ stdlib, không dùng mạng).

  python3 -m unittest discover -s tests -v

Mỗi test chạy CLI thật (scripts/trending.py) trên một bản sao tối thiểu của repo trong thư mục tạm.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

import fakeissue  # noqa: E402
import trending  # noqa: E402

OLD, NEW = "2026-09-20", "2026-09-27"


class Sandbox:
    """Bản sao scripts/, theme/, config/ trong thư mục tạm để chạy CLI không đụng repo thật."""

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="wt-test-"))
        for name in ("scripts", "theme", "config"):
            shutil.copytree(REPO / name, self.root / name, ignore=shutil.ignore_patterns("__pycache__"))

    def run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(self.root / "scripts" / "trending.py"), *args],
                              cwd=self.root, capture_output=True, text=True)

    def card(self, day: str, rank: int = 1) -> Path:
        return next((self.root / "content" / day / "cards").glob(f"{rank:02d}-*.json"))

    def edit_card(self, day: str, rank: int = 1, **changes: object) -> None:
        path = self.card(day, rank)
        card = json.loads(path.read_text(encoding="utf-8"))
        card.update(changes)
        path.write_text(json.dumps(card, ensure_ascii=False), encoding="utf-8")

    def site_bytes(self) -> dict[str, bytes]:
        site = self.root / "site"
        return {p.relative_to(site).as_posix(): p.read_bytes() for p in sorted(site.rglob("*")) if p.is_file()}

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


class ParseTrendingTest(unittest.TestCase):
    def test_fixture_page(self) -> None:
        page = (REPO / "tests" / "fixtures" / "trending-weekly.html").read_text(encoding="utf-8")
        repos = trending.parse_trending(page)
        self.assertEqual(len(repos), 10)
        self.assertTrue(all(repos))
        first = repos[0]
        self.assertEqual(first["rank"], 1)
        self.assertRegex(first["repo"], r"^[\w.-]+/[\w.-]+$")
        self.assertEqual(first["url"], f"https://github.com/{first['repo']}")
        for repo in repos:
            self.assertIsInstance(repo["stars"], int)
            self.assertIsInstance(repo["stars_week"], int)
            self.assertGreater(repo["stars_week"], 0)
        self.assertEqual([r["rank"] for r in repos], list(range(1, 11)))
        self.assertTrue(any(r["language_color"].startswith("#") for r in repos))

    def test_broken_article_is_none(self) -> None:
        page = '<article class="Box-row"><h2>không có link</h2> 12 stars this week</article>'
        self.assertEqual(trending.parse_trending(page), [None])

    def test_clean_readme_truncates(self) -> None:
        text, length, truncated = trending.clean_readme("a<!-- x -->b\n\n\n\nc" + "x" * 50, 20)
        self.assertTrue(truncated)
        self.assertEqual(length, len("ab\n\nc") + 50)
        self.assertTrue(text.startswith("ab\n\nc"))


class ImportTest(unittest.TestCase):
    """`import` lấy content/DATE/ từ branch dữ liệu của một origin cục bộ (repo bare trong thư mục tạm)."""

    def setUp(self) -> None:
        self.box = Sandbox()
        self.origin = self.box.root / "origin.git"
        self.git("init", "-q")
        self.git("init", "-q", "--bare", str(self.origin))
        self.git("remote", "add", "origin", str(self.origin))

    def tearDown(self) -> None:
        self.box.cleanup()

    def git(self, *args: str, cwd: Path | None = None) -> str:
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")
        return subprocess.run(["git", *args], cwd=cwd or self.box.root, env=env, check=True,
                              capture_output=True, text=True).stdout

    def push_data(self, day: str, extra: str = "") -> None:
        """Đẩy content/<day>/{trending.json, sources/} (như workflow Crawl) lên branch trending-data của origin."""
        work = self.box.root / "work"
        fakeissue.make_issue(work, day)
        shutil.rmtree(work / "content" / day / "cards")
        (work / "content" / day / "highlights.txt").unlink()
        if extra:
            (work / "content" / day / extra).write_text("x", encoding="utf-8")
        self.git("init", "-q", cwd=work)
        self.git("add", "content", cwd=work)
        self.git("commit", "-qm", f"crawl: {day}", cwd=work)
        self.git("push", "-q", str(self.origin), "HEAD:refs/heads/trending-data", cwd=work)

    def test_imports_issue(self) -> None:
        self.push_data(NEW)
        result = self.box.run("import", NEW, "--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        folder = self.box.root / "content" / NEW
        self.assertEqual(len(list((folder / "sources").glob("*.md"))), 10)
        self.assertTrue((folder / "cards").is_dir())
        self.assertEqual(self.box.run("tasks", NEW).returncode, 0)

    def test_requires_today_without_force(self) -> None:
        self.push_data(NEW)
        result = self.box.run("import", NEW)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("chỉ ghi được cho hôm nay", result.stderr)

    def test_missing_branch_or_date(self) -> None:
        result = self.box.run("import", NEW, "--force")
        self.assertIn("không lấy được branch trending-data", result.stderr)
        self.push_data(OLD)
        result = self.box.run("import", NEW, "--force")
        self.assertIn(f"chưa có content/{NEW}/", result.stderr)
        self.assertFalse((self.box.root / "content" / NEW).exists())

    def test_rejects_unexpected_file(self) -> None:
        self.push_data(NEW, extra="notes.txt")
        result = self.box.run("import", NEW, "--force")
        self.assertIn("file lạ", result.stderr)
        self.assertFalse((self.box.root / "content" / NEW).exists())


class ValidateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox()
        fakeissue.make_issue(self.box.root, NEW)

    def tearDown(self) -> None:
        self.box.cleanup()

    def assertInvalid(self, *needles: str, args: tuple[str, ...] = ()) -> None:
        result = self.box.run("validate", NEW, *args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        for needle in needles:
            self.assertIn(needle, result.stdout)

    def test_valid_issue(self) -> None:
        result = self.box.run("validate", NEW)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK", result.stdout)

    def test_cards_only_ignores_highlights(self) -> None:
        (self.box.root / "content" / NEW / "highlights.txt").unlink()
        self.assertEqual(self.box.run("validate", NEW, "--cards-only").returncode, 0)
        self.assertInvalid("thiếu highlights.txt")

    def test_english_card(self) -> None:
        self.box.edit_card(NEW, tagline="A command line tool for chores", summary="This is a command line tool " * 4,
                           audience="Developers who like automation", notable="",
                           use_cases=["Run checks before commits", "Bundle scripts into one command"])
        self.assertInvalid("tiếng Việt có dấu")

    def test_url_and_markdown(self) -> None:
        self.box.edit_card(NEW, notable="Xem thêm tại https://example.com nhé")
        self.box.edit_card(NEW, 2, notable="Hỗ trợ **rất** nhiều định dạng")
        self.assertInvalid("không được có URL", "không dùng markdown")

    def test_html_only_outside_code(self) -> None:
        self.box.edit_card(NEW, notable="Dùng lệnh `tool add <path>` để thêm thư mục mới")
        self.assertEqual(self.box.run("validate", NEW).returncode, 0)
        self.box.edit_card(NEW, notable="Hiển thị <b>đậm</b> trong giao diện dòng lệnh")
        self.assertInvalid("không được có URL, HTML")

    def test_star_numbers_forbidden(self) -> None:
        self.box.edit_card(NEW, notable="Đã vượt mốc 1.000 sao chỉ sau vài ngày")
        self.assertInvalid("không ghi số sao/fork")

    def test_unknown_number_is_error_without_refs(self) -> None:
        self.box.edit_card(NEW, notable="Hỗ trợ tới 42 ngôn ngữ lập trình khác nhau")
        self.assertInvalid("số 42 không có trong dữ liệu")

    def test_unknown_number_is_warning_with_refs(self) -> None:
        self.box.edit_card(NEW, notable="Hỗ trợ tới 42 ngôn ngữ lập trình khác nhau",
                           refs=["https://github.com/owner1/tool-1/blob/main/docs/langs.md"])
        result = self.box.run("validate", NEW)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("cảnh báo", result.stdout)

    def test_known_number_formats(self) -> None:
        self.box.edit_card(NEW, notable="Chạy tốt trên Python 3.12 mà không cần cài thêm gì")
        self.assertEqual(self.box.run("validate", NEW).returncode, 0)

    def test_refs_must_point_to_same_repo(self) -> None:
        self.box.edit_card(NEW, refs=["https://github.com/someone/else/blob/main/README.md"])
        self.assertInvalid("refs chỉ được trỏ vào chính owner1/tool-1")

    def test_wrong_repo_and_extra_key(self) -> None:
        self.box.edit_card(NEW, repo="owner9/tool-9", stars=5)
        self.assertInvalid("'repo' phải là 'owner1/tool-1'", "key không hợp lệ")

    def test_highlights_rules(self) -> None:
        highlights = self.box.root / "content" / NEW / "highlights.txt"
        highlights.write_text("Không có emoji ở đầu dòng\n🔥 Có **markdown** ở đây\n🚀 Tăng 99.999 sao trong tuần\n",
                              encoding="utf-8")
        self.assertInvalid("mở đầu bằng đúng 1 emoji", "chỉ dùng plain text", "số 99.999 không có")

    def test_highlights_may_cite_week_numbers(self) -> None:
        (self.box.root / "content" / NEW / "highlights.txt").write_text(
            "🚀 tool-10 dẫn đầu với 1.000 sao mới trong tuần\n", encoding="utf-8")
        self.assertEqual(self.box.run("validate", NEW).returncode, 0)

    def test_unexpected_file(self) -> None:
        (self.box.root / "content" / NEW / "notes.md").write_text("ghi chú", encoding="utf-8")
        self.assertInvalid("file lạ trong content/")

    def test_tasks(self) -> None:
        result = self.box.run("tasks", NEW)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 10)
        self.assertEqual(lines[0], f"01|owner1/tool-1|content/{NEW}/sources/01-owner1__tool-1.md|"
                                   f"content/{NEW}/cards/01-owner1__tool-1.json")


class PruneTest(unittest.TestCase):
    def test_retention_cutoff(self) -> None:
        box = Sandbox()
        try:
            # RETENTION_WEEKS=20 → mốc = 2026-09-27 − 139 ngày = 2026-05-11
            for day in ("2026-05-03", "2026-05-10", "2026-05-17", NEW):
                fakeissue.make_issue(box.root, day, 2)
                (box.root / "site" / day).mkdir(parents=True)
                (box.root / "site" / day / "index.html").write_text("x", encoding="utf-8")
            result = box.run("prune", NEW)
            self.assertEqual(result.returncode, 0, result.stderr)
            remaining = sorted(p.name for p in (box.root / "content").iterdir())
            self.assertEqual(remaining, ["2026-05-17", NEW])
            self.assertEqual(sorted(p.name for p in (box.root / "site").iterdir()), ["2026-05-17", NEW])
            self.assertIn("xoá 4 thư mục", result.stdout)  # 05-03 và 05-10, cả content/ lẫn site/
            self.assertIn("xoá 0 thư mục", box.run("prune", NEW).stdout)  # chạy lại không xoá thêm
        finally:
            box.cleanup()


class BuildTest(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox()
        fakeissue.make_issue(self.box.root, OLD)
        fakeissue.make_issue(self.box.root, NEW)

    def tearDown(self) -> None:
        self.box.cleanup()

    def test_build_is_deterministic(self) -> None:
        first = self.box.run("build", NEW)
        self.assertEqual(first.returncode, 0, first.stderr)
        before = self.box.site_bytes()
        second = self.box.run("build", NEW)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(before, self.box.site_bytes())
        for page in ("index.html", "404.html", "feed.xml", "assets/style.css", "assets/theme.js",
                     "assets/favicon.svg", f"{OLD}/index.html", f"{NEW}/index.html"):
            self.assertIn(page, before)

    def test_pages_content(self) -> None:
        self.assertEqual(self.box.run("build", NEW).returncode, 0)
        site = self.box.root / "site"
        index = (site / "index.html").read_text(encoding="utf-8")
        self.assertIn(f'href="{NEW}/"', index)
        self.assertIn(f'href="{OLD}/"', index)
        self.assertIn("Mới nhất", index)
        week = (site / NEW / "index.html").read_text(encoding="utf-8")
        self.assertIn("Top 10 GitHub Trending", week)
        self.assertIn("21/09 – 27/09/2026", week)
        self.assertIn("+1.000 tuần này", week)  # repo hạng 10: 100 × 10 sao/tuần, định dạng Việt
        self.assertIn("<code>tool run</code>", week)
        self.assertIn(f'href="../{OLD}/"', week)
        self.assertIn('<base href="/weekly-trending/">', (site / "404.html").read_text(encoding="utf-8"))
        feed = ET.parse(site / "feed.xml").getroot()
        entries = feed.findall("{http://www.w3.org/2005/Atom}entry")
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].findtext("{http://www.w3.org/2005/Atom}id"),
                         f"https://sontvwork.github.io/weekly-trending/{NEW}/")

    def test_escapes_third_party_text(self) -> None:
        self.box.edit_card(NEW, tagline="Hiển thị <script>alert(1)</script> an toàn")
        self.assertEqual(self.box.run("build", NEW).returncode, 0)
        week = (self.box.root / "site" / NEW / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("<script>alert", week)
        self.assertIn("&lt;script&gt;", week)

    def test_removes_stale_files(self) -> None:
        stale = self.box.root / "site" / "2020-01-05" / "index.html"
        stale.parent.mkdir(parents=True)
        stale.write_text("cũ", encoding="utf-8")
        self.assertEqual(self.box.run("build", NEW).returncode, 0)
        self.assertFalse(stale.parent.exists())

    def test_incomplete_issue_fails(self) -> None:
        self.box.card(OLD, 3).unlink()
        result = self.box.run("build", NEW)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f"thiếu content/{OLD}/cards/03-", result.stderr)

    def test_empty_site_without_date(self) -> None:
        box = Sandbox()
        try:
            result = box.run("build")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Chưa có bản tin nào", (box.root / "site" / "index.html").read_text(encoding="utf-8"))
            feed = ET.parse(box.root / "site" / "feed.xml").getroot()
            self.assertEqual(feed.findall("{http://www.w3.org/2005/Atom}entry"), [])
            self.assertNotEqual(box.run("build", NEW).returncode, 0)  # có DATE thì bản tin phải tồn tại
        finally:
            box.cleanup()

    def test_message_and_link(self) -> None:
        self.assertEqual(self.box.run("build", NEW).returncode, 0)
        lines = self.box.run("message", NEW).stdout.splitlines()
        self.assertEqual(lines[0], "*Top 10 GitHub Trending · 21/09 – 27/09/2026*")
        self.assertEqual(lines[1], fakeissue.HIGHLIGHTS.splitlines()[0])
        self.assertEqual(lines[-1], f"🔗 https://sontvwork.github.io/weekly-trending/{NEW}/")


class FenceTest(unittest.TestCase):
    def decide(self, event: dict, **env: str) -> str:
        environ = {k: v for k, v in os.environ.items() if k not in ("WT_FENCE", "CLAUDE_CODE_REMOTE")}
        environ.update(env)
        result = subprocess.run([sys.executable, str(REPO / "scripts" / "fence.py")], input=json.dumps(event),
                                capture_output=True, text=True, env=environ)
        self.assertEqual(result.returncode, 0, result.stderr)
        return "deny" if '"deny"' in result.stdout else "allow"

    def write(self, path: str) -> dict:
        return {"tool_name": "Write", "tool_input": {"file_path": path}, "cwd": str(REPO)}

    def test_disabled_by_default(self) -> None:
        self.assertEqual(self.decide(self.write(str(REPO / "scripts" / "x.py"))), "allow")
        self.assertEqual(self.decide(self.write(str(REPO / "scripts" / "x.py")), CLAUDE_CODE_REMOTE="true",
                                     WT_FENCE="0"), "allow")

    def test_writes(self) -> None:
        on = {"WT_FENCE": "1"}
        self.assertEqual(self.decide(self.write(str(REPO / "content" / NEW / "cards" / "a.json")), **on), "allow")
        self.assertEqual(self.decide(self.write("content/x/highlights.txt"), **on), "allow")
        self.assertEqual(self.decide(self.write(str(REPO / ".cache" / "note.md")), **on), "allow")
        self.assertEqual(self.decide(self.write(str(REPO / "scripts" / "guard.sh")), **on), "deny")
        self.assertEqual(self.decide(self.write(str(REPO / "content")), **on), "deny")
        self.assertEqual(self.decide(self.write(str(REPO / "content" / ".." / "README.md")), **on), "deny")
        self.assertEqual(self.decide(self.write("/tmp/outside.txt"), **on), "deny")
        self.assertEqual(self.decide(self.write(str(REPO / "site" / "index.html")), CLAUDE_CODE_REMOTE="true"),
                         "deny")

    def test_web(self) -> None:
        on = {"WT_FENCE": "1"}
        fetch = lambda url: {"tool_name": "WebFetch", "tool_input": {"url": url, "prompt": "x"}}  # noqa: E731
        self.assertEqual(self.decide(fetch("https://github.com/a/b/tree/main/docs"), **on), "allow")
        self.assertEqual(self.decide(fetch("https://raw.githubusercontent.com/a/b/HEAD/README.md"), **on), "allow")
        self.assertEqual(self.decide(fetch("https://example.com/?q=1"), **on), "deny")
        self.assertEqual(self.decide(fetch("https://github.com.evil.io/a"), **on), "deny")
        self.assertEqual(self.decide({"tool_name": "WebSearch", "tool_input": {"query": "x"}}, **on), "deny")
        self.assertEqual(self.decide({"tool_name": "Read", "tool_input": {"file_path": "/etc/hosts"}}, **on), "allow")


if __name__ == "__main__":
    unittest.main()
