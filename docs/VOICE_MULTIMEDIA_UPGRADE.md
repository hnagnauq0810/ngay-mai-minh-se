# Giọng kể và tư liệu theo lời dẫn — 04/11/2026

Bản này dùng **Thiện Minh**, một giọng nam miền Bắc thuộc nhóm giọng kể chuyện của [VieNeu v3 Turbo](https://github.com/pnnbao97/VieNeu-TTS). Cả 55 cảnh dùng cùng một giọng. Mô hình chạy cục bộ qua ONNX, không cần API key, không tính phí theo ký tự; người xem nghe MP3 có sẵn. Bộ giọng trước vẫn nằm trong `assets/voice/`, bộ mới nằm trong `assets/voice-story/`.

Mỗi cảnh được thu theo tiêu đề, các câu dẫn và thoại. Có khoảng nghỉ giữa các câu và chuyển phần. File JSON cạnh MP3 lưu thời điểm bắt đầu/kết thúc từng đoạn âm thanh; phụ đề dùng các thời điểm này. Đây vẫn là giọng tổng hợp, mức độ truyền cảm có thể được đánh giá qua mẫu hoặc nghe trực tiếp trong web.

Đã biên tập **181 mốc minh họa trong 55 cảnh**, mỗi cảnh 3–5 mốc, dùng **140 tư liệu khác nhau**. Trong đó có **9 đoạn video ở 12 cảnh**. Các mốc gắn với cụm từ trong lời dẫn, không chia đều thời gian một cách ngẫu nhiên. Chuyển hình dùng thời điểm của câu thu thực tế; vị trí bên trong câu được nội suy theo cụm từ. Có giới hạn giữ hình tối thiểu để những ý liệt kê nhanh không làm hình nhấp nháy.

| Video | Nội dung / phạm vi |
|---|---|
| Hà Nội 2017 | Đô thị, đời sống thời bình; không trình bày là phim quay năm 2026 |
| Phố Hà Nội 2009 | Nhịp sống đô thị về đêm, dùng ở đoạn suy ngẫm cuối |
| Hà Nội 19/7/1954 | Biểu tình trong thời gian Hội nghị Genève; không phải trong phòng đàm phán |
| Paris 1972 | Các nhà đàm phán; lễ ký 27/1/1973 dùng ảnh riêng |
| Tư liệu USAF 1966 | Chiến tranh mở rộng tại miền Bắc; không dùng như phim tháng 12/1972 |
| Thi công metro 2017 | Máy móc và công trường hạ tầng Thành phố Hồ Chí Minh |
| Đồng Tháp 2022 | Lao động và tận dụng trấu, không phải tư liệu Khoán 10 |

Ảnh mới bổ sung gồm Đông Khê 1950, Đại hội II 1951, đường Trường Sơn, cải cách ruộng đất, dấu tích biên giới, tem phiếu, vật dụng bao cấp, học nghề, sản xuất và học đường. Đồ họa SVG giải thích các ý như hợp nhất 1930, Bình dân học vụ, hai nhiệm vụ hai miền, thống nhất nhà nước 1976, giá–lương–tiền 1985 và hội nhập. Đồ họa được gắn nhãn; ảnh bảo tàng, di tích, ảnh hiện tại và bản số hóa ghi rõ phạm vi sử dụng.

Trong chế độ phim, vùng hình/video được tách khỏi lời kể, phù hợp cả màn hình lớn và điện thoại. Trong trang đọc, mỗi cảnh có bộ chọn tư liệu. Bấm nghe từng cảnh sẽ đưa vùng minh họa vào khung nhìn. Có thể xem tư liệu trước/tiếp mà không nhảy âm thanh. Khi lời kể tới mốc mới, hình tự chuyển tiếp.

Video chỉ giữ phần hình, luôn tắt âm thanh gốc, đi cùng trạng thái phát/tạm dừng. Nếu video không tải được, poster còn hiển thị và lời kể vẫn chạy. Thiết bị bật giảm chuyển động dùng poster; người xem có thể chủ động bấm xem đoạn phim.

Nguồn, tác giả, giấy phép và phạm vi cắt đoạn: [MULTIMEDIA_CREDITS.md](MULTIMEDIA_CREDITS.md). Bảng đối chiếu từng cụm từ: [storyboard_cues.csv](storyboard_cues.csv). Các trường hợp cần tư liệu gốc cụ thể vẫn được trình bày dưới dạng minh họa bối cảnh hoặc đồ họa, không nâng thành chứng cứ lịch sử.

Chạy từ thư mục source:

```powershell
python -m http.server 8080 --directory out
```

Chỉnh nội dung hoặc mốc hình:

```powershell
python scripts/build_story_graphics.py
python scripts/build_storyboards.py
.\.venv-voice\Scripts\python.exe scripts/generate_voice_vieneu.py
python scripts/build_site.py
npm.cmd run build
```

Cài môi trường tạo giọng nếu chưa có: `python -m venv .venv-voice`, rồi `.\.venv-voice\Scripts\python.exe -m pip install -r scripts/requirements-story-voice.txt`. Mô hình tải từ nguồn chính thức vào cache ở lần đầu; máy xem web không cần cài môi trường này.

Kiểm tra: `python scripts/validate_storyboards.py`, `python tests/story_media_playback.py`, `python tests/audio_playback.py`, hai smoke test giao diện và `npm.cmd run build`. Báo cáo giải mã âm thanh/video lưu trong `tests/audio_decode_report.json` và `tests/video_decode_report.json`.
