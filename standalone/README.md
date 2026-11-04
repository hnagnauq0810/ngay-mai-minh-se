# Ngày mai, mình sẽ… — Standalone cinematic v1.3

Chạy nhanh:

```bash
python -m http.server 8080
# mở http://localhost:8080
```

Chọn nút **▶ Xem như một bộ phim**. Player tự chuyển cảnh, có Tạm dừng → Tiếp tục, Dừng, Lặp và Toàn màn hình.

**Giọng Việt tự nhiên:** Đã kèm 55 MP3 giọng kể Thiện Minh (VieNeu). Không cần API key hay giọng Việt của máy. Nút Nghe câu chuyện và Tự kể cũng dùng MP3. Muốn tạo lại sau khi sửa kịch bản, chạy `.\.venv-voice\Scripts\python.exe scripts/generate_voice_vieneu.py` từ source gốc; xem README gốc để cài thư viện.

Nội dung lịch sử là bản thảo cần thẩm định trước công bố.


Đã kèm ảnh, đồ họa và 7 đoạn video cục bộ. Mỗi cảnh có 3–5 mốc đổi hình theo lời kể, tổng cộng 185 mốc. Nút tư liệu trước/tiếp cho phép xem thêm hình trong cùng một cảnh. Nguồn và giới hạn minh họa nằm trong chú thích; xem `docs/MULTIMEDIA_CREDITS.md` và `docs/storyboard_cues.csv` trong source gốc.
