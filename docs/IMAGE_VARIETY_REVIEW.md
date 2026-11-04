# Rà soát độ đa dạng hình minh họa — 04/11/2026

Giữ nguyên 55 bản thu giọng nam Thiện Minh. Bản trước có 185 mốc, 80 tư liệu; bản hiện tại có 181 mốc minh họa trong 55 cảnh, 140 tư liệu khác nhau, 9 đoạn phim tại 12 cảnh.

- 55 hình mở cảnh khác nhau; không lặp tư liệu trong cùng cảnh hoặc giữa hai cảnh liền nhau.
- Một tư liệu được dùng tối đa hai lần trong toàn bộ câu chuyện. Kiểm tra SHA-256 không có file giống nhau dưới tên khác; đã xem bảng ảnh và so sánh dấu vân tay hình để phát hiện ảnh gần trùng.
- Thêm 44 ảnh Internet thực sự được dùng và 14 tranh tạo riêng bằng imagegen tích hợp. Giữ ảnh gốc, không cắt xén để giả thành ảnh mới.
- Loại khỏi phương án sử dụng ảnh xưởng có số điện thoại quảng cáo và trái phiếu cải cách điền địa không đúng chính sách được kể. Mốc thời gian của ảnh chụp về sau được ghi rõ.
- Hai trích đoạn phim bổ sung dùng những khoảng thời gian khác nhau từ phim gốc, không đổi tên cùng một đoạn phim.
- Ảnh hiện đại chỉ minh họa chủ đề, không được gán là bằng chứng của sự kiện trước đó. Tranh AI có nhãn và ghi chú tái dựng ở cả chế độ đọc và phim.

Xem [bảng ảnh AI](../tests/generated_illustrations_contact.jpg), [bảng ảnh Internet](../tests/unique_photos_contact.jpg), [so sánh trích đoạn phim](../tests/video_variety_contact.jpg), [nguồn và giấy phép](MULTIMEDIA_CREDITS.md), [mốc chuyển hình theo lời dẫn](storyboard_cues.csv), [prompt và bản gốc](../artwork/IMAGE_PROMPTS.md).

Kiểm tra nội dung/niên đại ở đây là rà soát biên tập; các bước thẩm định lịch sử trước phát hành trong acceptance matrix vẫn giữ trạng thái riêng.

Kiểm tra đã chạy và đạt: `validate_storyboards.py`, `validate_content.py`, `visual_variety.py` trên bản export `out/` (140 tư liệu tải/giải mã được; nhãn AI; giọng Thiện Minh; 1440px và 390px), `story_media_playback.py` (9 video), `audio_playback.py` (55 MP3), `cinema_smoke.py`, `e2e_smoke.py`, `npm run build`.
