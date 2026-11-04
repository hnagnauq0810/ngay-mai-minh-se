from pathlib import Path
import json, shutil, html, re, textwrap, hashlib
from datetime import datetime
from generate_voice_vieneu import units
from narration_profile import load_profile
ROOT=Path(__file__).resolve().parent.parent
HANDOFF=ROOT
SRC=json.loads((HANDOFF/'content/story_manifest.v1.json').read_text(encoding='utf-8'))
CH=json.loads((HANDOFF/'content/chapters.v1.json').read_text(encoding='utf-8'))['chapters']
SC=SRC['scenes']
MEDIA=json.loads((ROOT/'content/media_plan.v1.json').read_text(encoding='utf-8'))
MEDIA_ASSETS={asset['id']: asset for asset in MEDIA['assets']}
SCENE_MEDIA=MEDIA['scene_media']
STORYBOARDS=json.loads((ROOT/'content/storyboard.v2.json').read_text(encoding='utf-8'))['scenes']
VISUAL_ASSETS=dict(MEDIA_ASSETS)
for filename in ('visual_assets.v2.json','video_assets.v1.json','unique_photos.v3.json','ai_illustrations.v3.json','topic_photos.v4.json'):
 VISUAL_ASSETS.update({a['id']:a for a in json.loads((ROOT/'content'/filename).read_text(encoding='utf-8'))['assets']})
NARRATION=load_profile(ROOT)
VOICE_DIRECTORY=NARRATION['directory']
RECORDINGS=ROOT/'public/assets'/VOICE_DIRECTORY
STORY_VOICE_READY=all((RECORDINGS/f'{s["id"]}.mp3').is_file() and (RECORDINGS/f'{s["id"]}.json').is_file() for s in SC)
if STORY_VOICE_READY:
 profiles={json.loads((RECORDINGS/f'{s["id"]}.json').read_text(encoding='utf-8'))['voice'] for s in SC}
 assert profiles=={NARRATION['voice']},'All 55 scenes must match the active narration profile'

def shots_for(scene):
 parts=units(scene);weights=[max(15,len(p['text'])) for p in parts];total=sum(weights)
 timings=json.loads((RECORDINGS/f'{scene["id"]}.json').read_text(encoding='utf-8')) if STORY_VOICE_READY else None
 shots=[];previous=-3.0
 for cue in STORYBOARDS[scene['id']]:
  asset=VISUAL_ASSETS[cue['asset']];segment=cue['segment'];offset=cue['offset']
  fraction=(sum(weights[:segment])+offset*weights[segment])/total
  src=media_image_url(asset) if asset['id'] in MEDIA_ASSETS else asset['local']
  shot={'id':asset['id'],'type':'video' if asset['id'].endswith('_video') else 'image','src':src,'poster':asset.get('poster',''),'caption':asset['caption'],'label':cue['label'],'date':asset['date'],'kind':asset['kind'],'ai_generated':asset.get('ai_generated',False),'author':asset['author'],'license':asset['license'],'source':asset.get('source_url',''),'note':asset.get('note',''),'fraction':round(fraction,5),'segment':segment,'offset':offset}
  if timings:
   part=timings['segments'][segment]
   raw=part['start']+offset*(part['end']-part['start'])
   shot['at']=round(min(max(raw,previous+2.6),max(0,timings['duration']-1.5)),3)
   previous=shot['at']
  shots.append(shot)
 return shots
def media_for(scene_id):
 mid=SCENE_MEDIA.get(scene_id)
 return MEDIA_ASSETS.get(mid) if mid else None
def media_image_url(media):
 local=ROOT / 'public' / media['local'].lstrip('/')
 return 'assets/historical/'+media['id']+'.jpg' if local.is_file() else media['url']
def media_credit(media):
 return ('ẢNH LƯU TRỮ' if media['kind']=='archive' else 'ẢNH CHỤP HIỆN ĐẠI')+' · '+media['date']+' · '+media['author']
STORY_SHOTS={scene['id']:shots_for(scene) for scene in SC}
MEDIA_REVISION=hashlib.sha256(json.dumps(STORY_SHOTS,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]
ASSET_VERSION=hashlib.sha256((MEDIA_REVISION+''.join((ROOT/'public/assets'/name).read_text(encoding='utf-8') for name in ['story-media.js','site.js','cinema.js','site.css','cinema.css','story-media.css'])).encode()).hexdigest()[:16]
root = ROOT
for part in ['app','app/chapters/[slug]','public/assets','generated','content','standalone/assets','standalone/chapters','scripts','tests','docs','.github/workflows']:
 (root/part).mkdir(parents=True,exist_ok=True)
E= lambda s: html.escape(str(s),quote=True)
ACT_INFO={
 'PROLOGUE':('MỞ ĐẦU','Một ngày bình thường','2026'),
 'HỒI I':('HỒI I','Ước mơ được tự quyết định tương lai','1930 — 1945'),
 'HỒI II':('HỒI II','Ước mơ được ở bên nhau','1945 — 1975'),
 'HỒI III':('HỒI III','Ước mơ về ngày mai','1975 — 2026'),
 'EPILOGUE':('KẾT THÚC','Ngày mai, mình sẽ…','2026'),
}
ACT_CSS={'PROLOGUE':'prologue','HỒI I':'act-one','HỒI II':'act-two','HỒI III':'act-three','EPILOGUE':'epilogue'}
INTRO={
'01':('Một đất nước đang tìm đường','Trước khi có một hướng đi chung, đã có biết bao cuộc kiếm tìm.'),
'02':('Những tiếng nói không chịu im lặng','Trong những khoảng lặng, một phong trào vẫn tiếp tục.'),
'03':('Một tờ báo cũng là tiếng nói','Có những cuộc đấu tranh bắt đầu từ lời nói và trang giấy.'),
'04':('Thời cơ không đợi ai','Một thời khắc lịch sử được chuẩn bị qua nhiều năm.'),
'05':('Giữ lấy một ngày bình thường','Độc lập vừa giành được phải đối diện những thử thách mới.'),
'06':('Những con đường không ở trên bản đồ','Đằng sau chiến thắng là sức dân và hậu phương.'),
'07':('Hai nửa của một bầu trời','Hai nhịp sống, hai nhiệm vụ — trong một hành trình lịch sử.'),
'08':('Ngày hai khung hình gặp nhau','Hai miền cùng trải qua một cuộc chiến và những bước ngoặt.'),
'09':('Hòa bình không có nghĩa là hết khó khăn','Sau chiến tranh, công cuộc tái thiết bắt đầu.'),
'10':('Khi cách làm cũ không còn phù hợp','Những khó khăn thực tiễn đặt ra yêu cầu phải đổi mới.'),
'11':('Những cánh cửa dần mở','Chính sách đổi mới làm biến chuyển đời sống từng ngày.'),
'12':('Ngày mai thuộc về ai?','Quá khứ gặp hiện tại, và câu hỏi trở lại với mỗi chúng ta.'),
}
SPLIT={
'C07_S01':('Xây dựng lại cuộc sống, khôi phục kinh tế sau kháng chiến chống Pháp.','Đời sống thay đổi trong bối cảnh chính trị – xã hội phức tạp ở miền Nam.'),
'C07_S02':('Khôi phục kinh tế, cải tạo và xây dựng; những sai lầm cải cách ruộng đất và quá trình sửa sai 1956–1957.','Hoàn cảnh hai miền tiếp tục khác biệt trong những năm sau 1954.'),
'C07_S03':('Miền Bắc tiếp tục những nhiệm vụ kinh tế – xã hội và xây dựng hậu phương.','Nghị quyết 15 (1959), phong trào Đồng khởi 1959–1960, Mặt trận Dân tộc Giải phóng miền Nam (1960).'),
'C07_S04':('Đại hội III (1960): xây dựng chủ nghĩa xã hội và giữ vai trò hậu phương lớn.','Đại hội III (1960): tiếp tục cách mạng dân tộc dân chủ nhân dân, tiền tuyến lớn.'),
'C07_S05':('Chuẩn bị đối phó chiến tranh phá hoại mở rộng.','Hoa Kỳ đưa quân chiến đấu trực tiếp vào miền Nam năm 1965.'),
'C08_S01':('Vừa sản xuất, vừa chiến đấu, chi viện cho miền Nam.','Chiến tranh ngày càng ác liệt, ảnh hưởng sâu sắc đến cuộc sống.'),
'C08_S02':('Mỹ hạn chế rồi chấm dứt ném bom miền Bắc trong năm 1968.','Mậu Thân 1968 tạo tác động chiến lược nhưng cũng gây nhiều tổn thất.'),
'C08_S03':('Phòng không đối phó cuộc tập kích tháng 12/1972, bối cảnh ký kết Hiệp định Paris.','Sau Hiệp định Paris 1973, xung đột tại miền Nam chưa chấm dứt.'),
'C08_S04':('Chi viện cho chiến trường trong cuộc Tổng tiến công mùa Xuân 1975.','Ba chiến dịch Tây Nguyên, Huế–Đà Nẵng, Hồ Chí Minh; thắng lợi 30/4/1975.'),
'C08_S05':('Bắt đầu nhiệm vụ cùng cả nước xây dựng và bảo vệ Tổ quốc.','Chiến tranh kết thúc, xã hội bước vào chặng đường hàn gắn và tái thiết.'),
}

def dialogue(raw):
 lines=[]
 for ln in raw.splitlines():
  ln=ln.strip()
  if not ln:continue
  if ':' in ln:
   a,b=ln.split(':',1)
   lines.append((a.strip(),b.strip().strip('“”\" ')))
  else:
   lines.append(('NHÂN VẬT',ln.strip('“”\" ')))
 return lines

def scene_html(s,i,total):
 id=s['id']; act=s['act']; ch=s['chapter_id']; sclass=ACT_CSS.get(act,'prologue')
 dialog=dialogue(s['dialogue_fiction'])
 dialogs=''.join(f'<div class="dialogue-line"><span class="speaker">{E(who)}</span><p>{E(msg)}</p></div>' for who,msg in dialog)
 split_html=''
 if id in SPLIT:
  north,south=SPLIT[id]
  split_html=f'''<div class="split-lives" aria-label="Hai tuyến truyện Nam và Bắc — minh họa bối cảnh lịch sử">
    <div class="split-panel split-north"><span class="panel-kicker">MIỀN BẮC</span><h4>Một nhịp sống</h4><p>{E(north)}</p></div>
    <div class="split-panel split-south"><span class="panel-kicker">MIỀN NAM</span><h4>Một nhịp sống</h4><p>{E(south)}</p></div></div>
    <p class="split-note">Đây là đối chiếu bối cảnh, không phải lời kể trực tiếp của nhân chứng lịch sử.</p>'''
 note = E(s['historical_notes'])
 m=media_for(id)
 shots=STORY_SHOTS[id]
 voice_dir=VOICE_DIRECTORY if STORY_VOICE_READY else 'voice'
 timing=json.loads((RECORDINGS/f'{id}.json').read_text(encoding='utf-8')) if STORY_VOICE_READY else None
 audio_attrs=f' data-audio-src="assets/{voice_dir}/{E(id)}.mp3" data-audio-profile="'+(E(timing['voice'])+' · giọng kể chuyện' if STORY_VOICE_READY else 'Hoài My')+'"'
 if timing:audio_attrs+=f' data-audio-timing="{E(json.dumps(timing,ensure_ascii=False,separators=(",",":")))}"'
 media_attrs=''; image_html=''
 if m:
  img_url=media_image_url(m)
  media_note=MEDIA.get('scene_review',{}).get(id,{}).get('note',m.get('note',''))
  media_attrs=f' data-media-src="{E(img_url)}" data-media-credit="{E(media_credit(m))}" data-media-caption="{E(m["caption"])}" data-media-note="{E(media_note)}" data-media-source="{E(m["source_url"])}"'
  video_link=('<a class="historical-video-link" href="https://commons.wikimedia.org/wiki/File:Manifestation_%C3%A0_Hano%C3%AF_pendant_la_conf%C3%A9rence_de_Gen%C3%A8ve.webm" target="_blank" rel="noopener noreferrer">Xem phim tư liệu Hà Nội tháng 7/1954 (Wikimedia Commons) ↗</a>' if id=='C07_S01' else '')
  first=shots[0];first_image=first['poster'] if first['type']=='video' else first['src']
  image_html=f'''<figure class="scene-archive-media" data-shots="{E(json.dumps(shots,ensure_ascii=False,separators=(',',':')))}">
     <div class="story-visual-viewport"><img src="{E(first_image)}" alt="{E(first['caption'])}" loading="lazy" decoding="async" referrerpolicy="no-referrer" /></div>
     <div class="story-visual-navigation" aria-label="Chọn tư liệu minh họa cho cảnh"></div>
     <figcaption><span class="archive-category">{'MINH HỌA TÁI DỰNG (AI)' if first.get('ai_generated') else 'ĐỒ HỌA GIẢI THÍCH' if first['kind']=='illustration' else 'TƯ LIỆU MINH HỌA'}</span><strong data-visual-caption>{E(first['caption'])}</strong><span data-visual-credit>{E(first['date'])} · {E(first['author'])} · {E(first['license'])}</span><span class="media-context-note" data-visual-note>{E(first['note'])}</span><a data-visual-source href="{E(first['source'])}" target="_blank" rel="noopener noreferrer" {'hidden' if not first['source'] else ''}>Nguồn & giấy phép ↗</a>{video_link}</figcaption>
  </figure>'''
 return f'''<article class="story-scene reveal {sclass}" id="{E(id)}" data-scene-id="{E(id)}" data-chapter="{E(ch or '')}" data-scene-index="{i}"{media_attrs}{audio_attrs} aria-labelledby="title-{E(id)}">
    <div class="scene-column">
      <div class="scene-meta"><span class="scene-number">{i+1:02d} <span aria-hidden="true">/</span> {total:02d}</span><span class="scene-period">{E(s['period_label'])}</span></div>
      <h3 class="scene-title" id="title-{E(id)}">{E(s['title'])}</h3>
      {image_html}
      {split_html}
      <div class="narration"><p>{E(s['narration'])}</p></div>
      <div class="dialogue" aria-label="Hội thoại tái dựng nghệ thuật"><span class="fiction-label"><span class="fiction-dot"></span> ĐỐI THOẠI HƯ CẤU · TÁI DỰNG NGHỆ THUẬT</span>{dialogs}</div>
      <div class="scene-tools"><button type="button" class="speak-scene" data-speak="{E(id)}" aria-label="Nghe cảnh {E(s['title'])} bằng giọng tiếng Việt"><span class="tool-icon">◖))</span> Nghe câu chuyện <small>(tiếng Việt)</small></button><button type="button" class="copy-scene" data-copy-scene="{E(id)}" aria-label="Sao chép đoạn văn">Sao chép</button><a class="scene-anchor" href="#{E(id)}">Liên kết cảnh ↗</a></div>
      <details class="history-notes"><summary>Bối cảnh & ghi chú kiểm chứng <span aria-hidden="true">＋</span></summary><p>{note}</p><p><strong>Tình trạng:</strong> bản thảo nội dung; chưa có đối chiếu dữ kiện tới từng nguồn và thẩm định học thuật.</p><p><strong>Tài liệu nền:</strong> Giáo trình Lịch sử Đảng Cộng sản Việt Nam (2019) và tài liệu tóm tắt học phần được cung cấp.</p></details>
    </div>
  </article>'''

# HTML fragments for one-page documentary
sections=[]; n=0
for k,group in [('PROLOGUE',[x for x in SC if x['act']=='PROLOGUE']), *[(c['id'],[x for x in SC if x['chapter_id']==c['id']]) for c in CH], ('EPILOGUE',[x for x in SC if x['act']=='EPILOGUE'])]:
 if k in ('PROLOGUE','EPILOGUE'):
  act=k; label,title,period=ACT_INFO[act]; q='Mọi ngày bình thường đều có một lịch sử.' if k=='PROLOGUE' else 'Câu trả lời của bạn là gì?'; section_id='prologue' if k=='PROLOGUE' else 'epilogue'
 else:
  ch=next(c for c in CH if c['id']==k); act=group[0]['act']; label=f"CHƯƠNG {int(k):02d} · {ACT_INFO[act][0]}"; title=INTRO[k][0];period=ch['period'];q=ch['question'];section_id='chuong-'+k
 cover=media_for(group[0]['id'])
 cover_img=('<img class="chapter-cover-image" src="'+E(media_image_url(cover))+'" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" />') if cover else ''
 sections.append(f'''<section class="story-section {ACT_CSS[act]}" id="{section_id}" aria-label="{E(label)}: {E(title)}">
   <div class="chapter-opening">
    <div class="chapter-bg" aria-hidden="true">{cover_img}<div class="chapter-drawing"></div></div>
    <div class="chapter-intro"><span class="eyebrow">{E(label)} <span>—</span> {E(period)}</span><h2>{E(title)}</h2><p>{E(q)}</p><a href="#{E(group[0]['id'])}" class="chapter-enter">Khám phá chương <span aria-hidden="true">↓</span></a></div>
   </div>
   {''.join(scene_html(s,n+i,len(SC)) for i,s in enumerate(group))}
  </section>''')
 n+=len(group)
assert n==55
act_nav=[]
for i,c in enumerate(CH):
 act_nav.append(f'<a class="chapter-link" href="#chuong-{E(c["id"])}" data-chapter-link="{E(c["id"])}"><span class="chapter-index">{int(c["id"]):02d}</span><span class="chapter-link-text"><strong>{E(INTRO[c["id"]][0])}</strong><small>{E(c["period"])}</small></span></a>')
chapterlist=''.join(act_nav)
markup=f'''<a href="#main" class="skip-link">Đi tới nội dung chính</a>
<div class="read-progress" id="read-progress" role="progressbar" aria-label="Tiến độ đọc" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span id="read-progress-fill"></span></div>
<header class="site-header" id="site-header"><a class="brand" href="#top" aria-label="Về đầu câu chuyện"><span class="brand-mark">✳</span><span>NGÀY MAI, <em>MÌNH SẼ…</em></span></a><div class="header-actions"><span class="current-period" id="current-period">1930—2026</span><button type="button" class="control-btn" id="reading-toggle" aria-pressed="false">Chế độ đọc</button><button type="button" class="control-btn menu-toggle" id="menu-open" aria-expanded="false" aria-controls="chapter-drawer"><span class="hamburger" aria-hidden="true">☰</span><span>Mục lục</span></button></div></header>
<main id="main">
<section class="hero" id="top"><div class="hero-art" aria-hidden="true"><img class="hero-cover-image" src="{E(media_image_url(MEDIA_ASSETS['hanoi_today']))}" alt="" fetchpriority="high" referrerpolicy="no-referrer"/><div class="sun-disc"></div><div class="hero-lines"></div><div class="hill-back"></div><div class="hill-front"></div></div><div class="hero-content"><span class="hero-eyebrow">MỘT HÀNH TRÌNH LỊCH SỬ · 1930—2026</span><h1>Ngày mai,<br/><span>mình sẽ…</span></h1><p class="hero-lead">Có những điều bình thường hôm nay từng là ước mơ của nhiều thế hệ.</p><div class="hero-ctas"><a class="primary-cta" href="#prologue">Bắt đầu câu chuyện <span aria-hidden="true">↗</span></a><button type="button" id="open-overview" class="ghost-cta">Xem hành trình <span aria-hidden="true">↓</span></button></div><span class="hero-image-source">Ảnh Hà Nội 2024 · Alexkom000 · <a href="https://commons.wikimedia.org/wiki/File:2024-11-03_Hanoi%27s_Old_Quarter_1.jpg" target="_blank" rel="noopener noreferrer">CC BY 4.0 ↗</a></span><span class="scroll-hint">CUỘN ĐỂ BẮT ĐẦU <span aria-hidden="true">↓</span></span></div><span class="hero-side-label" aria-hidden="true">MỘT CÂU CHUYỆN · BA THẾ HỆ · MỘT ĐẤT NƯỚC</span></section>
<section class="story-brief" id="overview"><div><span class="eyebrow">LỜI DẪN</span><h2>Một câu hỏi.<br/>Gần một thế kỷ.</h2></div><div class="brief-copy"><p>“Mẹ ơi, hòa bình là gì?” Một câu hỏi của đứa trẻ đưa chúng ta trở lại những chặng đường lịch sử: giành độc lập, đấu tranh bảo vệ và thống nhất đất nước, rồi tiếp tục xây dựng và Đổi mới.</p><p>Đây là một tác phẩm kể chuyện dựa trên tư liệu lịch sử. Nhân vật, đối thoại và một số tình huống đời thường là <strong>hư cấu minh họa</strong>, không phải lời kể nhân chứng.</p><div class="act-pills"><a href="#chuong-01">HỒI I · 1930–1945</a><a href="#chuong-05">HỒI II · 1945–1975</a><a href="#chuong-09">HỒI III · 1975–2026</a></div></div></section>
<div class="historic-disclaimer" role="note"><span aria-hidden="true">i</span><p><strong>Phiên bản trải nghiệm / bản thảo nội dung.</strong> 55 cảnh lấy từ kịch bản dự án. Các dữ kiện chưa được gắn nguồn ở mức từng claim hoặc thẩm định cuối cùng; Ảnh tư liệu từ Wikimedia Commons có chú thích nguồn, ngày chụp và giấy phép; tranh tái dựng AI được ghi nhãn riêng. Ảnh đương đại và tranh tái dựng không phải tư liệu trực tiếp của sự kiện lịch sử. Một số ảnh cần rà soát giấy phép trước phát hành.</p></div>
{''.join(sections)}
<section class="reflection" id="reflection"><div class="reflection-inner"><span class="eyebrow">ĐẾN LƯỢT BẠN</span><h2>Ngày mai,<br/><i>mình sẽ…</i></h2><p>Bạn không cần đưa ra một lời hứa lớn lao. Có thể chỉ là một điều nhỏ bạn muốn bắt đầu sau hành trình này.</p><label for="reflection-text">Viết một điều bạn muốn làm</label><textarea id="reflection-text" maxlength="500" rows="3" placeholder="Ngày mai, mình sẽ…"></textarea><div class="reflection-actions"><button type="button" id="save-reflection" class="primary-cta">Lưu trên thiết bị này</button><button type="button" id="copy-reflection" class="ghost-cta">Sao chép</button><button type="button" id="clear-reflection" class="ghost-cta">Xóa</button></div><p class="privacy-note" id="reflection-status" role="status">Nội dung chỉ nằm trong trình duyệt của bạn; website không gửi dữ liệu lên máy chủ.</p></div></section>
<section class="source-section" id="sources"><div class="source-inner"><span class="eyebrow">VỀ TÍNH LỊCH SỬ</span><h2>Ranh giới giữa<br/><i>chuyện kể và sự thật.</i></h2><p>Kịch bản gồm phần thuyết minh lịch sử và đối thoại hư cấu giữa mẹ và con, hoặc các nhân vật tổng hợp. Ảnh tư liệu và ảnh chụp hiện đại được phân biệt ở chú thích mỗi cảnh. Nội dung cần được thẩm định học thuật, bổ sung trích dẫn theo từng dữ kiện và kiểm tra bản quyền tư liệu trước khi công bố.</p><div class="source-grid"><div><strong>Giáo trình nền</strong><p>Giáo trình Lịch sử Đảng Cộng sản Việt Nam, Ban Tuyên giáo Trung ương & Bộ GDĐT, bản 2019 (nguồn do nhóm cung cấp).</p></div><div><strong>Tài liệu học phần</strong><p>Bản tổng hợp kiến thức các chương `ki_9.pdf` (nguồn do nhóm cung cấp; dùng để lập ma trận nội dung).</p></div><div><strong>Kiểm chứng trước công bố</strong><p>Xem <code>content/media_plan.v1.json</code>, <code>docs/MEDIA_CREDITS.md</code> và <code>content/historical_review_queue.csv</code> và hướng dẫn release gate trong source code.</p></div></div></div></section>
</main>
<footer class="site-footer"><a class="brand" href="#top"><span class="brand-mark">✳</span> NGÀY MAI, MÌNH SẼ…</a><p>Một trải nghiệm kể chuyện lịch sử, không phải tài liệu học thuật đã được phê duyệt.</p><a href="#top" class="back-top">Trở lại đầu trang ↑</a></footer>
<div class="drawer-backdrop" id="drawer-backdrop" hidden></div><aside class="chapter-drawer" id="chapter-drawer" aria-label="Mục lục các chương" aria-hidden="true" inert><div class="drawer-top"><div><small>HÀNH TRÌNH</small><h2>12 chương lịch sử</h2></div><button type="button" id="menu-close" class="close-drawer" aria-label="Đóng mục lục">✕</button></div><div class="drawer-groups"><button type="button" class="drawer-reading-control" id="drawer-reading-toggle" aria-pressed="false">Chế độ đọc dễ nhìn</button><span class="drawer-act">HỒI I · 1930–1945</span>{''.join(act_nav[:4])}<span class="drawer-act">HỒI II · 1945–1975</span>{''.join(act_nav[4:8])}<span class="drawer-act">HỒI III · 1975–2026</span>{''.join(act_nav[8:])}<a class="drawer-footer-link" href="#sources">Nguồn & lưu ý lịch sử ↗</a></div></aside>
<div class="voice-dock" id="voice-dock" hidden aria-live="polite"><span id="voice-status">Đang đọc lời dẫn bằng giọng máy…</span><div><button type="button" id="voice-pause">Tạm dừng</button><button type="button" id="voice-stop">Dừng</button></div></div>
'''
# Save generated render fragment as JSON for Next server use.
(root/'generated/pageMarkup.json').write_text(json.dumps({'html':markup,'assetVersion':ASSET_VERSION,'mediaRevision':MEDIA_REVISION},ensure_ascii=False),encoding='utf-8')
(root/'public/assets/storyboard-manifest.json').write_text(json.dumps({'version':1,'revision':MEDIA_REVISION,'scenes':STORY_SHOTS},ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

# standalone uses exactly the markup imported by Next.
index=f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><meta name="theme-color" content="#171d23"/><meta name="description" content="Ngày mai, mình sẽ… — Một website kể chuyện lịch sử Việt Nam từ 1930 đến 2026 qua 55 cảnh và 12 chương."/><title>Ngày mai, mình sẽ… · Hành trình 1930–2026</title><link rel="stylesheet" href="assets/site.css"/><link rel="stylesheet" href="assets/cinema.css"/><link rel="stylesheet" href="assets/story-media.css"/><script src="assets/story-media.js" defer></script><script src="assets/site.js" defer></script><script src="assets/cinema.js" defer></script></head><body>{markup}</body></html>'''
index=re.sub(r'(assets/(?:site|cinema|story-media)\.(?:css|js))',lambda match:match[1]+'?v='+ASSET_VERSION,index)
(root/'standalone/index.html').write_text(index,encoding='utf-8')
for asset in (root/'public/assets').iterdir():
 if asset.is_file(): shutil.copy2(asset,root/'standalone/assets'/asset.name)
for target in ('public/assets/media_plan.v1.json','standalone/assets/media_plan.v1.json'):
 shutil.copy2(root/'content/media_plan.v1.json',root/target)
print('Generated markup',len(markup), 'scene count',len(SC))
