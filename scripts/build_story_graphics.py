"""Create original SVG explanatory diagrams, clearly separated from archival photos."""
from pathlib import Path
import html
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]
GRAPHICS=[
 ('journey_1911','Một hành trình chuẩn bị','1911–1930',[('1911','Rời Tổ quốc tìm đường cứu nước'),('1920','Bước ngoặt lựa chọn con đường'),('THẬP NIÊN 1920','Truyền bá lý luận, đào tạo, tổ chức')],'Đồ họa hành trình được nhắc trong lời dẫn, không phải ảnh đồng thời của các mốc.'),
 ('nghe_tinh_context','Một phong trào và những mất mát','1930–1931',[('CÔNG NHÂN','Phong trào đấu tranh phát triển'),('NÔNG DÂN','Nghệ An và Hà Tĩnh chuyển động'),('THỬ THÁCH','Đàn áp, thiệt hại và tổ chức lại')],'Đồ họa bối cảnh Nghệ Tĩnh; không phải ảnh một cuộc biểu tình cụ thể.'),
 ('political_line','Văn kiện, nhận thức và thực tiễn','Luận cương 10/1930',[('NHẬN ĐỊNH','Nhiệm vụ và lực lượng cách mạng'),('GIỚI HẠN','Những đánh giá chưa đầy đủ'),('THỰC TIỄN','Tiếp tục xem xét và bổ sung')],'Sơ đồ giải thích nội dung lời dẫn, không phải bản chụp Luận cương.'),
 ('recovery_1935','Tổ chức lại sau những tổn thất','1932–1935',[('KHÔI PHỤC','Từng bước xây dựng lại tổ chức'),('1932','Chương trình hành động'),('1935','Đại hội lần thứ I')],'Đồ họa các mốc phục hồi tổ chức, không phải ảnh chụp Đại hội I.'),
 ('world_1936','Lựa chọn hình thức theo hoàn cảnh','1936–1939',[('THẾ GIỚI','Nguy cơ phát xít, bối cảnh mới'),('NHIỆM VỤ','Dân sinh, dân chủ, hòa bình'),('HÌNH THỨC','Công khai kết hợp hoạt động bí mật')],'Đồ họa giải thích bối cảnh phong trào dân chủ, không phải tư liệu báo chí gốc.'),
 ('preparation_1941','Thời cơ được chuẩn bị từ trước','1941–1945',[('1941','Đặt giải phóng dân tộc lên hàng đầu'),('VIỆT MINH','Tập hợp lực lượng rộng rãi'),('CHUẨN BỊ','Căn cứ, tổ chức, lực lượng vũ trang')],'Đồ họa các bước chuẩn bị được nêu trong lời dẫn, không phải ảnh hội nghị.'),
 ('reform_lesson','Nhìn nhận sai lầm để sửa sai','1956–1957',[('THỪA NHẬN','Những sai lầm nghiêm trọng'),('SỬA SAI','Tiến hành sửa sai 1956–1957'),('BÀI HỌC','Kể lịch sử với đầy đủ các mặt')],'Đồ họa nội dung về sửa sai, không phải văn kiện hay ảnh ghi lại quá trình này.'),
 ('dong_khoi_timeline','Những bước chuyển tại miền Nam','1959–1960',[('1959','Hội nghị Trung ương 15'),('1959–1960','Phong trào Đồng khởi, tiêu biểu Bến Tre'),('12 · 1960','Mặt trận Dân tộc Giải phóng miền Nam')],'Đồ họa các mốc trong kịch bản, không phải ảnh phong trào Đồng khởi.'),
 ('planning_economy','Từ sản xuất đến bữa cơm gia đình','Thời bao cấp',[('SẢN XUẤT','Kế hoạch và nguồn vật tư'),('PHÂN PHỐI','Hàng hóa và chế độ tem phiếu'),('ĐỘNG LỰC','Công sức, kết quả, đời sống')],'Sơ đồ cơ chế và những câu hỏi của lời dẫn, không đưa ra số liệu kinh tế mới.'),
 ('ordinary_day','Những dự định rất đỗi bình thường','2026',[('ĐI HỌC','Một bài tập, một điều mới'),('LÀM VIỆC','Hoàn thành công việc hôm nay'),('TRỞ VỀ','Gia đình và những cuộc gặp')],'Đồ họa minh họa dự định đời thường của nhân vật, không phải một câu chuyện nhân chứng.'),
 ('story_frame','Một câu hỏi nối những thế hệ','Khung truyện hư cấu',[('NGƯỜI MẸ','Gợi mở một hành trình lịch sử'),('ĐỨA TRẺ','Đặt câu hỏi từ đời sống hôm nay'),('NGƯỜI XEM','Suy nghĩ về lựa chọn của mình')],'Đồ họa khung truyện mẹ và con; đối thoại và các nhân vật được hư cấu để kể chuyện.'),
 ('unification_1930','Tìm một đường đi chung','1930',[('Trước 1930','Các tổ chức hoạt động riêng rẽ'),('Hương Cảng','Hội nghị hợp nhất'),('03 · 02 · 1930','Một tổ chức, một đường lối')],'Sơ đồ giải thích quá trình hợp nhất, không phải ảnh hội nghị.'),
 ('political_press','Khi trang giấy trở thành tiếng nói','1936–1939',[('DÂN SINH','Đời sống và việc làm'),('DÂN CHỦ','Báo chí, nghị trường, vận động'),('HÒA BÌNH','Những yêu cầu trước mắt')],'Đồ họa biên tập về phong trào dân chủ, không phải trang báo gốc.'),
 ('world_context','Một thế giới đang đổi thay','1939–1945',[('1939','Chiến tranh thế giới bùng nổ'),('1941','Đặt giải phóng dân tộc lên hàng đầu'),('1945','Nhận định và nắm bắt thời cơ')],'Sơ đồ các mốc được nhắc trong lời dẫn; không phải bản đồ chiến sự.'),
 ('literacy','Lần đầu viết được tên mình','1945–1946',[('HỌC ĐỌC','a · b · c'),('HỌC VIẾT','Tên mình, lời mình'),('THAM GIA','Tiếp cận thông tin, đời sống công dân')],'Đồ họa minh họa Bình dân học vụ, không phải ảnh lớp học lịch sử.'),
 ('ballot_1946','Một lá phiếu, một nền tảng pháp lý','1946',[('06 · 01','Tổng tuyển cử'),('QUỐC HỘI','Xây dựng chính quyền mới'),('HIẾN PHÁP','Nền tảng pháp lý năm 1946')],'Đồ họa giải thích tiến trình xây dựng chính quyền, không phải lá phiếu gốc.'),
 ('nation_building','Vừa xây dựng, vừa bảo vệ','1945–1946',[('LƯƠNG THỰC','Vượt qua thiếu thốn'),('GIÁO DỤC','Học đọc, học viết'),('ĐỘC LẬP','Ngoại giao và chuẩn bị kháng chiến')],'Đồ họa các nhiệm vụ trong lời dẫn, không phải tài liệu lưu trữ.'),
 ('resistance','Sức dân phía sau chiến trường','1946–1954',[('HẬU PHƯƠNG','Sản xuất · văn hóa · tổ chức'),('TIẾP VẬN','Lương thực · xe thồ · đường vận tải'),('TIỀN TUYẾN','Chiến đấu và giữ liên lạc')],'Sơ đồ giải thích kháng chiến toàn dân; hình ảnh biểu trưng do dự án biên tập.'),
 ('two_missions','Hai nhiệm vụ liên hệ chặt chẽ','Sau 1954',[('MIỀN BẮC','Khôi phục, xây dựng, hậu phương'),('CHI VIỆN','Tuyến Trường Sơn và đường biển'),('MIỀN NAM','Đấu tranh, tiền tuyến')],'Sơ đồ nhiệm vụ hai miền; không thể hiện một biên giới quốc gia vĩnh viễn.'),
 ('reconstruction','Hòa bình và những việc còn ở phía trước','Sau 1975',[('MÁI NHÀ','Hàn gắn và tìm lại người thân'),('CÔNG VIỆC','Khôi phục sản xuất'),('TRƯỜNG HỌC','Dự định cho thế hệ tiếp theo')],'Đồ họa minh họa đời sống tái thiết, không phải ảnh một gia đình có thật.'),
 ('state_1976','Từ kết thúc chiến tranh đến thống nhất nhà nước','1975–1976',[('11 · 1975','Hiệp thương chính trị'),('25 · 04 · 1976','Tổng tuyển cử cả nước'),('07 · 1976','Quốc hội khóa VI quyết định tên nước')],'Đồ họa phân biệt thắng lợi tháng 4/1975 và thống nhất về mặt nhà nước năm 1976.'),
 ('border_defence','Bảo vệ đất nước sau chiến tranh','Sau 1975',[('TÂY NAM','Bảo vệ biên giới và giúp Campuchia'),('PHÍA BẮC','Chiến tranh tháng 2/1979'),('ĐỜI SỐNG','Tổn thất và nhiệm vụ bảo vệ chủ quyền')],'Sơ đồ chủ đề hai hướng biên giới trong lời dẫn; không phải bản đồ trận đánh.'),
 ('price_wage_money','Vì sao một kỳ vọng có thể không thành?','1985',[('GIÁ','Cải cách cơ chế giá'),('LƯƠNG','Điều chỉnh thu nhập'),('TIỀN','Cải cách tiền tệ và những xáo trộn')],'Đồ họa giải thích ba thành phần giá–lương–tiền; không mô phỏng tờ tiền hay mức giá thật.'),
 ('renewal_timeline','Những nấc chuyển của Đổi mới','1981–1989',[('1981','Chỉ thị 100, tìm cách quản lý mới'),('1986','Đại hội VI, đường lối Đổi mới'),('1988–1989','Khoán 10, trở lại xuất khẩu gạo')],'Sơ đồ các mốc được nói trong kịch bản, không phải văn kiện gốc.'),
 ('integration','Những đường kết nối mở rộng','1995–2007',[('ASEAN · 1995','Hợp tác trong khu vực'),('THƯƠNG MẠI','Năng lực cạnh tranh và thích ứng'),('WTO · 2007','Một chặng hội nhập mới')],'Đồ họa giải thích hội nhập; không phải hình ảnh lễ gia nhập.'),
 ('future_goals','Những mục tiêu còn ở phía trước','2026 → 2045',[('2026','Định hướng cho chặng mới'),('2030','Mục tiêu phát triển đến 2030'),('2045','Tầm nhìn phát triển dài hạn')],'Đồ họa mục tiêu tương lai được nêu trong kịch bản, không trình bày các mục tiêu như thành tựu đã đạt.'),
]


def main():
 assets=[]
 for mid,title,period,points,note in GRAPHICS:
  boxes=[]
  for n,(label,description) in enumerate(points):
   x=70+n*390
   words=description.split();lines=['']
   for word in words:
    if len(lines[-1]+' '+word)>25:lines.append(word)
    else:lines[-1]+=(' ' if lines[-1] else '')+word
   body=''.join(f'<tspan x="{x+25}" dy="{0 if i==0 else 31}">{html.escape(line)}</tspan>' for i,line in enumerate(lines))
   boxes.append(f'<g><rect x="{x}" y="270" width="350" height="230" rx="18" fill="#263c43" stroke="#73918d"/><circle cx="{x+40}" cy="240" r="24" fill="#e4b573"/><text x="{x+40}" y="249" text-anchor="middle" fill="#17252b" font-size="23" font-weight="bold">{n+1}</text><text x="{x+25}" y="320" font-size="24" fill="#f4c885" font-weight="700">{html.escape(label)}</text><text x="{x+25}" y="374" font-size="24" fill="#edf0df">{body}</text></g>')
  svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-label="{html.escape(title)}"><defs><radialGradient id="g"><stop stop-color="#2f5057"/><stop offset="1" stop-color="#13222a"/></radialGradient></defs><rect width="1280" height="720" fill="url(#g)"/><g fill="none" stroke="#73918d" opacity=".25"><circle cx="1150" cy="80" r="190"/><circle cx="1150" cy="80" r="230"/><path d="M50 550H1220 M50 565H1220"/></g><g font-family="Arial, sans-serif"><text x="70" y="75" fill="#d9b77f" letter-spacing="5" font-size="18">NGÀY MAI, MÌNH SẼ… · ĐỒ HỌA GIẢI THÍCH</text><text x="70" y="138" fill="#fff4dd" font-size="37" font-weight="700">{html.escape(title)}</text><text x="70" y="187" fill="#aac5c0" font-size="27">{html.escape(period)}</text><path d="M110 240H930" fill="none" stroke="#d9b77f" stroke-width="3"/>{''.join(boxes)}<text x="70" y="616" fill="#b5c7c2" font-size="19">Minh họa biên tập từ lời dẫn · Không phải ảnh tư liệu hay văn kiện gốc</text><text x="70" y="657" fill="#d9b77f" font-size="20">{html.escape(period)}</text></g></svg>'''
  dest=ROOT/'public/assets/visual'/(mid+'.svg');dest.write_text(svg,encoding='utf-8');mirror=ROOT/'standalone/assets/visual'/dest.name;mirror.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,mirror)
  assets.append(dict(id=mid,caption=title,date=period,kind='illustration',author='Đồ họa của dự án',license='Nội dung dự án',source_url='',local='assets/visual/'+dest.name,note=note))
 (ROOT/'content/graphic_assets.v2.json').write_text(json.dumps({'assets':assets},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'Generated {len(assets)} original explanatory SVGs')


if __name__=='__main__':main()
