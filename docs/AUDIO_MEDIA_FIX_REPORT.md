> Báo cáo dưới đây ghi nhận bản sửa đầu tiên. Tình trạng hình ảnh hiện tại đã được cập nhật tại [IMAGE_VARIETY_REVIEW.md](IMAGE_VARIETY_REVIEW.md).

# Sửa âm thanh và rà hình minh họa — 04/11/2026

Nút nghe từng cảnh trước đây chỉ gọi SpeechSynthesis của trình duyệt. Chế độ phim tìm MP3 nhưng source chưa kèm file nào, sau đó phụ thuộc giọng Việt của máy. Đây là nguyên nhân không có âm thanh trên máy thiếu giọng Việt. Ngoài ra, lỗi media có thể đồng thời phát sự kiện `error` và từ chối promise `play()`, làm khởi động TTS dự phòng hai lần; thanh tiến độ cũng không chạy lại sau tiếp tục.

Đã tích hợp tạo MP3 bằng Edge TTS, giọng `vi-VN-HoaiMyNeural`, tốc độ `-8%`. Mỗi cảnh đọc tiêu đề, lời dẫn và thoại, tương ứng cùng một nội dung ở cả hai trình phát. Script lưu vào cả bản Next và standalone, chỉ tạo lại khi nội dung/giọng/tốc độ thay đổi, thử lại lỗi mạng và chỉ công bố file hoàn chỉnh. Không cần API key. Thư viện cộng đồng dùng dịch vụ đọc trực tuyến của Microsoft, cần Internet khi tạo, không có cam kết ổn định như API thương mại; phát MP3 có sẵn không phụ thuộc dịch vụ này.

Nút nghe từng cảnh, Tự kể và chế độ phim đều ưu tiên MP3. Tạm dừng/tiếp tục giữ thời gian; dừng rồi phát bắt đầu lại cảnh. Có thông báo khi không tải được file, thiếu giọng Việt hoặc bị trình duyệt chặn phát. TTS dự phòng chỉ khởi động một lần và không chọn giọng khác ngôn ngữ.

Nguồn kỹ thuật: [Edge TTS](https://github.com/rany2/edge-tts). FPT.AI vẫn là tùy chọn với key của chủ tài khoản; [bảng giá chính thức](https://docs.fpt.ai/docs/vi/speech/documentation/tts-pricing/) nêu gói miễn phí 100.000 ký tự/tháng có hạn mức yêu cầu. Không có key dùng chung được nhúng vào frontend.

Đã đọc nội dung đủ 55 cảnh, kiểm tra ảnh thực tế và metadata Commons, tải đủ 29 ảnh vào hai bản web. Đã sửa gán ảnh tại 10 cảnh:

| Cảnh | Điều chỉnh |
|---|---|
| C01_S01 | Chân dung → nhà máy cao su Nam Kỳ thập niên 1920, phù hợp bối cảnh lao động |
| C01_S04 | Bố cáo Nghệ Tĩnh → Nguyễn Ái Quốc, ghi rõ đây là chân dung 1924 |
| C02_S03 | Nguyễn Ái Quốc → Trần Phú, phù hợp chủ đề Luận cương 1930 |
| C04_S01 | Đảo chính tháng 3 → mít tinh cuối tháng 8/1945 |
| C04_S02 | Binh lính Pháp bị bắt → Nguyễn Ái Quốc, ghi rõ ảnh nhân vật chụp trước 1941 |
| C08_S03 | Mậu Thân 1968 → lễ ký Hiệp định Paris 27/1/1973 |
| C10_S02, C11_S02 | Ruộng → máy dệt tại Việt Nam năm 2022, ghi rõ minh họa về sau |
| C11_S03 | Phố Hà Nội → trụ sở ASEAN, ghi rõ ảnh 2010, không phải lễ gia nhập 1995 |
| C11_S04 | Phố Hà Nội → trụ sở WTO, ghi rõ ảnh 2001, không phải lễ gia nhập 2007 |

Ảnh `Vietnamese rice fields.jpg` thực tế là hòn non bộ dù tên file nói về ruộng. Đã thay bằng ảnh ruộng gần Đà Lạt năm 2015 của P. Hughes, CC BY 4.0, và sửa năm/tác giả/nguồn ở tất cả nơi dùng.

Phân loại cuối: 15 cảnh gắn trực tiếp chủ đề/sự kiện, 26 cảnh minh họa bối cảnh, 14 cảnh cần tư liệu sát hơn. Các cảnh cần bổ sung là C02_S04, C05_S02, C05_S04, C06_S03, C07_S02–S05, C08_S04, C09_S01, C09_S03–S04, C10_S03–S04. Ví dụ: lớp Bình dân học vụ vẫn dùng ảnh chống đói cùng thời; cải cách giá–lương–tiền vẫn dùng ảnh ruộng. Giới hạn này được ghi trên chú thích mỗi cảnh và trong “Bối cảnh ảnh” ở chế độ phim. Bảng đầy đủ: [media_story_review.csv](media_story_review.csv); nguồn và giấy phép: [MEDIA_CREDITS.md](MEDIA_CREDITS.md).

Kiểm tra tự động gồm phát MP3 thật trên Chromium 1440×900 và 390×844, phát lại, giữ vị trí tạm dừng, chuyển cảnh bằng sự kiện kết thúc thật; giả lập thiếu MP3/thiếu giọng Việt/chặn play; kiểm tra không khởi động TTS dự phòng hai lần. `tests/audio_playback.py` còn giải mã đủ 55 MP3 và đo năng lượng mẫu PCM để phát hiện file rỗng/im lặng; kết quả ở `tests/audio_decode_report.json`. Kiểm thử giao diện, cấu trúc nội dung, media và Next static build được chạy cùng bản sửa.

Việc rà độ phù hợp của hình không thay thế thẩm định các dữ kiện lịch sử hoặc phê duyệt quyền sử dụng cuối cùng.
