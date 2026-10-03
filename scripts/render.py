"""Renderer của Weekly Trending: content/<DATE>/ → site/ (chỉ stdlib, Python ≥ 3.9).

Template, CSS, JS nằm trong theme/ (người sửa; routine không động vào). Số liệu (sao, sao trong tuần, fork,
ngôn ngữ) lấy thẳng từ trending.json do crawl ghi; phần chữ lấy từ cards/*.json và highlights.txt.
Không dùng giờ hiện tại, nên build tất định: cùng content/ + theme/ → cùng từng byte.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from itertools import groupby
from pathlib import Path
from string import Template
from urllib.parse import urlsplit

WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
VN_OFFSET = timedelta(hours=7)  # Asia/Ho_Chi_Minh, không có giờ mùa hè
# Owner trên GitHub chỉ gồm chữ, số, '-' → '__' trong tên file luôn tách được owner/repo.
REPO_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+$")
COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{3,8}$")
CODE = re.compile(r"`([^`\n]+)`")
EMPTY_FEED_UPDATED = "1970-01-01T00:00:00Z"
# Icon nét (stroke) theo phong cách Feather (MIT); màu/kích thước do class .i trong style.css quyết định.
ICONS = {
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "up": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "fork": '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/>'
            '<path d="M6 8.5v1a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3v-1"/><line x1="12" y1="12.5" x2="12" y2="15.5"/>',
    "external": '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
                '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>',
}


class IssueError(Exception):
    """Dữ liệu một tuần trong content/ thiếu hoặc sai cấu trúc."""


@dataclass
class Repo:
    rank: int
    name: str  # owner/repo
    language: str
    language_color: str
    stars: int
    forks: int | None
    stars_week: int
    card: dict

    @property
    def url(self) -> str:
        return f"https://github.com/{self.name}"


@dataclass
class Issue:
    day: date
    fetched_at: datetime | None  # UTC
    repos: list[Repo]
    highlights: list[str]

    @property
    def start(self) -> date:
        return self.day - timedelta(days=6)

    @property
    def href(self) -> str:
        """Đường dẫn trang tuần, tương đối với gốc site (link ổn định theo ngày)."""
        return f"{self.day.isoformat()}/"


def slug(rank: int, name: str) -> str:
    """Tên file của một repo trong content/<DATE>/: '01-owner__repo'."""
    return f"{rank:02d}-{name.replace('/', '__')}"


def load_trending(folder: Path) -> dict:
    """content/<DATE>/trending.json đã kiểm tra cấu trúc (không kiểm tra số lượng repo)."""
    where = f"content/{folder.name}/trending.json"
    try:
        data = json.loads((folder / "trending.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise IssueError(f"thiếu {where}") from None
    except ValueError as err:  # gồm lỗi JSON và UTF-8
        raise IssueError(f"{where} không đọc được: {err}") from None
    if not isinstance(data, dict) or data.get("date") != folder.name:
        raise IssueError(f"{where}: 'date' phải là {folder.name}")
    repos = data.get("repos")
    if not isinstance(repos, list) or not repos:
        raise IssueError(f"{where}: thiếu danh sách 'repos'")
    for index, item in enumerate(repos, 1):
        name = item.get("repo") if isinstance(item, dict) else None
        if not isinstance(name, str) or not REPO_RE.match(name) or item.get("rank") != index:
            raise IssueError(f"{where}: repo thứ {index} sai 'rank' hoặc 'repo'")
        for key in ("stars", "stars_week", "forks"):
            value = item.get(key)
            if key == "forks" and value is None:
                continue
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise IssueError(f"{where}: {name} có '{key}' không phải số nguyên ≥ 0")
        stem = slug(index, name)
        if item.get("source") != f"sources/{stem}.md" or item.get("card") != f"cards/{stem}.json":
            raise IssueError(f"{where}: {name} cần source=sources/{stem}.md, card=cards/{stem}.json")
    return data


def read_highlights(folder: Path) -> list[str] | None:
    path = folder / "highlights.txt"
    if not path.is_file():
        return None
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_utc(text: str) -> datetime | None:
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None


def load_issue(folder: Path) -> Issue:
    """Một tuần đầy đủ (trending.json + mọi card + highlights.txt), sẵn sàng render."""
    data = load_trending(folder)
    repos = []
    for item in data["repos"]:
        where = f"content/{folder.name}/{item['card']}"
        try:
            card = json.loads((folder / item["card"]).read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise IssueError(f"thiếu {where}") from None
        except ValueError as err:  # gồm lỗi JSON và UTF-8
            raise IssueError(f"{where} không đọc được: {err}") from None
        if not isinstance(card, dict):
            raise IssueError(f"{where} phải là một object JSON")
        color = str(item.get("language_color") or "")
        repos.append(Repo(
            rank=item["rank"], name=item["repo"], language=str(item.get("language") or ""),
            language_color=color if COLOR_RE.match(color) else "",
            stars=item["stars"], forks=item.get("forks"), stars_week=item["stars_week"], card=card,
        ))
    highlights = read_highlights(folder)
    if not highlights:
        raise IssueError(f"thiếu content/{folder.name}/highlights.txt")
    return Issue(date.fromisoformat(folder.name), parse_utc(str(data.get("fetched_at", ""))), repos, highlights)


# ---------- định dạng ----------

def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def inline(text: str) -> str:
    """Escape HTML; chỉ nhận `code` làm định dạng inline."""
    return CODE.sub(r"<code>\1</code>", html.escape(text, quote=False))


def card_text(card: dict, key: str) -> str:
    value = card.get(key)
    return value.strip() if isinstance(value, str) else ""


def card_list(card: dict, key: str) -> list[str]:
    value = card.get(key)
    return [v.strip() for v in value if isinstance(v, str) and v.strip()] if isinstance(value, list) else []


def fmt_int(value: int) -> str:
    """12345 → '12.345' (dấu chấm phân cách hàng nghìn kiểu Việt)."""
    return f"{value:,}".replace(",", ".")


def week_label(issue: Issue) -> str:
    start, end = issue.start, issue.day
    if start.year == end.year:
        return f"{start:%d/%m} – {end:%d/%m/%Y}"
    return f"{start:%d/%m/%Y} – {end:%d/%m/%Y}"


def issue_title(issue: Issue) -> str:
    return f"Top {len(issue.repos)} GitHub Trending · {week_label(issue)}"


def fetched_label(issue: Issue) -> str:
    if issue.fetched_at is None:
        return ""
    local = issue.fetched_at + VN_OFFSET
    return f"{local:%H:%M} {local:%d/%m/%Y}"


def icon(name: str) -> str:
    return f'<svg class="i" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


# ---------- khối HTML ----------

def repo_card(repo: Repo) -> str:
    card = repo.card
    owner, name = repo.name.split("/", 1)
    stats = [
        f'<li class="stat-star" title="Tổng số sao trên GitHub">{icon("star")}{fmt_int(repo.stars)}</li>',
        f'<li class="stat-up" title="Số sao tăng trong tuần (GitHub Trending)">{icon("up")}'
        f"+{fmt_int(repo.stars_week)} tuần này</li>",
    ]
    if repo.forks is not None:
        stats.append(f'<li title="Số fork">{icon("fork")}{fmt_int(repo.forks)}</li>')
    if repo.language:
        style = f' style="--lang: {repo.language_color}"' if repo.language_color else ""
        stats.append(f'<li class="stat-lang" title="Ngôn ngữ chính"><i class="dot"{style}></i>{esc(repo.language)}</li>')
    uses = "".join(f"<li>{inline(use)}</li>" for use in card_list(card, "use_cases"))
    notable = card_text(card, "notable")
    notable_html = f'<p class="notable"><b>✨ Đáng chú ý</b><span>{inline(notable)}</span></p>' if notable else ""
    return (
        f'<article class="repo{" is-top" if repo.rank <= 3 else ""}" id="hang-{repo.rank}">'
        f'<header class="repo-head"><span class="rank" title="Hạng {repo.rank} trên GitHub Trending tuần">{repo.rank}</span>'
        f'<div class="repo-title"><h2 class="repo-name"><a href="{esc(repo.url)}" target="_blank" rel="noopener">'
        f'<span class="owner">{esc(owner)}/</span><span class="name">{esc(name)}</span>{icon("external")}</a></h2>'
        f'<p class="repo-tagline">{inline(card_text(card, "tagline"))}</p></div></header>'
        f'<ul class="repo-stats">{"".join(stats)}</ul>'
        f'<div class="repo-body">'
        f'<section><h3>💡 Để làm gì</h3><p>{inline(card_text(card, "summary"))}</p></section>'
        f'<section><h3>🛠️ Use case</h3><ul class="uses">{uses}</ul></section>'
        f'<section><h3>👥 Ai nên dùng</h3><p>{inline(card_text(card, "audience"))}</p></section>'
        f"{notable_html}</div></article>"
    )


def highlight_items(issue: Issue) -> str:
    return "".join(f"<li>{esc(line)}</li>" for line in issue.highlights)


def issue_card(issue: Issue, *, latest: bool) -> str:
    """Card của một tuần trên trang danh sách."""
    chips = "".join(
        f'<span class="chip"><b>#{repo.rank}</b>{esc(repo.name.split("/", 1)[1])}</span>' for repo in issue.repos[:3]
    )
    badge = '<span class="badge">Mới nhất</span>' if latest else ""
    return (
        f'<a class="issue{" is-latest" if latest else ""}" href="{esc(issue.href)}" aria-label="{esc(issue_title(issue))}">'
        f'<time class="issue-date" datetime="{issue.day.isoformat()}"><b>{issue.day.day:02d}</b>'
        f"<span>Th{issue.day.month}</span></time>"
        f'<div class="issue-body"><div class="issue-head"><h3>Tuần {esc(week_label(issue))}</h3>{badge}</div>'
        f'<ul class="issue-summary">{highlight_items(issue)}</ul>'
        f'<div class="issue-foot"><div class="chips">{chips}</div>'
        f'<span class="more">Xem {len(issue.repos)} repo →</span></div></div></a>'
    )


def issue_list(issues: list[Issue]) -> str:
    """Card các tuần trên trang danh sách, gom theo tháng. `issues` đã sắp mới nhất trước."""
    return "".join(
        f'<h2 class="section-title">Tháng {month} · {year}</h2><div class="issue-list">'
        + "".join(issue_card(issue, latest=issue is issues[0]) for issue in group) + "</div>"
        for (year, month), group in groupby(issues, key=lambda issue: (issue.day.year, issue.day.month))
    )


def feed_xml(issues: list[Issue], base: str) -> str:
    """Atom feed: id/link của entry = URL trang tuần (ổn định); updated = DATE 12:00Z (19:00 giờ VN)."""
    entries = []
    for issue in issues:
        url = f"{base}/{issue.href}"
        stamp = f"{issue.day.isoformat()}T12:00:00Z"
        items = "".join(
            f'<li><a href="{esc(repo.url)}">{esc(repo.name)}</a> — {esc(card_text(repo.card, "tagline"))}</li>'
            for repo in issue.repos
        )
        content = "<p>" + "<br>".join(esc(line) for line in issue.highlights) + f"</p><ol>{items}</ol>"
        entries.append(
            "  <entry>\n"
            f"    <id>{esc(url)}</id>\n"
            f"    <title>{esc(issue_title(issue))}</title>\n"
            f'    <link rel="alternate" type="text/html" href="{esc(url)}"/>\n'
            f"    <published>{stamp}</published>\n"
            f"    <updated>{stamp}</updated>\n"
            f'    <summary type="text">{esc(" · ".join(issue.highlights))}</summary>\n'
            f'    <content type="html">{esc(content)}</content>\n'
            "  </entry>\n"
        )
    updated = f"{issues[0].day.isoformat()}T12:00:00Z" if issues else EMPTY_FEED_UPDATED
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="vi">\n'
        f"  <id>{esc(base)}/</id>\n"
        "  <title>Weekly Trending · Top GitHub Trending mỗi tuần</title>\n"
        "  <subtitle>Bản tin tiếng Việt về các repo nổi bật nhất trên GitHub mỗi tuần: để làm gì, ai nên dùng, use case.</subtitle>\n"
        f'  <link rel="self" type="application/atom+xml" href="{esc(base)}/feed.xml"/>\n'
        f'  <link rel="alternate" type="text/html" href="{esc(base)}/"/>\n'
        f"  <updated>{updated}</updated>\n"
        "  <author><name>Weekly Trending</name></author>\n"
        + "".join(entries)
        + "</feed>\n"
    )


def render_site(issues: list[Issue], theme_dir: Path, *, base_url: str, retention_weeks: int) -> dict[str, bytes]:
    """Toàn bộ site/: {đường dẫn tương đối: nội dung}. Người gọi ghi ra đĩa và xoá file thừa."""
    issues = sorted(issues, key=lambda issue: issue.day, reverse=True)
    base = base_url.rstrip("/")
    pages: dict[str, bytes] = {}

    def template(name: str) -> Template:
        return Template((theme_dir / name).read_text(encoding="utf-8"))

    def put(path: str, text: str) -> None:
        pages[path] = text.encode("utf-8")

    def nav(other: Issue | None, label: str, css: str) -> str:
        if other is None:
            return "<span></span>"
        return f'<a class="{css}" href="../{esc(other.href)}">{label}</a>'

    issue_tpl = template("issue.html")
    for pos, issue in enumerate(issues):
        newer = issues[pos - 1] if pos > 0 else None
        older = issues[pos + 1] if pos + 1 < len(issues) else None
        fetched = fetched_label(issue)
        put(f"{issue.day.isoformat()}/index.html", issue_tpl.safe_substitute(
            title=esc(issue_title(issue)),
            description=esc(" · ".join(issue.highlights)),
            url=esc(f"{base}/{issue.href}"),
            week=esc(week_label(issue)),
            count=len(issue.repos),
            fetched=f" · số liệu GitHub lúc {esc(fetched)} (giờ VN)" if fetched else "",
            cards="".join(repo_card(repo) for repo in issue.repos),
            prev_link=nav(older, f"← Tuần {esc(week_label(older))}" if older else "", "prev"),
            next_link=nav(newer, f"Tuần {esc(week_label(newer))} →" if newer else "", "next"),
        ))

    latest = issues[0] if issues else None
    distinct = len({repo.name for issue in issues for repo in issue.repos})
    stats = "".join(f'<div class="stat"><b>{value}</b><span>{label}</span></div>' for value, label in [
        (len(issues), f"bản tin · giữ {retention_weeks} tuần"),
        (distinct, "repo khác nhau"),
        (f"{latest.day:%d/%m}" if latest else "—", "số mới nhất"),
    ])
    put("index.html", template("index.html").safe_substitute(
        description=esc(" · ".join(latest.highlights) if latest else "Top repo nổi bật trên GitHub mỗi tuần, tóm tắt bằng tiếng Việt."),
        url=esc(f"{base}/"),
        stats=stats,
        issue_cards=issue_list(issues) or (
            '<div class="empty"><div class="big">📭</div><p>Chưa có bản tin nào. '
            "Bản tin đầu tiên lên lúc 19:00 tối Chủ nhật (giờ VN).</p></div>"
        ),
        updated=f"{latest.day:%d/%m/%Y}" if latest else "—",
        retention_weeks=retention_weeks,
    ))
    put("404.html", template("404.html").safe_substitute(
        base=esc(urlsplit(base).path.rstrip("/") + "/"),
        retention_weeks=retention_weeks,
    ))
    put("feed.xml", feed_xml(issues, base))
    for asset in sorted((theme_dir / "assets").iterdir()):
        if asset.is_file() and not asset.name.startswith("."):
            pages[f"assets/{asset.name}"] = asset.read_bytes()
    return pages
