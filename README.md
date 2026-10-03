# Weekly Trending

Bản tin tiếng Việt hằng tuần về **top 10 repo trên [GitHub Trending](https://github.com/trending?since=weekly)**. Mỗi repo có tóm tắt "để làm gì, ai nên dùng, use case" và số liệu lấy nguyên từ GitHub.

- 🌐 Trang: https://sontvwork.github.io/weekly-trending/
- 📡 Feed: https://sontvwork.github.io/weekly-trending/feed.xml

```
GitHub Actions Crawl (17:00 tối Chủ nhật giờ VN = cron 0 10 * * 0 UTC)
  → scripts/trending.py crawl: trang trending (HTML) + README (raw.githubusercontent.com) → content/DATE/
  → đẩy content/DATE/ lên branch dữ liệu `trending-data` (bot, không đụng main)
Claude Code Routine (19:00 tối Chủ nhật giờ VN = cron 0 12 * * 0 UTC, cloud, mạng Trusted)
  → scripts/trending.py import: lấy content/DATE/ từ branch `trending-data` (proxy cloud chặn trang trending)
  → prompts/write.md: 10 sub-agent `repo-writer` viết card song song → highlights.txt → validate
  → scripts/publish.sh: xoá tuần quá 20 tuần → build site/ → guard → commit "weekly: DATE" → push main
      → GitHub Actions deploy site/ lên Pages → kiểm tra Pages khớp bản build → Google Chat
  (lỗi ở bất kỳ bước nào → Google Chat báo bước bị fail)
GitHub Actions watchdog 21:00 tối Chủ nhật giờ VN: chưa có bản tin tuần này → Google Chat
```

## Cấu trúc

| Đường dẫn | Vai trò |
|---|---|
| `config/weekly.env` | Cấu hình không bí mật: URL Pages, `TOP_N`, `RETENTION_WEEKS`, `README_MAX_CHARS`, `DATA_BRANCH` |
| `scripts/trending.py` | `crawl`, `import`, `tasks`, `validate`, `prune`, `build`, `link`, `message`, `verify-live` |
| `scripts/render.py` + `theme/` | Renderer và template: trang danh sách, trang tuần, `feed.xml`, `404.html`, light/dark |
| `scripts/publish.sh` | Cách duy nhất để commit/push; lỗi ở bước nào cũng gửi Google Chat |
| `scripts/guard.sh` | Hàng rào: chỉ cho thay đổi `content/DATE/` + `site/`, không xoá (trừ tuần quá hạn), không lộ secret |
| `scripts/notify.sh` | Google Chat webhook (`curl`), có `DRY_RUN=1` |
| `scripts/dev.sh` | Chạy lại từng bước ở local (`crawl`, `write`, `build`, `notify`): không commit, không push |
| `scripts/fence.py` + `.claude/settings.json` | Hook rào trên cloud: chỉ ghi `content/`, `.cache/`; WebFetch chỉ GitHub |
| `.claude/agents/repo-writer.md` | Sub-agent viết card cho 1 repo. **Văn phong của card nằm ở đây** |
| `prompts/write.md` | Quy trình bước viết (chia việc cho sub-agent, highlights, validate) |
| `content/YYYY-MM-DD/` | Dữ liệu tuần: `trending.json`, `sources/` (README đã crawl), `cards/`, `highlights.txt` |
| `site/` | Output build, deploy lên Pages. **Không sửa tay** |
| `ROUTINE_PROMPT.md` | Prompt để dán vào routine |
| `.github/workflows/crawl.yml` | Crawl trên GitHub Actions → branch `trending-data`; lỗi thì báo Google Chat |
| `tests/` | `python3 -m unittest discover -s tests`, `bash tests/test_guard.sh` |

## Setup từ đầu

### 1. Google Chat incoming webhook
1. Mở Space nhận tin → bấm tên Space → **Apps & integrations** → **Webhooks** → **Add webhook**.
2. Đặt tên rồi **Save**, copy URL (dạng `https://chat.googleapis.com/v1/spaces/.../messages?key=...&token=...`).
3. URL này là **secret**. Chỉ lưu ở 3 nơi: env của cloud environment, GitHub secret và `.env.local` (local, đã gitignore). Tuyệt đối không commit.

### 2. GitHub repo + Pages
1. Tạo repo **public** `sontvwork/weekly-trending` (để trống, không tạo README), rồi push code: `git push -u origin main`.
2. Vào **Settings → Pages → Build and deployment → Source: GitHub Actions**. Sau đó vào **Actions → Deploy Pages → Run workflow** để deploy lần đầu. Lần push đầu tiên chạy trước khi Pages được bật nên sẽ fail; điều này bình thường.
3. **Không** bật branch protection hay ruleset cho `main`. Nếu bật, routine sẽ bị từ chối push.
4. Mọi commit trên `main` phải do chính bạn (`sontvwork`) author. Repo local đã đặt `user.email` là email noreply của `sontvwork`. Không merge PR của người khác vào `main`.
5. Vào **Settings → Secrets and variables → Actions → New repository secret**, thêm `GCHAT_WEBHOOK_URL` = URL webhook. Workflow watchdog và crawl dùng secret này.

### 3. Quyền GitHub cho routine
Cài [Claude GitHub App](https://github.com/apps/claude) cho repo, hoặc chạy `/web-setup` trong Claude Code CLI.

### 4. Cloud environment + routine
Làm tại [claude.ai/code/routines](https://claude.ai/code/routines) → **New routine**, hoặc chạy `/schedule` trong một session Claude Code local.

| Mục | Giá trị |
|---|---|
| Tên | `Weekly Trending` |
| Prompt | Dán **nguyên văn** nội dung [`ROUTINE_PROMPT.md`](ROUTINE_PROMPT.md); chọn model ở ô prompt |
| Repository | `sontvwork/weekly-trending` |
| Environment | Tạo mới tên `weekly-trending` (xem bên dưới) |
| Trigger | **Weekly**, Chủ nhật, 19:00 giờ VN. Muốn đặt cron chính xác thì dùng `/schedule update` và nhập `0 12 * * 0` (UTC). Kiểm tra *next run* hiển thị 19:00 giờ VN |
| Connectors | **Bỏ hết**: routine không cần connector nào |

Cloud environment `weekly-trending`:
- **Network access: Trusted** (mặc định). Danh sách này đã có `github.com`, `raw.githubusercontent.com` và `*.googleapis.com` (Google Chat), nên không cần Full.
- **Environment variables**:
  ```
  GCHAT_WEBHOOK_URL=<url webhook>
  WT_FENCE=1
  ```
  `WT_FENCE=1` bật hook rào (`scripts/fence.py`): chỉ cho ghi `content/` và `.cache/`, WebFetch chỉ tới GitHub. ⚠️ Ai dùng chung environment này đều đọc được các biến trên, nên hãy giữ environment ở chế độ riêng tư.
- **Setup script**: để trống. Script chỉ dùng Python stdlib (chạy được với Python ≥ 3.9), `git` và `curl`; image cloud đã có sẵn cả ba.
- Không cần GitHub token. Repo không gọi GitHub REST API (proxy GitHub của cloud chỉ cho API vào repo gắn với session); mọi dữ liệu lấy từ trang trending và raw README.

Lịch đặt đúng giờ chẵn có thể chạy trễ vài phút. Ngày của bản tin luôn tính theo `Asia/Ho_Chi_Minh` nên không bị ảnh hưởng.

### 5. Chạy thử
1. Vào **Actions → Crawl → Run workflow**. Workflow sẽ tạo (hoặc cập nhật) branch `trending-data` chứa `content/<hôm nay>/`. Workflow cần quyền ghi (`permissions: contents: write` đã khai báo trong file); nếu push bị từ chối, vào **Settings → Actions → General → Workflow permissions** chọn **Read and write permissions**.
2. Trên trang routine, bấm **Run now** và nhập text `dry-run`. Routine sẽ chạy đủ import → viết → build → guard nhưng **không push**, và tin Google Chat chỉ được in ra. Mở session của run để đọc transcript. `import` chỉ nhận dữ liệu của **hôm nay** (giờ VN), nên bước 1 phải chạy cùng ngày.
3. Bấm **Run now** không kèm text để publish thật. Bản tin sẽ mang ngày chạy, nhãn tuần là 7 ngày tính tới ngày đó, và tồn tại 20 tuần. Muốn bản tin đầu tiên rơi vào Chủ nhật thì cứ chờ lịch.
4. Vào **Actions → Watchdog → Run workflow** để thử đường báo lỗi: nếu tuần đó chưa có bản tin, Google Chat sẽ nhận tin `watchdog`.

Lưu ý: chấm xanh trong danh sách run chỉ có nghĩa là session không gặp lỗi hạ tầng. Kết quả thật nằm trong transcript và tin Google Chat.

## Chạy ở local (macOS/Linux, Python ≥ 3.9)
```bash
printf 'GCHAT_WEBHOOK_URL=%s\n' '<url>' > .env.local && chmod 600 .env.local   # bỏ bước này thì notify luôn dry-run
DATE=$(TZ=Asia/Ho_Chi_Minh date +%F)
bash scripts/dev.sh "$DATE" crawl..notify   # crawl → viết (claude -p, 10 sub-agent) → build → notify dry-run
bash scripts/dev.sh "$DATE" write..notify   # đổi văn phong: viết lại từ dữ liệu đã crawl, không crawl lại
bash scripts/dev.sh "$DATE" build           # validate → prune → build → guard (chỉ cảnh báo)
bash scripts/dev.sh "$DATE" notify --send   # chỉ gửi lại tin Google Chat thật (tiền tố "[TEST] ")
python3 -m http.server -d site 8000         # xem thử: http://localhost:8000/
git checkout -- content/ site/ && git clean -fd content/ site/   # bỏ kết quả test
```
`dev.sh` không commit và không push. Muốn publish thật một tuần đã chạy lại thì dùng `bash scripts/publish.sh DATE`, sau khi code bảo trì đã được commit và push.

## Vận hành
- **Đổi văn phong card:** sửa `.claude/agents/repo-writer.md`. Đổi quy trình viết hoặc luật viết highlights thì sửa `prompts/write.md`. Hai file này nằm trong repo nên routine tự dùng bản mới, không cần dán lại prompt. Luật kiểm tra tương ứng nằm trong `scripts/trending.py` (`check_card`, `check_highlights`).
- **Đổi giao diện:** sửa `theme/` (template `$tên`, `assets/style.css`). HTML của từng card nằm trong `scripts/render.py`. Xem thử bằng `python3 scripts/trending.py build <DATE mới nhất>`, rồi commit cả `theme/` lẫn `site/` đã render.
- **Đổi số tuần lưu trữ / số repo:** sửa `RETENTION_WEEKS` / `TOP_N` trong `config/weekly.env`.
- **Lưu trữ:** mỗi lần publish, `trending.py prune` xoá `content/<D>/` và `site/<D>/` có `D < DATE − (RETENTION_WEEKS×7 − 1)` và gộp vào commit `weekly: DATE`. File chỉ bị xoá khỏi `main` và site, history git vẫn giữ. Link cũ mở ra `404.html` với thông báo "đã quá hạn lưu trữ".
- **Chạy lại trong ngày:** `content/DATE/` bị thay toàn bộ. Link trang tuần (`/<DATE>/`) giữ nguyên.
- **Guard chặn:** file ngoài `content/` và `site/`; sửa tuần khác; xoá file (trừ tuần quá hạn); đuôi file lạ; symlink; file thực thi; file > 1 MB; merge commit; commit message khác `weekly: YYYY-MM-DD`; secret trong nội dung.

## Rủi ro đã biết
- **Trang trending không có API chính thức.** Nếu GitHub đổi HTML, crawl sẽ fail và báo Google Chat. Sửa regex ở đầu `scripts/trending.py` và fixture `tests/fixtures/trending-weekly.html`.
- **Proxy cloud chặn trang trending** (`HTTP 403` ở lần dry-run đầu). Vì vậy crawl chạy trên GitHub Actions lúc 17:00; routine `import` từ branch `trending-data`, và chỉ thử crawl trực tiếp khi import lỗi. Workflow Crawl lỗi → Google Chat báo bước `crawl-actions`; sửa xong bấm **Run workflow** lại trước 19:00 là kịp. Sau 19:00 thì chạy workflow rồi **Run now** routine.
- **Không được để bot commit vào `main`.** Routine chỉ push được khi mọi commit trên `main` do `sontvwork` author, nên workflow Crawl chỉ ghi vào `trending-data`. Commit của routine chứa bản sao dữ liệu, do `sontvwork` author.
- **WebFetch có thể sai.** Sub-agent được WebFetch thêm docs trên GitHub khi README sơ sài; nội dung trang được một model nhỏ tóm tắt nên có thể sai. Số liệu thống kê luôn do script chèn. Số trong phần chữ thì bị kiểm tra: không có trong dữ liệu đã crawl là lỗi (hoặc cảnh báo nếu card có `refs`).
- **README bên thứ ba nằm trong repo public.** `content/*/sources/` lưu đoạn trích README (≤ 30.000 ký tự/repo) để chạy lại bước viết; phần này không deploy lên Pages.
- **Routines đang ở research preview.** UI, giới hạn và quy tắc push có thể thay đổi. Routine tính vào hạn mức sử dụng của tài khoản.
- **Cron của GitHub Actions (crawl, watchdog) có thể trễ** vài phút đến vài chục phút; crawl chừa 2 tiếng trước routine.
