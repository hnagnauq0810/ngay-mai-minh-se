"""Copy selected built-in imagegen outputs into the project; encode web assets."""
from pathlib import Path
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]


def main():
 from PIL import Image
 catalog=json.loads((ROOT/'artwork/generated_catalog.json').read_text(encoding='utf-8'));assets=[]
 prompts=['# Prompt set for the story illustrations','','Mode: built-in `image_gen`, via the imagegen skill. Each image is generated separately. Original PNGs are preserved in `artwork/generated-originals/`; web files are in `public/assets/illustrations-ai/`.','']
 for source in catalog['assets']:
  record=dict(source);mid=record['id'][3:]
  original=ROOT/'artwork/generated-originals'/(mid+'.png');original.parent.mkdir(parents=True,exist_ok=True)
  generated=Path(source['original'])
  if generated.is_file() and generated.resolve()!=original.resolve():shutil.copy2(generated,original)
  if not original.is_file():raise FileNotFoundError(f'Missing original illustration: {original}')
  output=ROOT/'public'/record['local'];output.parent.mkdir(parents=True,exist_ok=True)
  im=Image.open(original).convert('RGB');im.save(output,'WEBP',quality=92,method=6)
  mirror=ROOT/'standalone'/record['local'];mirror.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(output,mirror)
  prompts.extend(['## '+record['id'],'',record.pop('prompt'),''])
  record.pop('original');record['original']='artwork/generated-originals/'+original.name;assets.append(record)
 (ROOT/'content/ai_illustrations.v3.json').write_text(json.dumps({'assets':assets},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/'artwork/IMAGE_PROMPTS.md').write_text('\n'.join(prompts)+'\n',encoding='utf-8')
 print(f'Prepared {len(assets)} individually generated illustrations and their prompt set')


if __name__=='__main__':main()
