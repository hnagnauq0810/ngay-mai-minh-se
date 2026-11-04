"""Prepare distinct, source-attributed Commons photographs for the revised cut."""
import html
import io
import json
from pathlib import Path
import re
import shutil
import time
import urllib.parse
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
ITEMS=[
 ('colonial_boulevard','Boulevard Francis Garnier à Hanoï.jpg','Một đại lộ Hà Nội năm 1931','1931','archive'),
 ('colonial_shops','Winkelstraat te Hanoi in Indochina, KITLV 1401885.tiff','Phố buôn bán Hà Nội thời thuộc địa','Thời thuộc địa; xem nguồn','archive'),
 ('colonial_lake','AP0024-Sallet Hanoï, 1930 – Vue aérienne – Le Petit Lac et ses alentours.jpg','Hồ Hoàn Kiếm và khu phố năm 1930','1930','archive'),
 ('colonial_fair','AP0012-Sallet Hanoï, vers 1930 – Vue aérienne – La Foire et le Musée économique.jpg','Khu hội chợ và bảo tàng kinh tế ở Hà Nội','Khoảng 1930','archive'),
 ('physics_class','Một buổi dạy học Vật lý tại Đại học Đông Dương (1929-1933).png','Một lớp Vật lý tại Đại học Đông Dương','1929–1933','archive'),
 ('university_1937','Toàn cảnh Viện Đại học Đông Dương năm 1937.jpg','Viện Đại học Đông Dương năm 1937','1937','archive'),
 ('press_1939_front',"L'Effort Indochinois (Journal Autonomiste Paraissant la Vendredi) - 29 September 1939 issue 01.jpg",'Báo L’Effort Indochinois, số ra ngày 29/9/1939','29/09/1939','archive'),
 ('nguyen_tours','Comrade Nguyen Ai Quoc at the national congress of the Socialist Party of France in the city of Tous, France in December 1920.jpg','Nguyễn Ái Quốc tại Đại hội Tours','12/1920','archive'),
 ('nguyen_marseille',"Nguyen Aïn Nuä'C (Ho-Chi-Minh), délégué indochinois, Congrès communiste de Marseille, 1921, Meurisse, BNF Gallica.jpg",'Nguyễn Ái Quốc tại Marseille, ảnh báo chí Meurisse','1921','archive'),
 ('nguyen_1922','Portrait dated 1922 of Ho Chi Minh.jpg','Chân dung Nguyễn Ái Quốc năm 1922','1922','archive'),
 ('vietminh_training','1945 Aug 16 Deer Team train Vietminh.png','Tư liệu huấn luyện lực lượng Việt Minh tháng 8/1945','08/1945','archive'),
 ('august_17','Rencontre au Grand Opéra de Hanoï le 17 août 1945.jpg','Tụ họp tại Nhà hát Lớn Hà Nội ngày 17/8/1945','17/08/1945','archive'),
 ('august_28','Ngày 28-08-1945, Đoàn giải phóng quân ở Việt Bắc về duyệt binh ở quảng trường Nhà hát Lớn - Hà Nội.jpg','Đoàn quân tại quảng trường Nhà hát Lớn Hà Nội','28/08/1945','archive'),
 ('independence_dais','Toàn cảnh lễ đài tại Quảng trường Ba Đình - Hà Nội, ngày 02-09-1945.jpg','Lễ đài tại Quảng trường Ba Đình ngày Độc lập','02/09/1945','archive'),
 ('assembly_exit','Chủ tịch Hồ Chí Minh tan giờ họp Quốc hội tại Nhà Hát Lớn - Hà Nội, năm 1946 (Trung tâm Lưu trữ quốc gia III, Mục lục Tài liệu ảnh A36).jpg','Tan giờ họp Quốc hội tại Nhà hát Lớn Hà Nội','1946','archive'),
 ('government_1946','Lâm-thời Liên-hiệp Chính-phủ Việt-nam Dân-chủ Cộng-hòa ra mắt Quốc-hội ngày 02 tháng 03 năm 1946.jpg','Chính phủ ra mắt Quốc hội ngày 2/3/1946','02/03/1946','archive'),
 ('office_1946','Chủ tịch Hồ Chí Minh trong phòng làm việc ở khách sạn Royal Monceau, tháng 6 năm 1946.jpg','Hồ Chí Minh làm việc tại Paris tháng 6/1946','06/1946','archive'),
 ('hunger_relief_1946','Cụ Ngô Tử Hạ đọc diễn văn trong cuộc Vận động cứu đói Hà Nội đầu năm 1946.jpg','Vận động cứu đói tại Hà Nội đầu năm 1946','Đầu năm 1946','archive'),
 ('fontainebleau_1946','Bộ trưởng Nguyễn Văn Huyên (thứ hai, từ trái sang) trong phái đoàn Chính phủ Việt Nam đàm phán tại Fontainebleau (Pháp) năm 1946.jpg','Phái đoàn Chính phủ tại Fontainebleau','1946','archive'),
 ('road_engineers','Công binh mở đường vào chiến dịch.jpg','Công binh mở đường vào chiến dịch','Tư liệu chiến dịch; xem nguồn','archive'),
 ('ethnic_porters','Dân công dân tộc vận chuyển hàng ra mặt trận.jpg','Dân công vận chuyển hàng ra mặt trận','Tư liệu hậu cần; xem nguồn','archive'),
 ('dbp_artillery','Artillery in Dien Bien Phu.jpg','Pháo binh tại Điện Biên Phủ','1954','archive'),
 ('southern_resistance','Nambokhangchien.jpg','Tư liệu lực lượng kháng chiến ở Nam Bộ','Ảnh tư liệu; xem nguồn','archive'),
 ('trail_road','HoChiMinhTrail002.jpg','Đường vận chuyển trong hệ thống Trường Sơn','Ảnh tư liệu; xem nguồn','archive'),
 ('trail_trucks','HoChiMinhTrail003.jpg','Chuẩn bị hàng tiếp tế trên tuyến Trường Sơn','Ảnh tư liệu; xem nguồn','archive'),
 ('saigon_deserted','A deserted street in Saigon during the Tet fighting.jpg','Một con phố Sài Gòn trong Tết Mậu Thân','1968','archive'),
 ('saigon_repair','Cable repair, Cholon, February 1968.jpg','Sửa chữa đường dây tại Chợ Lớn','02/1968','archive'),
 ('saigon_after_tet','Cholon after Tet Offensive operations 1968.jpg','Chợ Lớn sau những trận đánh Mậu Thân','1968','archive'),
 ('paris_aftermath','Mine explosion Operation End Sweep 9 March 1973.jpg','Gỡ thủy lôi ngoài khơi Hải Phòng sau Hiệp định Paris','09/03/1973','archive'),
 ('surrender_1975','Surrender letter of Duong Van Minh.JPG','Văn bản đầu hàng của Dương Văn Minh','1975; bản chụp hiện vật','contemporary'),
 ('victory_celebration',"Vietnam Victory Celebration Lai Van Ncoc charge d'affaires Apr 1975.jpg",'Một buổi chào mừng thắng lợi tháng 4/1975','04/1975','archive'),
 ('port_container','Container Ship at the Hai Phong International Container Terminal 01.jpg','Tàu container tại cảng Hải Phòng','Ảnh chụp về sau; xem nguồn','contemporary'),
 ('port_cranes','07-HAIPHONG PORT.jpg','Cảng Hải Phòng và hoạt động giao thương','Ảnh chụp về sau; xem nguồn','contemporary'),
 ('city_skyline','Skyline sông Cấm Hải Phòng năm 2026.jpg','Không gian đô thị bên sông Cấm','2026; xem ngày chụp tại nguồn','contemporary'),
 ('factory_knit','Knitted-clothing-factory.jpg','Một xưởng dệt may tại Việt Nam','Ảnh hiện đại; xem nguồn','contemporary'),
 ('factory_electronics','Exxelia Usine - Vietnam.jpg','Một cơ sở sản xuất điện tử tại Việt Nam','Ảnh hiện đại; xem nguồn','contemporary'),
 ('factory_bricks','Brick Making Factory - Hoi An (12050887515).jpg','Lao động sản xuất gạch tại Hội An','Ảnh hiện đại; xem nguồn','contemporary'),
 ('rice_mill','Một nhà máy xay lúa ở Mỹ Quý.jpg','Nhà máy xay lúa tại Mỹ Quý','Ảnh hiện đại; xem nguồn','contemporary'),
 ('students_hallway','HCMC Students in hallway.JPG','Sinh viên trong khuôn viên trường học','Ảnh hiện đại; xem nguồn','contemporary'),
 ('students_studying','HCMC Two students studying.JPG','Hai sinh viên cùng học tập','Ảnh hiện đại; xem nguồn','contemporary'),
 ('students_drawing','HCMC Uni Drawing Class 01.JPG','Một lớp học vẽ tại Thành phố Hồ Chí Minh','Ảnh hiện đại; xem nguồn','contemporary'),
 ('students_1952','Hanoi students on a lunch break leave school with briefcases and bicycles, 1952.jpg','Học sinh rời trường tại Hà Nội năm 1952','1952','archive'),
 ('hanoi_1999_bridge','Vietnam 1999.Hanoi.Pont Long Bien.Pont Paul Doumer (23).jpg','Cầu Long Biên và nhịp sống Hà Nội năm 1999','1999','archive'),
 ('hanoi_1999_street','Vietnam 1999.Hanoi.Rue et motocyclette (25).jpg','Phố Hà Nội và xe máy năm 1999','1999','archive'),
 ('hanoi_florist',"Vietnam vers 1999. Boutique d'une fleuriste.jpg",'Một cửa hàng hoa ở Hà Nội cuối thập niên 1990','Khoảng 1999','archive'),
 ('rice_terraces','Ha Giang rizieres bis.jpg','Ruộng lúa tại Hà Giang','2019','contemporary'),
 ('paddy_fields','Road and paddy fields in Sa Pa, Vietnam, 20240126 1202 3586.jpg','Đường làng và ruộng lúa gần Sa Pa','26/01/2024','contemporary'),
]


def fetch(url,raw=False):
 for attempt in range(2):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NMMS/1.4 educational picture curation'}),timeout=35) as response:
    return response.read(25_000_001) if raw else json.load(response)
  except urllib.error.HTTPError as exc:
   if exc.code!=429 or attempt==1:raise
   time.sleep(3*(attempt+1))


def main():
 from PIL import Image
 pages={}
 for cached in (ROOT/'.cache/image-research').glob('category-*.json'):
  data=json.loads(cached.read_text(encoding='utf-8'))
  pages.update({p['title'][5:]:p for p in data.get('query',{}).get('pages',{}).values()})
 missing=[name for _,name,*_ in ITEMS if name not in pages]
 for start in range(0,len(missing),35):
  names=missing[start:start+35]
  q=urllib.parse.urlencode(dict(action='query',format='json',titles='|'.join('File:'+n for n in names),prop='imageinfo',iiprop='url|extmetadata|size',iiurlwidth=960))
  data=fetch('https://commons.wikimedia.org/w/api.php?'+q)
  pages.update({p['title'][5:]:p for p in data.get('query',{}).get('pages',{}).values()})
 selected={};assets=[];failures=[]
 for mid,name,caption,date,kind in ITEMS:
  page=pages.get(name,{});info=page.get('imageinfo',[{}])[0];m=info.get('extmetadata',{})
  plain=lambda key:html.unescape(re.sub('<[^>]+>','',m.get(key,{}).get('value',''))).strip()
  if not info or not plain('LicenseShortName'):
   failures.append(mid);print('MISSING/NO LICENSE',mid,flush=True);continue
  selected[mid]=page
  dest=ROOT/'public/assets/unique-photos'/(mid+'.webp');dest.parent.mkdir(parents=True,exist_ok=True)
  try:
   if not dest.exists():
    try:raw=fetch(info.get('thumburl',info['url']),raw=True)
    except urllib.error.HTTPError:
     q=urllib.parse.urlencode(dict(action='query',format='json',titles='File:'+name,prop='imageinfo',iiprop='url',iiurlwidth=330))
     response=fetch('https://commons.wikimedia.org/w/api.php?'+q);i=next(iter(response['query']['pages'].values()))['imageinfo'][0]
     raw=fetch(i.get('thumburl',i['url']),raw=True)
    im=Image.open(io.BytesIO(raw)).convert('RGB');im.thumbnail((1600,1400));im.save(dest,'WEBP',quality=90)
   mirror=ROOT/'standalone/assets/unique-photos'/dest.name;mirror.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,mirror)
   note=('Tư liệu minh họa đúng bối cảnh hoặc nhân vật được ghi trong chú thích; không phải ảnh tình huống đời thường hư cấu.' if kind=='archive' else 'Ảnh chụp về sau/hiện vật, dùng minh họa; không phải ảnh chụp trực tiếp sự kiện lịch sử được kể.')
   assets.append(dict(id=mid,filename=name,caption=caption,date=date,kind=kind,author=plain('Artist').replace('Unknown authorUnknown author','Không rõ tác giả'),license=plain('LicenseShortName'),license_url=plain('LicenseUrl'),source_url=info['descriptionurl'],local='assets/unique-photos/'+dest.name,note=note))
   print('READY',mid,'|',plain('ImageDescription')[:120],flush=True)
   (ROOT/'content/unique_photos.v3.json').write_text(json.dumps({'assets':assets},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  except Exception as exc:
   failures.append(mid);print('FAILED',mid,str(exc),flush=True)
  time.sleep(.8)
 (ROOT/'docs/unique_photo_sources.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 if failures:raise SystemExit('Unresolved: '+', '.join(failures))


if __name__=='__main__':main()
