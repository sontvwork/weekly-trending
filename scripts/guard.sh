#!/usr/bin/env bash
# Hàng rào an toàn trước commit/push của routine.
#
#   guard.sh worktree DATE   # trước commit: mọi thay đổi (kể cả untracked) đúng phạm vi bản tin DATE
#   guard.sh outgoing        # trước push: từng commit origin/main..HEAD đúng phạm vi, message "weekly: YYYY-MM-DD"
#
# Cho phép với bản tin DATE: thêm/sửa/xoá trong content/DATE/ (crawl thay cả thư mục khi chạy lại), thêm/sửa
# trong site/ (build render lại mọi trang), xoá content/<D>/ và site/<D>/ khi D < DATE − (RETENTION_WEEKS×7 − 1).
# Chặn: file ngoài content/ và site/, sửa tuần khác trong content/, đổi tên/copy, đuôi file lạ, symlink, file thực thi,
# file > 1 MB, merge commit, commit message sai, secret lọt vào nội dung. Vi phạm → in danh sách, exit 3.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=../config/weekly.env
source config/weekly.env
if [[ -f .env.local ]]; then set -a; source .env.local; set +a; fi

SECRET_VARS=(GCHAT_WEBHOOK_URL GH_TOKEN GITHUB_TOKEN ANTHROPIC_API_KEY)
DATE_RE='^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
DATED_RE='^(content|site)/([0-9]{4}-[0-9]{2}-[0-9]{2})/'
MAX_BYTES=1048576
violations=()
pruned=0
# Output của git ghi ra file tạm (không dùng process substitution) để `set -e` bắt được lỗi của git:
# guard phải fail-closed, không được in "OK" khi không đọc được trạng thái repo.
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "guard.sh: $ROOT không phải git repo" >&2; exit 2; }

# Mốc xoá cho bản tin DATE: thư mục có ngày < mốc mới được xoá. In rỗng (= cấm xoá) nếu RETENTION_WEEKS sai,
# DATE sai format / ở tương lai, hoặc không có content/DATE/trending.json (trên đĩa, hoặc trong <commit> nếu có).
cutoff_for() {  # <DATE> [commit]
  local day="$1" commit="${2:-}" weeks="${RETENTION_WEEKS:-}"
  [[ "$weeks" =~ ^[1-9][0-9]*$ && "$day" =~ $DATE_RE ]] || return 0
  [[ "$day" > "$(TZ="$NEWS_TZ" date +%F)" ]] && return 0
  if [[ -n "$commit" ]]; then
    git cat-file -e "$commit:content/$day/trending.json" 2>/dev/null || return 0
  else
    [[ -f "content/$day/trending.json" ]] || return 0
  fi
  python3 -c 'import sys, datetime as d
print(d.date.fromisoformat(sys.argv[1]) - d.timedelta(days=int(sys.argv[2]) * 7 - 1))' "$day" "$weeks" 2>/dev/null || true
}

check_path() {  # <status> <path> <DATE của bản tin, rỗng nếu không rõ> <mốc xoá, rỗng = cấm xoá>
  local status="$1" path="$2" day="$3" cutoff="$4" dated=""
  case "$path" in
    content/*|site/*) ;;
    *) violations+=("ngoài phạm vi content/ và site/: $path"); return 0 ;;
  esac
  [[ "$path" =~ $DATED_RE ]] && dated="${BASH_REMATCH[2]}"
  if [[ "$status" == *D* ]]; then
    if [[ -n "$dated" && -n "$cutoff" && "$dated" < "$cutoff" ]]; then pruned=$((pruned + 1)); return 0; fi
    [[ "$path" == content/* && -n "$day" && "$dated" == "$day" ]] && return 0
    violations+=("xoá file: $path")
    return 0
  fi
  if [[ "$path" == content/* ]]; then
    if [[ -z "$day" || "$dated" != "$day" ]]; then
      violations+=("sửa ngoài content/${day:-<DATE>}/: $path")
    elif [[ ! "$path" =~ \.(json|md|txt)$ ]]; then
      violations+=("đuôi file không hợp lệ trong content/: $path")
    fi
  elif [[ ! "$path" =~ \.(html|xml|css|js|svg)$ ]]; then
    violations+=("đuôi file không hợp lệ trong site/: $path")
  fi
  return 0
}

scan_secrets() {  # đọc nội dung từ stdin (gọi bằng redirect, không qua pipe, để giữ $violations)
  local content var value
  content="$(cat)"
  grep -Eq 'chat\.googleapis\.com/v1/spaces/[^[:space:]]*key=[A-Za-z0-9_-]{20,}' <<<"$content" \
    && violations+=("nội dung chứa URL webhook Google Chat")
  for var in "${SECRET_VARS[@]}"; do
    value="${!var:-}"
    [[ ${#value} -ge 8 && "$value" != proxy-injected ]] || continue
    grep -Fq -- "$value" <<<"$content" && violations+=("nội dung chứa giá trị \$$var")
  done
  return 0
}

mode="${1:-}"
count=0
cutoffs=""
case "$mode" in
  worktree)
    day="${2:-}"
    [[ "$day" =~ $DATE_RE ]] || { echo "guard.sh worktree: cần DATE dạng YYYY-MM-DD" >&2; exit 2; }
    cutoff="$(cutoff_for "$day")"; cutoffs="$cutoff"
    changed=()
    git status --porcelain=v1 -z --untracked-files=all --no-renames > "$SCRATCH/status"
    while IFS= read -r -d '' entry; do
      xy="${entry:0:2}"; path="${entry:3}"
      if [[ "$xy" == R* || "$xy" == C* ]]; then
        IFS= read -r -d '' orig || true
        violations+=("đổi tên/copy: $orig -> $path")
        continue
      fi
      check_path "$xy" "$path" "$day" "$cutoff"
      count=$((count + 1))
      if [[ -L "$path" ]]; then
        violations+=("symlink: $path")
      elif [[ -f "$path" ]]; then
        changed+=("$path")
        [[ -x "$path" ]] && violations+=("file thực thi: $path")
        [[ $(wc -c < "$path") -le $MAX_BYTES ]] || violations+=("file > 1 MB: $path")
      fi
    done < "$SCRATCH/status"
    if [[ ${#changed[@]} -gt 0 ]]; then
      cat -- "${changed[@]}" > "$SCRATCH/content"
      scan_secrets < "$SCRATCH/content"
    fi
    ;;
  outgoing)
    # Refspec tường minh: luôn cập nhật origin/main (ref cũ sẽ kéo cả commit đã push vào range).
    git fetch --quiet origin '+refs/heads/main:refs/remotes/origin/main'
    range="origin/main..HEAD"
    merges="$(git rev-list --merges "$range")"
    commits="$(git rev-list "$range")"
    [[ -z "$merges" ]] || violations+=("có merge commit trong $range")
    # Từng commit một (không dùng diff gộp): commit sau xoá file mà commit trước thêm vẫn bị bắt.
    while IFS= read -r commit; do
      [[ -n "$commit" ]] || continue
      subject="$(git log -1 --format=%s "$commit")"
      day=""; cutoff=""
      if [[ "$subject" =~ ^weekly:\ ([0-9]{4}-[0-9]{2}-[0-9]{2})$ ]]; then
        day="${BASH_REMATCH[1]}"
        cutoff="$(cutoff_for "$day" "$commit")"
        [[ -n "$cutoff" ]] && cutoffs="$cutoff"
      else
        violations+=("commit message sai format (cần 'weekly: YYYY-MM-DD'): '$subject'")
      fi
      # --raw -z: ":<mode cũ> <mode mới> <sha cũ> <sha mới> <status>" NUL "<path>" NUL
      git diff-tree -r -z --no-commit-id --no-renames --raw "$commit" > "$SCRATCH/tree"
      while IFS= read -r -d '' meta && IFS= read -r -d '' path; do
        read -r _ newmode _ newsha status <<<"$meta"
        check_path "$status" "$path" "$day" "$cutoff"
        count=$((count + 1))
        [[ "$status" == D* ]] && continue
        case "$newmode" in
          120000) violations+=("symlink: $path") ;;
          100755) violations+=("file thực thi: $path") ;;
        esac
        [[ $(git cat-file -s "$newsha") -le $MAX_BYTES ]] || violations+=("file > 1 MB: $path")
      done < "$SCRATCH/tree"
    done <<< "$commits"
    git diff origin/main HEAD > "$SCRATCH/diff"
    scan_secrets < "$SCRATCH/diff"
    ;;
  *)
    sed -n '2,10p' "$0" >&2; exit 2
    ;;
esac

if [[ ${#violations[@]} -gt 0 ]]; then
  echo "GUARD CHẶN ($mode): ${#violations[@]} vi phạm"
  printf ' - %s\n' "${violations[@]}"
  exit 3
fi
note=""
[[ $pruned -gt 0 ]] && note=" · xoá $pruned file quá hạn (ngày < $cutoffs)"
echo "GUARD OK ($mode): $count thay đổi, tất cả đúng phạm vi$note"
