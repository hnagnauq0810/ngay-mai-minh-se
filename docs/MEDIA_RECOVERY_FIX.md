# Sửa lỗi ảnh cũ không tải được — 04/11/2026

Ảnh chụp lỗi hiển thị mục `ordinary_day.svg` (mốc 3/4 của cảnh mở đầu), chú thích “Những dự định rất đỗi bình thường” và nhãn đồ họa. File diagram này đã bị xóa trong bản thay ảnh. Khi trang HTML hoặc lịch sử trình duyệt còn giữ danh sách tư liệu cũ, mục đó trả về HTTP 404. Bản online hiện tại và bản export mới không còn gọi đường dẫn này.

Bản sửa:

- Gắn phiên bản theo nội dung vào URL của các script và stylesheet standalone, để bản HTML mới lấy đúng mã trình xem.
- Xuất `assets/storyboard-manifest.json` từ cùng dữ liệu tạo trang. Khi gặp dữ liệu diagram cũ, ảnh lỗi hoặc trang được khôi phục từ lịch sử trình duyệt, trình xem lấy danh sách hiện tại với yêu cầu không dùng cache. Giữ chỉ số hình đang xem; cập nhật cả ảnh, chú thích, nguồn và chế độ phim.
- Ảnh không tải được tự chuyển sang tư liệu khác trong cùng cảnh. Các yêu cầu lỗi có giới hạn; nếu toàn bộ tư liệu không tải được, nút “Thử tải lại” hoạt động sau khi có mạng.
- Bỏ trình xử lý lỗi cũ vốn giấu ảnh và hiện thông báo Commons dù file là ảnh local. Không khôi phục diagram đã bỏ.

`tests/media_recovery.py` tái hiện bốn tình huống trong Chromium: HTML cũ còn diagram; HTTP 404 thật của `ordinary_day.svg` sau khi trình xem đã chạy; ảnh mới bị chặn; toàn bộ ảnh tạm mất và sau đó thử lại thành công. Các trường hợp đều kiểm tra hình hiển thị và chú thích thực tế, gồm đường dẫn dự án GitHub Pages.

Đã chạy đạt: `tests/media_recovery.py`, `tests/visual_variety.py --directory standalone` (138 tư liệu; 1440px và 390px), `tests/story_media_playback.py` (10 MP4; giọng nam; tạm dừng/tiếp tục), `tests/cinema_smoke.py`, `tests/e2e_smoke.py`, `scripts/validate_content.py`, `scripts/validate_storyboards.py`, `npm run build`.
