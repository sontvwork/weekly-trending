#!/usr/bin/env bash
# Chạy lại từng bước của pipeline ở LOCAL để test. KHÔNG commit, KHÔNG push → guard chỉ cảnh báo, không chặn
# (code chưa commit vẫn chạy được). Publish thật vẫn đi qua publish.sh sau khi đã commit + push code bảo trì.
#
#   dev.sh <DATE> <STEP>|<FROM>..<TO> [--send]      STEP theo thứ tự: crawl → write → build → notify
#
#   dev.sh 2026-10-04 crawl..notify   # cả pipeline (crawl chỉ nhận DATE = hôm nay theo giờ VN)
#   dev.sh 2026-10-04 write..notify   # đổi văn phong: viết lại card + highlights từ dữ liệu đã crawl
#   dev.sh 2026-10-04 build           # validate → prune → build site/ → guard (chỉ cảnh báo)
#   dev.sh 2026-10-04 notify --send   # chỉ gửi lại tin Google Chat thật (tiền tố "[TEST] ")
#
# write: gọi `claude -p` (headless) làm theo prompts/write.md, bật hook rào (WT_FENCE=1). Có thể chọn model
#        bằng WT_MODEL=<model>. Hoặc mở Claude Code và yêu cầu: "Làm bước write cho <DATE> theo prompts/write.md".
# notify: mặc định DRY_RUN (chỉ in payload). --send gửi thật, NOTIFY_PREFIX mặc định "[TEST] " (NOTIFY_PREFIX= để bỏ).
# Bỏ kết quả test: git checkout -- content/ site/ && git clean -fd content/ site/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

STEPS="crawl write build notify"
usage() { sed -n '2,15p' "$0" >&2; exit 2; }
index_of() {  # <step> → vị trí trong STEPS, rỗng nếu không có
  local i=0 s
  for s in $STEPS; do
    [[ "$s" == "$1" ]] && { echo "$i"; return 0; }
    i=$((i + 1))
  done
  return 0
}

DATE="${1:-}"; RANGE="${2:-}"; SEND=0
[[ "${3:-}" == "--send" ]] && SEND=1
[[ "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ && -n "$RANGE" ]] || usage
FROM="$(index_of "${RANGE%%..*}")"; TO="$(index_of "${RANGE##*..}")"
[[ -n "$FROM" && -n "$TO" && $FROM -le $TO ]] || usage

run_crawl() {
  python3 scripts/trending.py crawl "$DATE"
}

run_write() {
  command -v claude >/dev/null || {
    echo "dev.sh: không thấy lệnh claude — mở Claude Code trong repo và yêu cầu:" >&2
    echo "  \"Làm bước write cho $DATE theo đúng prompts/write.md\"" >&2
    exit 2
  }
  [[ -f "content/$DATE/trending.json" ]] || { echo "dev.sh: chưa có content/$DATE/ — chạy bước crawl trước" >&2; exit 2; }
  # Prompt qua stdin; quyền tối thiểu: sub-agent ghi file (acceptEdits), WebFetch chỉ GitHub, Bash chỉ trending.py.
  printf '%s\n' \
    "DATE=$DATE. Bạn đang chạy bước write của Weekly Trending ở máy local, không có người trực: không hỏi lại." \
    "Đọc prompts/write.md và làm đúng theo đó cho DATE này (ghi đè card và highlights cũ nếu có)." \
    "Không commit, không push, không chạy scripts/publish.sh hay notify.sh." \
    "Kết thúc bằng báo cáo ngắn: số card đạt, repo nào phải viết lại, cảnh báo còn lại." \
  | WT_FENCE=1 claude -p ${WT_MODEL:+--model "$WT_MODEL"} \
      --permission-mode acceptEdits \
      --allowedTools Read Write Edit Glob Grep Agent \
        "WebFetch(domain:github.com)" "WebFetch(domain:raw.githubusercontent.com)" \
        "Bash(python3 scripts/trending.py tasks:*)" "Bash(python3 scripts/trending.py validate:*)"
  python3 scripts/trending.py validate "$DATE"
}

run_build() {
  echo "== validate"; python3 scripts/trending.py validate "$DATE"
  echo "== prune";    python3 scripts/trending.py prune "$DATE"
  echo "== build";    python3 scripts/trending.py build "$DATE"
  # Chỉ để biết trước publish.sh thật có bị chặn không (code chưa commit, commit bảo trì chưa push…).
  echo "== guard (chỉ cảnh báo)"
  bash scripts/guard.sh worktree "$DATE" || echo "⚠️  publish.sh thật sẽ bị guard worktree chặn (xem danh sách trên)"
  bash scripts/guard.sh outgoing || echo "⚠️  publish.sh thật sẽ bị guard outgoing chặn (hoặc chưa có remote origin)"
}

run_notify() {
  if [[ $SEND == 1 ]]; then
    NOTIFY_PREFIX="${NOTIFY_PREFIX-[TEST] }" bash scripts/notify.sh success "$DATE"
  else
    DRY_RUN=1 bash scripts/notify.sh success "$DATE"
  fi
}

i=0
for step in $STEPS; do
  if [[ $i -ge $FROM && $i -le $TO ]]; then
    echo "===== $step $DATE"
    "run_$step"
  fi
  i=$((i + 1))
done
echo "✅ dev.sh $DATE $RANGE xong — không commit/push. Xem thử: python3 -m http.server -d site 8000"
