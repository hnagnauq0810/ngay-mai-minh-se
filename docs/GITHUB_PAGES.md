# Chạy bản test trên GitHub Pages

Website: https://hnagnauq0810.github.io/ngay-mai-minh-se/

Repository: https://github.com/hnagnauq0810/ngay-mai-minh-se

Mỗi lần push nhánh `main`, workflow **Deploy GitHub Pages** kiểm tra nội dung, ảnh/video, giọng đọc, tạo bản Next.js static export và triển khai thư mục `out/`. Toàn bộ ảnh, video, 55 MP3 giọng nam Thiện Minh được phục vụ từ website; người xem không cần API key.

GitHub Settings → Pages → Build and deployment dùng **GitHub Actions**. `actions/configure-pages` cung cấp đường dẫn dự án vào biến `NEXT_PUBLIC_BASE_PATH` khi build. Chạy local bình thường không cần đặt biến này.

Build và kiểm tra đường dẫn dự án trên PowerShell:

```powershell
$env:NEXT_PUBLIC_BASE_PATH='/ngay-mai-minh-se'
npm.cmd run build
python tests/visual_variety.py --base-path /ngay-mai-minh-se
Remove-Item Env:NEXT_PUBLIC_BASE_PATH
```

Kiểm tra bản online:

```powershell
python tests/visual_variety.py --url https://hnagnauq0810.github.io/ngay-mai-minh-se/
```

Trang test giữ nhãn bản thảo, ghi chú nguồn tư liệu và `noindex`. Thẩm định lịch sử trước phát hành được theo dõi riêng trong acceptance matrix.
