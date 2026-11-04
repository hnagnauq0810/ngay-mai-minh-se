# NGÀY MAI, MÌNH SẼ… — source v1.3

Bản test online: https://hnagnauq0810.github.io/ngay-mai-minh-se/ · [Hướng dẫn GitHub Pages](docs/GITHUB_PAGES.md)

## Bản giọng kể và nhiều tư liệu — 04/11/2026

Giọng mặc định hiện là **Thiện Minh (VieNeu, phong cách kể chuyện)**, cùng một giọng cho 55 cảnh. Mỗi cảnh có 3–5 mốc đổi hình theo lời dẫn: 181 mốc, 138 tư liệu, gồm 10 video dùng tại 13 cảnh. Video không phát tiếng gốc; tạm dừng cùng lời kể. Nguồn, năm và nhãn ảnh bối cảnh được ghi rõ. Các diagram và bản đồ đã được thay bằng ảnh hoặc video. Có 14 tranh AI tạo riêng và 67 ảnh Internet bổ sung được sử dụng; 55 cảnh có hình mở khác nhau, hai cảnh liền nhau không lặp tư liệu. Xem [rà soát hình ảnh](docs/IMAGE_VARIETY_REVIEW.md).

Chạy ngay: `python -m http.server 8080 --directory out`, rồi mở `http://localhost:8080`. Không cần API key hay mô hình TTS khi xem.

Hướng dẫn tạo lại giọng và chỉnh hình: [docs/VOICE_MULTIMEDIA_UPGRADE.md](docs/VOICE_MULTIMEDIA_UPGRADE.md). Nguồn tư liệu: [docs/MULTIMEDIA_CREDITS.md](docs/MULTIMEDIA_CREDITS.md). Mốc hình theo từng cụm từ: [docs/storyboard_cues.csv](docs/storyboard_cues.csv).

Các mục v1.3 bên dưới ghi lại bộ giọng/ảnh trước đó và lựa chọn FPT tùy chọn. Bộ MP3 Hoài My được giữ để so sánh; web hiện ưu tiên bộ giọng kể mới trong `voice-story/`.

**Website cinematic kể chuyện lịch sử · 12 chương · 55 cảnh · 1930–2026**

> **Cảnh báo biên tập:** Nội dung đang là bản thảo và chưa được thẩm định lịch sử theo từng dữ kiện. Kịch bản có các đoạn hội thoại hư cấu được gắn nhãn. Trước khi phát hành, kiểm tra lịch sử, ảnh tư liệu và quyền sử dụng.

## Các tính năng phim (từ v1.2)

- **Xem phim liên tục:** Nhấn `▶ Xem như một bộ phim` trên trang đầu. Một lượt bấm kích hoạt phát 55 cảnh theo thứ tự; tự chuyển cảnh khi kết thúc âm thanh.
- **Tạm dừng / Tiếp tục:** Dừng và tiếp tục từ đúng thời điểm trong file MP3 (không phát lại từ đầu cảnh).
- **Dừng:** Kết thúc phát; `Phát` lại từ đầu cảnh hiện tại. `Thoát` trở về web.
- **Lặp: Bật/Tắt:** mặc định bật — sau cảnh 55 tự quay lại cảnh 1 và chạy tiếp cho đến khi người xem dừng.
- **Giọng tiếng Việt:** ưu tiên MP3 đã tạo bằng FPT.AI (`banmai`, `leminh`, ...). Nếu chưa có MP3, chỉ dùng giọng `vi-VN` sẵn trên thiết bị, **không** đọc bằng giọng nước ngoài. Thiết bị không có giọng vi-VN sẽ hiển thị hướng dẫn.
- **Phụ đề:** bật/tắt được. Với MP3 xuất sẵn, timing phụ đề phân bổ theo độ dài câu, chưa phải time alignment chính xác theo từ.
- **Toàn màn hình:** trong trình duyệt hỗ trợ Fullscreen API.
- **Xuất file MP4 (tùy chọn):** script tạo video liên tục từ poster từng cảnh và bộ MP3 giọng đọc.

## Bản sửa âm thanh và ảnh — 04/11/2026

- Đã tích hợp giọng nữ Việt **Hoài My Neural** qua Edge TTS. Bộ MP3 được tạo sẵn cho 55 cảnh trong cả `public/assets/voice/` và `standalone/assets/voice/`; người xem không cần API key hay giọng Việt cài trên máy.
- Nút **Nghe câu chuyện**, **Tự kể** và chế độ phim đều ưu tiên MP3; hỗ trợ dừng/phát lại, tạm dừng/tiếp tục. Chỉ dùng giọng Việt của thiết bị nếu không tải được MP3.
- Tạo lại sau khi sửa kịch bản: `python -m pip install -r scripts/requirements-audio.txt`, rồi `python scripts/generate_voice_edge.py`. Chỉ những cảnh có nội dung/giọng/tốc độ thay đổi mới được tạo lại. Có thể chọn giọng nam bằng `--voice vi-VN-NamMinhNeural`.
- Edge TTS dùng dịch vụ đọc trực tuyến của Microsoft qua thư viện cộng đồng, cần Internet lúc tạo MP3; không phải API thương mại có cam kết dịch vụ. File đã tạo được phát trực tiếp từ website.
- FPT.AI vẫn là lựa chọn tùy chọn bên dưới. Theo [bảng giá chính thức](https://docs.fpt.ai/docs/vi/speech/documentation/tts-pricing/), gói miễn phí có 100.000 ký tự/tháng và giới hạn yêu cầu; API key phải được tạo trong tài khoản của bạn.
- Đã tải 29 ảnh vào cả hai bản web, sửa 10 cách gán ảnh và thay ảnh bị ghi nhầm là ruộng lúa. Bảng rà soát đủ 55 cảnh ở [docs/media_story_review.csv](docs/media_story_review.csv); 14 cảnh vẫn cần tư liệu sát chủ đề hơn, có ghi rõ giới hạn ở chú thích.

Kiểm tra: `python tests/audio_playback.py` (phát MP3 thật + giải mã đủ 55 file), `python tests/cinema_smoke.py`, `python tests/e2e_smoke.py`, `python scripts/validate_media.py`.

## 1. Chạy ngay bản độc lập

```bash
cd standalone
python -m http.server 8080
```

Mở `http://localhost:8080`, nhấn **Xem như một bộ phim**.

Không cần Node.js, npm hay backend. Bộ MP3 tiếng Việt đã có sẵn. Nếu một file không tải được, trình phát thử giọng Việt của hệ điều hành và hiện thông báo rõ khi không có giọng phù hợp.

## 2. Chạy Next.js

```bash
npm install
npm run generate
npm run validate
npm run dev
```

Mở `http://localhost:3000`.

Build xuất static:

```bash
npm run build
# upload thư mục out/ lên Netlify, Cloudflare Pages hoặc static hosting khác
```

**Lưu ý kiểm thử:** bản độc lập đã qua smoke test desktop/mobile với audio mô phỏng. Bản sửa 04/11/2026 đã chạy Next build và kiểm thử phát MP3 thật trên Chromium ở desktop/mobile.

## 3. Tùy chọn: tạo MP3 bằng FPT.AI khi có key riêng

FPT.AI Speech TTS v5 cung cấp nhiều giọng nói: `banmai` (nữ Bắc), `leminh` (nam Bắc), `lannhi` (nữ Nam), `thuminh` (nữ Bắc), `myan` (nữ Trung), `giahuy` (nam Trung), `linhsan` (nữ Nam).

Tài liệu API chính thức: https://docs.fpt.ai/docs/vi/speech/api/text-to-speech/

**Bước A — xem trước chi phí/số request (không cần key):**

```bash
python scripts/generate_voice_fpt.py --dry-run
python scripts/generate_voice_fpt.py --dry-run --dramatized
```

Mặc định: 55 request (một giọng đọc cho từng cảnh). `--dramatized`: 164 request (đổi giọng khi mẹ/con đối thoại). Số request có thể thay đổi nếu biên tập thêm nội dung.

**Bước B — thiết lập key cục bộ:**

macOS/Linux:

```bash
export FPT_AI_KEY="YOUR_FPT_KEY"
```

Windows PowerShell:

```powershell
$env:FPT_AI_KEY="YOUR_FPT_KEY"
```

**Bước C — tạo MP3:**

```bash
# Giọng nữ miền Bắc, kiểu dẫn chuyện nhẹ nhàng
python scripts/generate_voice_fpt.py --voice banmai --speed -1

# Thử 3 cảnh trước khi trả phí sinh đủ 55 cảnh
python scripts/generate_voice_fpt.py --voice banmai --speed -1 --limit 3

# Có hai giọng mẹ/con riêng, cần ffmpeg
python scripts/generate_voice_fpt.py --voice banmai --speed -1 --dramatized
```

File sinh ra ở cả hai nơi:

- `public/assets/voice/PRO_S01.mp3`, `...C01_S01.mp3`, ... cho Next.js.
- `standalone/assets/voice/PRO_S01.mp3`, ... cho bản độc lập.

Script có cache, retry mã 429 và đợi link MP3 bất đồng bộ. Chạy lại sẽ bỏ qua những file đã tạo (trừ khi có `--overwrite`). **Việc dùng FPT.AI có thể phát sinh phí.** Không được công khai hoặc chia sẻ API key.

**Giọng người thật:** Bạn cũng có thể mời người Việt thu âm thực sự và đặt các MP3 theo đúng tên `SCENE_ID.mp3`; player sẽ phát ngay không cần API.

## 4. Xuất thành một MP4 duy nhất (tùy chọn)

Sau khi tạo đủ MP3:

```bash
pip install Pillow
# Cài ffmpeg (có cả ffprobe) và thêm vào PATH
python scripts/export_video.py --size 1920x1080 --output video/ngay-mai-minh-se.mp4
```

Để thử trước 1 cảnh:

```bash
python scripts/export_video.py --limit 1 --size 640x360 --output video/demo.mp4
```

MP4 là video **title-card + phụ đề tóm tắt + voice**, không phải phim có cảnh quay lịch sử; thay hình minh họa bằng media đã xác minh và có quyền dùng trước khi phát hành. MP4 có thể đưa lên web bằng thẻ `<video controls>` để phát/tạm dừng/tiếp tục theo kiểu video truyền thống.

## 5. Các phím điều khiển trong chế độ phim

| Phím hoặc nút | Hành động |
|---|---|
| `▶ Xem như một bộ phim` | Bắt đầu từ cảnh 1 |
| `❚❚ Tạm dừng` | Tạm dừng audio và giữ nguyên vị trí |
| `▶ Tiếp tục` | Phát từ đúng vị trí tạm dừng |
| `■ Dừng` | Kết thúc lượt phát; phát lại từ đầu cảnh hiện tại |
| `Lặp: Bật/Tắt` | Cho phép lặp tự động hết hành trình |
| `❮` / `❯` | Lùi/tiến một cảnh |
| `Space` | Tạm dừng/tiếp tục (khi không focus vào nút) |
| `Esc` | Thoát chế độ phim |
| `⛶ Toàn màn hình` | Mở Fullscreen API |

## 6. Kiểm thử và phát hành

```bash
python scripts/validate_content.py
python tests/cinema_smoke.py
node --check public/assets/cinema.js
python scripts/generate_voice_fpt.py --dry-run --limit 1
```

Smoke tests dùng audio mô phỏng để không phụ thuộc TTS API; kiểm tra render, auto-next, pause/resume preserving time, loop 55→1, stop và close ở kích thước 1440×900 và 390×844.

Không phát hành công khai trước khi hoàn thành xác minh lịch sử và quyền sử dụng tư liệu. Quy trình release gate: `python scripts/validate_content.py --release`.

## Cấu trúc chính

```text
app/                         Next.js App Router
public/assets/site.{css,js}  Website gốc
public/assets/cinema.{css,js} Phim liên tục, phụ đề, TTS/audio player
public/assets/voice/         MP3 của từng cảnh (tạo sau khi có FPT key)
standalone/                  Bản chạy độc lập, assets tương ứng
content/story_manifest.v1.json 55 cảnh: giọng dẫn, thoại và metadata
scripts/generate_voice_fpt.py  Tạo MP3 hàng loạt và lưu vào cả hai bản web
scripts/export_video.py       Xuất MP4 từ MP3
scripts/build_site.py        Sinh lại trang sau khi sửa JSON nội dung
tests/cinema_smoke.py         Kiểm tra chức năng player
```



## v1.3 — Ảnh theo từng cảnh, thay hình mặc định

- Đã gắn **29 tư liệu Wikimedia Commons** vào **55/55 cảnh**, có chú thích niên đại, nguồn và giấy phép.
- Mở đầu + tiêu đề 12 chương dùng ảnh theo giai đoạn; đọc cuộn trang có ảnh ở từng cảnh.
- Cinema Player tự thay hình theo cảnh, giữ nguyên tính năng Phát liên tục / Tạm dừng / Tiếp tục / Dừng.
- Một clip tư liệu Genève 1954 có **liên kết xem tùy chọn** ở cảnh C07_S01.
- Ảnh ghi `archive` là ảnh lưu trữ; `contemporary` là ảnh chụp đời sống hiện tại dùng để minh họa, được dán nhãn minh bạch.

**29 ảnh hiện đã được lưu cục bộ** trong cả hai bản web; trang dùng file local khi có sẵn. URL Wikimedia Commons vẫn được giữ làm nguồn và phương án dự phòng. Để triển khai ổn định và tránh hotlink, trên máy dev có Internet chạy:

```bash
python scripts/download_commons_media.py --all
python scripts/build_site.py
python scripts/validate_media.py
```

Nếu dùng Next.js, chạy tiếp `npm run dev` hoặc `npm run build`. Bản standalone có thể mở `standalone/index.html` sau bước generate. Tài liệu giấy phép và nguồn ảnh chi tiết: `docs/MEDIA_CREDITS.md`.

**Release gate:** Kiểm tra bản quyền tư liệu thực tế, nguồn sự kiện, tính chính xác captions, sự phân biệt ảnh đương đại và tư liệu lịch sử trước khi công khai.
