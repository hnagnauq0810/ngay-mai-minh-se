"""Editorial visual cues anchored to the actual words in each narration."""
from pathlib import Path
import json
import re
import unicodedata
from generate_voice_vieneu import units

ROOT=Path(__file__).resolve().parents[1]
# Each tuple is (asset, phrase in narration, short explanation).
# The empty phrase starts on the title. Other cuts follow the sentence and
# within-sentence position of their anchor; exact recording timings are preferred.
PLAN={
 'PRO_S01': [('hanoi_life_video','','Một ngày trên phố'),('school_today','Có thể là đi học','Những dự định học tập'),('ordinary_day','Những dự định ấy nhỏ','Những điều bình thường'),('story_frame','Nhưng lịch sử','Câu hỏi mở ra hành trình')],
 'PRO_S02': [('story_frame','','Mẹ, con và người xem'),('hanoi_today','đã sinh ra trong thời bình','Đời sống thời bình'),('journey_1911','Những câu chuyện sắp tới','Bước vào câu chuyện lịch sử')],
 'C01_S01': [('rubber_factory_1920s','','Lao động thời thuộc địa'),('nguyen_ai_quoc_1921','câu hỏi đang đặt ra','Những con người tìm đường'),('unification_1930','song những nỗ lực','Yêu cầu một hướng đi chung')],
 'C01_S02': [('nguyen_ai_quoc_1921','','Những lựa chọn cứu nước'),('rubber_factory_1920s','Mỗi con đường','Bối cảnh thuộc địa'),('unification_1930','Hiểu điều này','Từ kiếm tìm đến tổ chức')],
 'C01_S03': [('journey_1911','','Các mốc của hành trình'),('nguyen_ai_quoc_1921','Năm 1911','Chân dung nhân vật, ảnh 1924'),('nguyen_ai_quoc_1924','Từ giữa thập niên','Chuẩn bị lý luận và tổ chức')],
 'C01_S04': [('nguyen_ai_quoc_1921','','Trước hội nghị hợp nhất'),('nguyen_ai_quoc_1924','Hội nghị hợp nhất','Người chủ trì hội nghị'),('unification_1930','Ngày 3 tháng 2','Mốc thành lập năm 1930')],
 'C02_S01': [('nghe_tinh_context','','Một gia đình trong biến động'),('rubber_factory_1920s','phong trào đấu tranh','Bối cảnh lao động'),('nghe_tinh_decree','thuế khóa','Văn bản của chính quyền thuộc địa')],
 'C02_S02': [('nghe_tinh_context','','Cao trào 1930–1931'),('nghe_tinh_decree','tại một số địa phương','Tư liệu liên quan Nghệ Tĩnh'),('rubber_factory_1920s','Những thiệt hại này','Bối cảnh thuộc địa, không phải ảnh đàn áp')],
 'C02_S03': [('tran_phu','','Nhân vật gắn với Luận cương'),('political_line','Luận cương tháng 10','Nhiệm vụ và giới hạn nhận định'),('nghe_tinh_decree','thực tiễn','Bối cảnh phong trào, không phải Luận cương')],
 'C02_S04': [('nghe_tinh_decree','','Từ những tổn thất 1930–1931'),('recovery_1935','Chương trình hành động','Các mốc 1932 và 1935'),('nguyen_ai_quoc_1924','Nhìn lại','Nhìn lại một quá trình tổ chức')],
 'C03_S01': [('political_press','','Trang báo và cuộc trò chuyện'),('phan_dang_luu','các yêu cầu về đời sống','Phong trào dân chủ tại Huế'),('world_1936','Lần này','Đấu tranh qua những hình thức mới')],
 'C03_S02': [('world_1936','','Hoàn cảnh quốc tế'),('political_press','Đảng điều chỉnh','Những yêu cầu dân sinh, dân chủ'),('phan_dang_luu','Sự thay đổi này','Ảnh bối cảnh phong trào 1936–1939')],
 'C03_S03': [('political_press','','Những hình thức tập hợp'),('phan_dang_luu','Những phong trào ấy','Con người trong phong trào'),('world_1936','Đấu tranh chính trị','Lựa chọn hình thức theo hoàn cảnh')],
 'C03_S04': [('phan_dang_luu','','Kinh nghiệm từ phong trào'),('world_1936','Những kinh nghiệm','Bối cảnh 1936–1939'),('world_context','Tháng 9/1939','Một giai đoạn mới của thế giới')],
 'C04_S01': [('hanoi_august_1945','','Hà Nội cuối tháng Tám 1945'),('world_context','thời cơ lịch sử','Thời cơ và bối cảnh chiến tranh'),('pac_bo','quay lại những năm','Nhìn lại địa điểm chuẩn bị lực lượng')],
 'C04_S02': [('pac_bo','','Địa điểm gắn với quá trình chuẩn bị'),('nguyen_ai_quoc_1924','Hội nghị Trung ương','Chân dung Nguyễn Ái Quốc, ảnh 1924'),('preparation_1941','Mặt trận Việt Minh','Tập hợp và xây dựng lực lượng')],
 'C04_S03': [('hanoi_march_1945','','Đảo chính tháng 3/1945'),('world_context','Khi Nhật tuyên bố','Thế giới và thời cơ tháng Tám'),('hanoi_august_1945','Nhưng sự nhanh nhạy','Lực lượng đã chuẩn bị từ trước')],
 'C04_S04': [('hanoi_august_1945','','Tổng khởi nghĩa tháng Tám'),('independence_1945','Ngày 2/9/1945','Ngày Tuyên ngôn Độc lập'),('preparation_1941','Thành quả này','Nhìn lại quá trình chuẩn bị')],
 'C05_S01': [('famine_relief','','Ngày vận động chống nạn đói'),('nation_building','Chính quyền mới','Những nhiệm vụ song song'),('literacy','giáo dục','Học đọc, học viết cùng xây dựng đời sống')],
 'C05_S02': [('literacy','','Một lớp học của người lớn'),('nation_building','biết chữ gắn','Giáo dục và đời sống công dân'),('assembly_1946','chính quyền mới','Bối cảnh xây dựng chính quyền')],
 'C05_S03': [('ballot_1946','','Từ lá phiếu đến Hiến pháp'),('assembly_1946','xây dựng chính quyền','Quốc hội khóa I'),('nation_building','Trong cùng thời gian','Tài chính, sản xuất và đoàn kết')],
 'C05_S04': [('nation_building','','Vừa kiến thiết, vừa giữ độc lập'),('independence_1945','Ở miền Bắc','Bối cảnh chính quyền vừa thành lập'),('resistance','chuẩn bị kháng chiến','Chuẩn bị cho cuộc kháng chiến lâu dài')],
 'C06_S01': [('dien_bien_porters','','Công việc của người dân công'),('dien_bien_trench','đưa lương thực','Nhu cầu tiếp tế cho chiến trường'),('resistance','một cuộc kháng chiến lớn','Từ công việc nhỏ đến sức dân')],
 'C06_S02': [('resistance','','Các mặt của cuộc kháng chiến'),('dien_bien_porters','Điều đó có nghĩa','Hậu phương và tiếp vận'),('dien_bien_trench','Từ người dân công','Con người phía trước và phía sau')],
 'C06_S03': [('resistance','','Những nấc phát triển'),('dong_khe_1950','Chiến dịch Biên giới','Biên giới Thu–Đông 1950'),('congress_1951','Đại hội II','Đại hội năm 1951'),('congress_1951_report','Những thắng lợi','Định hướng và tổ chức cuộc kháng chiến')],
 'C06_S04': [('dien_bien_victory','','Điện Biên Phủ năm 1954'),('dien_bien_trench','Thắng lợi là','Chiến đấu và sinh hoạt chiến trường'),('dien_bien_porters','Những chiếc xe đạp','Hậu cần và sức dân')],
 'C06_S05': [('geneva_1954','','Hội nghị Genève 1954'),('hien_luong_today','Ở Việt Nam','Địa điểm gợi giới tuyến tạm thời'),('geneva_hanoi_video','Một niềm hy vọng','Hà Nội trong những ngày hội nghị')],
 'C07_S01': [('hien_luong_today','','Một dòng sông trong ký ức chia cắt'),('two_missions','Người thứ nhất','Hai hoàn cảnh, hai nhiệm vụ'),('geneva_hanoi_video','Từ năm 1954','Bối cảnh dẫn đến giai đoạn chia cắt')],
 'C07_S02': [('land_reform_titles','','Tư liệu về cải cách ruộng đất'),('land_reform_farmer','thành tựu','Một hình ảnh người nông dân'),('reform_lesson','sai lầm nghiêm trọng','Nhìn nhận và sửa sai'),('two_missions','Kể trọn vẹn','Bối cảnh xây dựng miền Bắc')],
 'C07_S03': [('hien_luong_today','','Bối cảnh chia cắt'),('two_missions','Phong trào đấu tranh','Nhiệm vụ tại miền Nam'),('dong_khoi_timeline','Hội nghị Trung ương 15','Các mốc chuyển biến 1959–1960')],
 'C07_S04': [('two_missions','','Hai nhiệm vụ chiến lược'),('trail_map','Trường Sơn','Sơ đồ tuyến đường chi viện'),('trail_people','được xây dựng','Vận chuyển trên tuyến đường'),('trail_bicycles','Hai tuyến câu chuyện','Những mắt xích liên hệ hai miền')],
 'C07_S05': [('hanoi_1966_video','','Tư liệu năm 1966 về chiến tranh mở rộng'),('trail_people','Từ đây','Đời sống và chi viện trong chiến tranh'),('two_missions','Những dự định','Biến động ảnh hưởng cả hai miền')],
 'C08_S01': [('hanoi_1966_video','','Chiến tranh tại miền Bắc, tư liệu 1966'),('trail_bicycles','chi viện tiền tuyến','Một tuyến vận chuyển'),('saigon_1968','Ở miền Nam','Tư liệu Sài Gòn 1968'),('trail_map','thống nhất đất nước','Mối liên hệ giữa hai miền')],
 'C08_S02': [('saigon_1968','','Mậu Thân 1968'),('paris_talks_video','đàm phán tại Paris','Những cuộc đàm phán, phim năm 1972'),('two_missions','Đây là giai đoạn','Đặt các hệ quả trong bối cảnh hai miền')],
 'C08_S03': [('paris_talks_video','','Đàm phán Paris, phim năm 1972'),('b52_museum','Cuối năm 1972','Hiện vật gợi cuộc tập kích'),('paris_1973','Ngày 27/1/1973','Lễ ký Hiệp định Paris'),('two_missions','Nhưng sau hiệp định','Xung đột chưa kết thúc')],
 'C08_S04': [('saigon_1975_street','','Sài Gòn dịp Tết, trước chiến dịch'),('tank_1975_museum','Ngày 30/4/1975','Hiện vật gắn với chiến thắng 1975'),('reconstruction','hai khung hình','Bước chuyển sang hàn gắn và tái thiết')],
 'C08_S05': [('tank_1975_museum','','Một hiện vật của chiến thắng'),('reconstruction','Nhưng ba thập niên','Thiệt hại và tái thiết'),('subsidy_display','Bước sang','Đời sống và những nhiệm vụ mới')],
 'C09_S01': [('reconstruction','','Những việc sau chiến tranh'),('subsidy_display','một mái nhà','Vật dụng đời sống, mô hình trưng bày'),('government_1976','Cả đất nước','Bối cảnh tổ chức nhà nước mới')],
 'C09_S02': [('state_1976','','Các mốc thống nhất nhà nước'),('government_1976','Quốc hội quyết định','Thành viên Chính phủ năm 1976'),('reconstruction','thời kỳ mới','Những nhiệm vụ xây dựng đất nước')],
 'C09_S03': [('ration_coupons','','Hiện vật cơ chế phân phối'),('subsidy_display','Cơ chế tập trung','Một góc đời sống thời bao cấp'),('planning_economy','Từ bữa cơm','Sản xuất, phân phối và động lực')],
 'C09_S04': [('border_defence','','Hai hướng bảo vệ biên giới'),('lang_son_damage','Tháng 2/1979','Dấu tích tại Lạng Sơn, ảnh về sau'),('border_vehicle','nhiệm vụ bảo vệ','Hiện vật hậu cần trong trưng bày')],
 'C10_S01': [('rice_today','','Nông nghiệp, ảnh minh họa năm 2015'),('planning_economy','động lực','Công sức và kết quả sản xuất'),('renewal_timeline','Chỉ thị 100','Mốc điều chỉnh năm 1981')],
 'C10_S02': [('factory_today','','Nhà máy hiện đại để hình dung sản xuất'),('textile_machine_today','Làm thế nào','Máy móc và nguồn lực'),('trainees_1985','Các quyết định','Học viên Việt Nam học nghề năm 1985'),('planning_economy','yêu cầu cải tiến','Bài toán về cơ chế quản lý')],
 'C10_S03': [('price_wage_money','','Ba thành phần của cuộc cải cách'),('ration_coupons','những bất cập','Bối cảnh phân phối thời bao cấp'),('subsidy_display','Nhưng cải cách','Đời sống trong những xáo trộn'),('renewal_timeline','câu chuyện Đổi mới','Đặt thất bại trong tiến trình Đổi mới')],
 'C10_S04': [('renewal_timeline','','Từ tìm tòi đến Đổi mới'),('planning_economy','hạn chế của cơ chế','Những giới hạn của cách quản lý cũ'),('ration_coupons','bao cấp','Hiện vật của cơ chế phân phối'),('factory_workers','Từ đây','Sản xuất ở chặng phát triển về sau')],
 'C11_S01': [('rice_today','','Một cánh đồng, ảnh minh họa về sau'),('renewal_timeline','Năm 1988','Khoán 10 trong tiến trình Đổi mới'),('floating_market','xuất khẩu gạo','Giao thương đồng bằng, ảnh minh họa'),('rice_husk_work_video','tính toán công sức','Lao động và phụ phẩm nông nghiệp ngày nay')],
 'C11_S02': [('trainees_1985','','Một hình ảnh học nghề trước Đổi mới'),('factory_workers','công nghiệp hóa','Lao động công nghiệp về sau'),('textile_machine_today','năng lực sản xuất','Máy móc trong sản xuất hiện đại'),('factory_today','cơ hội phát triển','Một cơ sở sản xuất hiện đại')],
 'C11_S03': [('asean_headquarters','','Trụ sở ASEAN, ảnh năm 2010'),('integration','Ngày 28/7/1995','Mốc gia nhập ASEAN'),('floating_market','thương mại','Giao thương trong đời sống'),('hanoi_life_video','Những đường kết nối','Đô thị trong chặng hội nhập về sau')],
 'C11_S04': [('wto_headquarters','','Trụ sở WTO, ảnh năm 2001'),('integration','ngày 11/1/2007','Mốc gia nhập WTO'),('factory_workers','công nghệ','Con người và năng lực sản xuất'),('metro_construction_video','phát triển bền vững','Hạ tầng ở chặng phát triển về sau')],
 'C12_S01': [('hanoi_life_video','','Trở lại đời sống hôm nay'),('school_today','đi học','Đời sống học đường'),('factory_workers','làm việc','Công việc và lao động'),('ordinary_day','Nhưng không phải','Những yêu cầu của một ngày bình thường')],
 'C12_S02': [('metro_station','','Một khía cạnh phát triển đô thị'),('renewal_timeline','Đổi mới','Nhìn lại các bước chuyển'),('future_goals','2030 và 2045','Các mốc định hướng tương lai'),('hanoi_metro','Bên cạnh','Thành tựu và những việc cần tiếp tục')],
 'C12_S03': [('future_goals','','Định hướng và mục tiêu phía trước'),('metro_construction_video','khoa học','Hạ tầng và công nghệ, tư liệu 2017'),('hanoi_metro','Mục tiêu đến năm 2030','Hình minh họa hiện tại cho mục tiêu tương lai'),('future_goals','Đây là mục tiêu','Phân biệt mục tiêu với thành tựu đã đạt')],
 'C12_S04': [('school_today','','Những cơ hội của thế hệ hôm nay'),('hanoi_traffic_video','Nếu hôm nay','Một nhịp sống đô thị'),('ordinary_day','bạn sẽ muốn','Dự định thuộc về chính bạn')],
 'EPI_S01': [('hanoi_life_video','','Lặp lại những hình ảnh đời thường'),('school_today','con đường đến trường','Học tập trong thời bình'),('journey_1911','tìm đường cứu nước','Nhìn lại điểm đầu hành trình'),('renewal_timeline','Đổi mới','Nhìn lại những bước chuyển'),('ordinary_day','Những điều bình thường','Trở lại câu hỏi của hôm nay')],
 'EPI_S02': [('story_frame','','Một câu hỏi còn mở'),('school_today','học nghiêm túc','Bắt đầu từ học tập'),('factory_workers','làm tốt công việc','Bắt đầu từ công việc'),('hanoi_traffic_video','một việc nhỏ','Một ngày bình thường'),('ordinary_day','quá khứ và hiện tại','Lựa chọn cho ngày mai')],
}


def normalize(text):return unicodedata.normalize('NFC',text).casefold()


def main():
 scenes=json.loads((ROOT/'content/story_manifest.v1.json').read_text(encoding='utf-8'))['scenes']
 replacements=json.loads((ROOT/'content/visual_replacements.v3.json').read_text(encoding='utf-8'))['scenes']
 diagram_replacements=json.loads((ROOT/'content/diagram_replacements.v4.json').read_text(encoding='utf-8'))['scenes']
 assert set(PLAN)=={s['id'] for s in scenes}
 output={};errors=[]
 for scene in scenes:
  parts=units(scene);shots=[]
  original=PLAN[scene['id']];revised=list(original)
  for change in replacements.get(scene['id'],[]):
   matches=[i for i,p in enumerate(original) if p[0]==change['from']]
   index=matches[change.get('occurrence',0)]
   asset,anchor,label=original[index]
   revised[index]=None if change.get('remove') else (change['to'],change.get('anchor',anchor),change.get('label',label))
  for entry in revised:
   if entry is None:continue
   asset,anchor,label=entry
   change=diagram_replacements.get(scene['id'],{}).get(asset)
   if change:asset,label=change['asset'],change['label']
   segment=0;offset=0.0
   if anchor:
    found=next(((i,p) for i,p in enumerate(parts) if p['kind']=='narration' and normalize(anchor) in normalize(p['text'])),None)
    if not found:errors.append(scene['id']+': '+anchor);continue
    segment,part=found;offset=normalize(part['text']).index(normalize(anchor))/max(1,len(part['text']))
   shots.append(dict(asset=asset,anchor=anchor,label=label,segment=segment,offset=round(offset,5)))
  shots.sort(key=lambda s:(s['segment'],s['offset']))
  assert len({s['asset'] for s in shots})>=3,scene['id']
  output[scene['id']]=shots
 if errors:raise SystemExit('Unmatched editorial anchors:\n'+'\n'.join(errors))
 target=ROOT/'content/storyboard.v2.json'
 target.write_text(json.dumps({'version':'2.0','scenes':output},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'Built {sum(map(len,output.values()))} word-anchored visual cues across {len(output)} scenes')


if __name__=='__main__':main()
