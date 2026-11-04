"""Collect primary Commons metadata and local previews for storyboard artwork."""
from pathlib import Path
import html
import io
import json
import re
import shutil
import time
import urllib.parse
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
ITEMS=[
 ('pac_bo','Pác Bó.jpg','Suối Lê Nin tại Pác Bó','Ảnh di tích chụp về sau, minh họa địa điểm hoạt động; không phải ảnh năm 1941.','contemporary'),
 ('dong_khe_1950','Ho Chi Minh in Dong Khe, 1950.jpg','Hồ Chí Minh tại mặt trận Đông Khê năm 1950','Tư liệu chiến dịch Biên giới năm 1950.','archive'),
 ('congress_1951','Dai hoi Dai bieu toan quoc lan thu hai, Dang cong san VN.jpg','Đại hội II năm 1951','Tư liệu Đại hội II, không phải Đại hội VI năm 1986.','archive'),
 ('congress_1951_report','ICP 1951c, II Party Congress.jpg','Trường Chinh trình bày báo cáo tại Đại hội II','Tuyên Quang, tháng 2/1951.','archive'),
 ('land_reform_farmer','Cai cach ruong dat5.jpg','Người nông dân trong bối cảnh cải cách ruộng đất','Ảnh gắn với cải cách ruộng đất; không thay thế việc trình bày những sai lầm và quá trình sửa sai.','archive'),
 ('land_reform_titles','Cải cách ruộng đất thắng lợi, nông dân vui sướng đốt văn tự cũ.jpg','Nông dân đốt văn tự ruộng đất cũ','Tư liệu một khía cạnh phong trào; không phải ảnh về quá trình sửa sai 1956–1957.','archive'),
 ('trail_map','HoCMT.png','Sơ đồ tuyến vận tải Trường Sơn','Bản đồ giải thích tuyến đường; không phải ảnh chụp đường Trường Sơn.','archive'),
 ('trail_people','HoChiMinhTrial001.jpg','Vận chuyển trên đường Trường Sơn','Ảnh lưu trữ về vận tải trên tuyến đường Trường Sơn.','archive'),
 ('trail_bicycles','HoTrial001.jpg','Xe đạp vận tải trên tuyến Trường Sơn','Ảnh tư liệu hậu cần; không phải ảnh riêng chiến dịch Điện Biên Phủ.','archive'),
 ('b52_museum','B-52 wreckage.jpg','Xác máy bay trưng bày tại Bảo tàng Chiến thắng B-52','Ảnh hiện vật chụp về sau; không phải hình quay trong cuộc tập kích năm 1972.','contemporary'),
 ('border_vehicle','Soviet GAZ-66 Truck of 1979.jpg','Xe GAZ-66 trong trưng bày lịch sử quân sự','Ảnh bảo tàng năm 2025, gợi nhiệm vụ hậu cần; không phải ảnh chiến trường năm 1979.','contemporary'),
 ('lang_son_damage','Facade with Damage from 1979 Sino-Vietnamese War - Lang Son - Vietnam (48142922346).jpg','Dấu tích chiến tranh tại Lạng Sơn','Ảnh dấu tích chụp về sau, gắn với chiến tranh biên giới 1979.','contemporary'),
 ('ration_coupons','Tem phiếu thời bao cấp.jpg','Tem phiếu mua thực phẩm thời bao cấp','Ảnh hiện vật chụp năm 2007; minh họa cơ chế phân phối, không phải ảnh chợ năm 1985.','contemporary'),
 ('subsidy_display','Thoi bao cap.jpg','Hiện vật đời sống thời bao cấp','Ảnh trưng bày chụp về sau, minh họa vật dụng và sinh hoạt thời bao cấp.','contemporary'),
 ('banknote_1988_back','Vietnam 500 dong banknote, 1988 back side.jpg','Mặt sau tờ 500 đồng phát hành năm 1988','Ảnh tiền năm 1988; không phải tiền trong cuộc đổi tiền năm 1985.','contemporary'),
 ('banknote_1988_front','Vietnam 500 dong banknote, 1988 obverse side.jpg','Mặt trước tờ 500 đồng năm 1988','Ảnh tiền năm 1988; chỉ minh họa tiền tệ ở chặng Đổi mới.','contemporary'),
 ('trainees_1985','Bundesarchiv Bild 183-1985-0716-003, Plauen, Auszubildende aus Vietnam.jpg','Học viên Việt Nam học nghề tại Plauen năm 1985','Ảnh học nghề tại CHDC Đức năm 1985; không phải xưởng quốc doanh ở Việt Nam.','archive'),
 ('floating_market','Floating Market - Can Tho - Vietnam.JPG','Chợ nổi tại Cần Thơ','Ảnh chụp về sau minh họa giao thương vùng đồng bằng; không phải mốc gia nhập ASEAN hoặc WTO.','contemporary'),
 ('factory_workers','Shell-button-factory-vietnam.jpg','Lao động trong nhà máy tại Việt Nam','Ảnh hoạt động sản xuất, minh họa lao động công nghiệp; xem ngày chụp tại nguồn.','contemporary'),
 ('factory_today','Nhà máy Song Thắng.jpg','Một nhà máy tại Việt Nam','Ảnh nhà máy chụp về sau, không phải tư liệu cơ chế quản lý năm 1981.','contemporary'),
 ('school_today','Các em học sinh chúc mừng cô giáo nhân ngày 20 tháng 11, 2025.jpg','Học sinh và cô giáo trong ngày Nhà giáo Việt Nam','Ảnh năm 2025 minh họa đời sống học đường; không phải lớp Bình dân học vụ năm 1945.','contemporary'),
]


def fetch(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NMMS/1.4 educational storyboard research'}),timeout=35) as response:return response.read(20_000_001)
  except urllib.error.HTTPError as exc:
   if exc.code!=429 or attempt==3:raise
   time.sleep(3*(attempt+1))


def main():
 from PIL import Image
 q=urllib.parse.urlencode(dict(action='query',format='json',titles='|'.join('File:'+i[1] for i in ITEMS),prop='imageinfo',iiprop='url|extmetadata|size',iiurlwidth=960))
 source=json.loads(fetch('https://commons.wikimedia.org/w/api.php?'+q))
 (ROOT/'docs/extra_image_source_metadata.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 pages={p['title'][5:]:p for p in source['query']['pages'].values()}
 result=[]
 for mid,filename,caption,note,kind in ITEMS:
  page=pages.get(filename,{})
  if not page.get('imageinfo'):print('MISSING',filename,flush=True);continue
  info=page['imageinfo'][0];m=info.get('extmetadata',{});plain=lambda key:html.unescape(re.sub('<[^>]+>','',m.get(key,{}).get('value',''))).strip()
  license=plain('LicenseShortName')
  if not license:raise RuntimeError('No license metadata: '+filename)
  dest=ROOT/'public/assets/visual'/(mid+'.jpg');dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():
   url=info.get('thumburl',info['url'])
   try:raw=fetch(url)
   except urllib.error.HTTPError:
    q=urllib.parse.urlencode(dict(action='query',format='json',titles='File:'+filename,prop='imageinfo',iiprop='url',iiurlwidth=500))
    p=next(iter(json.loads(fetch('https://commons.wikimedia.org/w/api.php?'+q))['query']['pages'].values()))
    i=p['imageinfo'][0];raw=fetch(i.get('thumburl',i['url']))
   im=Image.open(io.BytesIO(raw));im.load()
   if im.mode!='RGB':
    rgba=im.convert('RGBA');im=Image.new('RGB',rgba.size,'white');im.paste(rgba,mask=rgba.getchannel('A'))
   im.save(dest,quality=90)
  mirror=ROOT/'standalone/assets/visual'/dest.name;mirror.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,mirror)
  date=plain('DateTimeOriginal')
  # Keep noisy Commons HTML date expansions out of the visible UI.
  if len(date)>120:date='Xem ngày chụp tại nguồn'
  result.append(dict(id=mid,filename=filename,caption=caption,note=note,kind=kind,date=date or 'Xem nguồn',author=plain('Artist').replace('Unknown authorUnknown author','Không rõ tác giả'),license=license,license_url=plain('LicenseUrl'),source_url=info['descriptionurl'],local='assets/visual/'+dest.name))
  print('READY',mid,'|',plain('ImageDescription')[:170],'|',date,'|',license,flush=True)
  (ROOT/'content/visual_assets.v2.json').write_text(json.dumps({'assets':result},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  time.sleep(1)


if __name__=='__main__':main()
