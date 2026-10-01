#!/usr/bin/env bash
# Kịch bản cho scripts/guard.sh và publish.sh --no-push trên repo tạm có bare origin (không dùng mạng, không gửi tin).
#
#   bash tests/test_guard.sh
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
OLD=2026-05-03    # quá hạn so với NEW: RETENTION_WEEKS=20 → mốc 2026-05-11
KEPT=2026-09-20   # còn hạn
NEW=2026-09-27    # bản tin đang publish
PASS=0; FAIL=0

git init -q --bare "$TMP/origin.git"
git -C "$TMP/origin.git" symbolic-ref HEAD refs/heads/main
git clone -q "$TMP/origin.git" "$TMP/repo" 2>/dev/null
cd "$TMP/repo"
git symbolic-ref HEAD refs/heads/main
git config user.name test
git config user.email test@example.com
cp -R "$SRC/scripts" "$SRC/config" "$SRC/theme" "$SRC/tests" .
rm -rf scripts/__pycache__ tests/__pycache__
python3 tests/fakeissue.py . "$OLD" 2
python3 tests/fakeissue.py . "$KEPT" 2
python3 scripts/trending.py build "$KEPT" >/dev/null
git add -A
git commit -qm seed
git push -q origin main

reset() { git reset -q --hard origin/main; git clean -qfd; }
new_issue() {  # <số repo>: bản tin NEW + prune + build, như publish.sh làm trước guard
  python3 tests/fakeissue.py . "$NEW" "${1:-2}"
  python3 scripts/trending.py prune "$NEW" >/dev/null
  python3 scripts/trending.py build "$NEW" >/dev/null
}
expect() {  # <mô tả> <exit mong đợi> <chuỗi phải có trong output> <lệnh…>
  local name="$1" want="$2" needle="$3" out rc=0
  shift 3
  out="$("$@" 2>&1)" || rc=$?
  if [[ $rc -eq $want && "$out" == *"$needle"* ]]; then
    PASS=$((PASS + 1)); echo "✓ $name"
  else
    FAIL=$((FAIL + 1)); echo "✗ $name (exit $rc, cần $want; cần thấy '$needle')"
    printf '%s\n' "$out" | sed 's/^/    /'
  fi
}

echo "== guard worktree"
new_issue
expect "bản tin mới + xoá tuần quá hạn" 0 "file quá hạn" bash scripts/guard.sh worktree "$NEW"
git add -A && git commit -qm "weekly: $NEW"
expect "outgoing: commit đúng phạm vi" 0 "GUARD OK (outgoing)" bash scripts/guard.sh outgoing

reset; new_issue; echo x > scripts/intruder.sh
expect "file ngoài content/ và site/" 3 "ngoài phạm vi content/ và site/: scripts/intruder.sh" \
  bash scripts/guard.sh worktree "$NEW"

reset; new_issue; echo "🔥 sửa lén" >> "content/$KEPT/highlights.txt"
expect "sửa bản tin tuần khác" 3 "sửa ngoài content/$NEW/: content/$KEPT/highlights.txt" \
  bash scripts/guard.sh worktree "$NEW"

reset; new_issue; rm "content/$KEPT/highlights.txt"
expect "xoá file chưa quá hạn" 3 "xoá file: content/$KEPT/highlights.txt" bash scripts/guard.sh worktree "$NEW"

reset; new_issue; printf '#!/bin/sh\n' > "content/$NEW/run.sh"
expect "đuôi file lạ" 3 "đuôi file không hợp lệ trong content/" bash scripts/guard.sh worktree "$NEW"

reset; new_issue; chmod +x "content/$NEW/trending.json"
expect "file thực thi" 3 "file thực thi: content/$NEW/trending.json" bash scripts/guard.sh worktree "$NEW"

reset; new_issue; ln -s ../../scripts "content/$NEW/link.md"
expect "symlink" 3 "symlink: content/$NEW/link.md" bash scripts/guard.sh worktree "$NEW"

hook="https://chat.googleapis.com/v1/spaces/AAAA/messages?key=abcdefghijklmnopqrstuvwxyz0123&token=secret-token"
reset; new_issue; printf '🔥 %s\n' "$hook" >> "content/$NEW/highlights.txt"
expect "lộ URL webhook" 3 "nội dung chứa giá trị \$GCHAT_WEBHOOK_URL" \
  env GCHAT_WEBHOOK_URL="$hook" bash scripts/guard.sh worktree "$NEW"

reset; new_issue
expect "DATE ở tương lai thì cấm xoá" 3 "xoá file: content/$OLD/" bash scripts/guard.sh worktree 2099-01-01

mkdir "$TMP/nogit" && cp -R scripts config "$TMP/nogit/"
expect "không phải git repo thì fail, không in OK" 2 "không phải git repo" \
  bash "$TMP/nogit/scripts/guard.sh" worktree "$NEW"

echo "== guard outgoing"
reset; new_issue; git add -A && git commit -qm "update stuff"
expect "commit message sai" 3 "commit message sai format" bash scripts/guard.sh outgoing

reset; echo "ghi chú" > NOTES.md; git add -A && git commit -qm "weekly: $NEW"
expect "commit chạm file ngoài phạm vi" 3 "ngoài phạm vi content/ và site/: NOTES.md" bash scripts/guard.sh outgoing

reset; git checkout -q -b side; new_issue; git add -A && git commit -qm "weekly: $NEW"
git checkout -q main; git merge -q --no-ff -m "weekly: $NEW" side
expect "merge commit" 3 "có merge commit" bash scripts/guard.sh outgoing
git branch -q -D side

echo "== publish.sh --no-push"
reset; new_issue 10
expect "publish dry-run thành công" 0 "[DRY-RUN] Google Chat payload" bash scripts/publish.sh "$NEW" --no-push
expect "commit 'weekly: DATE' đã tạo" 0 "weekly: $NEW" git log -1 --format=%s
reset; new_issue 10; echo x > scripts/intruder.sh
expect "publish dừng ở guard và báo lỗi (dry-run)" 3 "Bước: guard" bash scripts/publish.sh "$NEW" --no-push

echo
echo "Kết quả: $PASS đạt, $FAIL hỏng"
[[ $FAIL -eq 0 ]]
