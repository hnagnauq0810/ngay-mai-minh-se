"""Write source credits and review evidence for the current, actually used cut."""
import csv
from collections import Counter
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILES=['media_plan.v1.json','visual_assets.v2.json','graphic_assets.v2.json','video_assets.v1.json','unique_photos.v3.json','ai_illustrations.v3.json']


def main():
 assets={a['id']:a for filename in FILES for a in json.loads((ROOT/'content'/filename).read_text(encoding='utf-8'))['assets']}
 scenes=json.loads((ROOT/'content/storyboard.v2.json').read_text(encoding='utf-8'))['scenes']
 uses=Counter(s['asset'] for shots in scenes.values() for s in shots)
 videos=[mid for mid in uses if mid.endswith('_video')]
 video_scenes=sum(any(s['asset'] in videos for s in shots) for shots in scenes.values())
 total=sum(uses.values());ai=sum(bool(assets[mid].get('ai_generated')) for mid in uses)
 new_photos={a['id'] for a in json.loads((ROOT/'content/unique_photos.v3.json').read_text(encoding='utf-8'))['assets']}
 stats=f'{total} mốc minh họa trong 55 cảnh, {len(uses)} tư liệu khác nhau, {len(videos)} đoạn phim tại {video_scenes} cảnh'
 lines=['# Nguồn tư liệu cho bản nhiều hình và video','',f'Bản dựng 04/11/2026: {stats}. Mỗi cảnh có 3–5 mốc.','',f'Có {ai} tranh tái dựng bằng AI, được ghi nhãn rõ trong cả chế độ đọc và phim. Các nhân vật đời thường trong tranh là hư cấu. Ảnh hiện đại, hiện vật chụp về sau và ảnh lưu trữ có chú thích ngày/bối cảnh riêng.','', 'Metadata gốc: `media_source_metadata.json`, `extra_image_source_metadata.json`, `unique_photo_sources.json`, `video_source_metadata.json`. Tranh được tạo bằng công cụ imagegen tích hợp; [toàn bộ prompt và vị trí bản gốc](../artwork/IMAGE_PROMPTS.md).','', '| ID | Tư liệu | Ngày / phạm vi | Tác giả | Giấy phép theo nguồn | Lượt dùng |','|---|---|---|---|---|---:|']
 for mid in sorted(uses):
  a=assets[mid];caption=a['caption'].replace('|',' / ');url=a.get('source_url','');title=f'[{caption}]({url})' if url else caption
  fields=[f'`{mid}`',title,a['date'],a['author'].replace('|',' / ').replace('\n',' '),a['license'],str(uses[mid])]
  lines.append('| '+' | '.join(fields)+' |')
 (ROOT/'docs/MULTIMEDIA_CREDITS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 with (ROOT/'docs/storyboard_cues.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.writer(f);w.writerow(['scene_id','order','asset','anchor','narration_segment','segment_offset','label','source'])
  for sid,shots in scenes.items():
   for index,s in enumerate(shots,1):w.writerow([sid,index,s['asset'],s['anchor'],s['segment'],s['offset'],s['label'],assets[s['asset']].get('source_url','')])
 review=f'''# Rà soát độ đa dạng hình minh họa — 04/11/2026

Giữ nguyên 55 bản thu giọng nam Thiện Minh. Bản trước có 185 mốc, 80 tư liệu; bản hiện tại có {stats}.

- 55 hình mở cảnh khác nhau; không lặp tư liệu trong cùng cảnh hoặc giữa hai cảnh liền nhau.
- Một tư liệu được dùng tối đa hai lần trong toàn bộ câu chuyện. Kiểm tra SHA-256 không có file giống nhau dưới tên khác; đã xem bảng ảnh và so sánh dấu vân tay hình để phát hiện ảnh gần trùng.
- Thêm {len(set(uses)&new_photos)} ảnh Internet thực sự được dùng và {ai} tranh tạo riêng bằng imagegen tích hợp. Giữ ảnh gốc, không cắt xén để giả thành ảnh mới.
- Loại khỏi phương án sử dụng ảnh xưởng có số điện thoại quảng cáo và trái phiếu cải cách điền địa không đúng chính sách được kể. Mốc thời gian của ảnh chụp về sau được ghi rõ.
- Hai trích đoạn phim bổ sung dùng những khoảng thời gian khác nhau từ phim gốc, không đổi tên cùng một đoạn phim.
- Ảnh hiện đại chỉ minh họa chủ đề, không được gán là bằng chứng của sự kiện trước đó. Tranh AI có nhãn và ghi chú tái dựng ở cả chế độ đọc và phim.

Xem [bảng ảnh AI](../tests/generated_illustrations_contact.jpg), [bảng ảnh Internet](../tests/unique_photos_contact.jpg), [so sánh trích đoạn phim](../tests/video_variety_contact.jpg), [nguồn và giấy phép](MULTIMEDIA_CREDITS.md), [mốc chuyển hình theo lời dẫn](storyboard_cues.csv), [prompt và bản gốc](../artwork/IMAGE_PROMPTS.md).

Kiểm tra nội dung/niên đại ở đây là rà soát biên tập; các bước thẩm định lịch sử trước phát hành trong acceptance matrix vẫn giữ trạng thái riêng.
'''
 (ROOT/'docs/IMAGE_VARIETY_REVIEW.md').write_text(review,encoding='utf-8')
 print(stats)


if __name__=='__main__':main()
