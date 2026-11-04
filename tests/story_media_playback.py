"""Real video, image sequences, pause/resume and editorial asset validation."""
import asyncio
import functools
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import threading
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass


async def main():
 server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT/'standalone')))
 threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/'
 try:
  async with async_playwright() as p:
   browser=await p.chromium.launch(headless=True)
   for width,height in [(1440,900),(390,844)]:
    page=await browser.new_page(viewport={'width':width,'height':height},reduced_motion='no-preference')
    await page.route('https://**/*',lambda route:route.abort())
    await page.add_init_script('window.__audios=[];const OriginalAudio=window.Audio;window.Audio=function(...args){const a=new OriginalAudio(...args);__audios.push(a);return a;};')
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    await page.goto(url)
    assert await page.locator('.scene-archive-media[data-shots]').count()==55
    assert await page.evaluate('[...NMMSMedia.readers.values()].every(p=>p.shots.length>=3)')
    await page.locator('.cinema-open-btn').click()
    await page.wait_for_function('document.querySelector("#cinema-media-backdrop video").currentTime>.15')
    await page.wait_for_function('__audios.at(-1).currentTime>.15')
    assert await page.evaluate('document.querySelector("#cinema-media-backdrop video").muted')
    await page.locator('#cinema-playpause').click()
    video_time=await page.evaluate('document.querySelector("#cinema-media-backdrop video").currentTime')
    await page.wait_for_timeout(250)
    assert await page.evaluate('document.querySelector("#cinema-media-backdrop video").paused')
    assert abs(await page.evaluate('document.querySelector("#cinema-media-backdrop video").currentTime')-video_time)<.08
    await page.locator('#cinema-playpause').click()
    await page.wait_for_function('(t)=>document.querySelector("#cinema-media-backdrop video").currentTime>t+.1',arg=video_time)
    await page.locator('#cinema-visual-navigation [aria-label="Tư liệu tiếp"]').click()
    assert await page.evaluate('NMMS_CINEMA_DEBUG.getVisual()')==1
    assert 'học' in (await page.locator('#cinema-source-text').inner_text()).lower()
    await page.wait_for_timeout(300)
    assert await page.evaluate('NMMS_CINEMA_DEBUG.getVisual()')==1
    await page.screenshot(path=str(ROOT/f'tests/story_film_{width}.png'))
    # The illustration area must remain visible above the controls on phones.
    box=await page.locator('#cinema-media-backdrop').bounding_box()
    assert box and box['height']>=150
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    await page.evaluate('window.__seen=[];new MutationObserver(()=>__seen.push(document.getElementById("cinema-media-image").getAttribute("src"))).observe(document.getElementById("cinema-media-image"),{attributes:true,attributeFilter:["src"]});__audios.at(-1).playbackRate=12;')
    await page.wait_for_function('NMMS_CINEMA_DEBUG.getIndex()===1',timeout=9000)
    seen=await page.evaluate('__seen')
    assert any('ordinary_day' in (s or '') for s in seen),seen
    assert any('story_frame' in (s or '') for s in seen),seen
    await page.locator('#cinema-close').click()
    assert await page.evaluate('[...document.querySelectorAll("video")].every(v=>v.paused)')
    assert not errors,errors
    print(f'PASS {width}: real silent video, narration, pause/resume, manual gallery, automatic cuts, usable viewport')
    await page.close()
   page=await browser.new_page(viewport={'width':1440,'height':900},reduced_motion='no-preference')
   await page.route('https://**/*',lambda route:route.abort())
   await page.route('**/assets/video/*.mp4',lambda route:route.abort())
   await page.goto(url)
   await page.locator('.cinema-open-btn').click()
   await page.wait_for_function('document.getElementById("cinema-media-backdrop").classList.contains("video-fallback")')
   assert await page.locator('#cinema-media-image').is_visible()
   assert await page.evaluate('document.getElementById("cinema-media-image").naturalWidth>0')
   assert await page.evaluate('NMMS_CINEMA_DEBUG.getState()')=='playing'
   print('PASS unavailable video: poster remains visible while narration continues')
   await page.close()
   page=await browser.new_page()
   await page.route('https://**/*',lambda route:route.abort())
   await page.goto(url)
   paths=[a['local'] for a in json.loads((ROOT/'content/video_assets.v1.json').read_text(encoding='utf-8'))['assets']]
   result=await page.evaluate('''async(paths)=>{
     const video=document.createElement('video');video.muted=true;video.playsInline=true;document.body.append(video);const result=[];
     for(const path of paths){
       video.src=path;await video.play();
       if(!Number.isFinite(video.duration)||video.duration<.5||!video.videoWidth)throw new Error('Invalid video '+path);
       result.push({path,duration:video.duration,width:video.videoWidth,height:video.videoHeight});video.pause();
     }
     video.remove();return result;
   }''',paths)
   (ROOT/'tests/video_decode_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
   print(f'PASS {len(result)} local MP4 excerpts: browser decode and playback')
   await browser.close()
 finally:server.shutdown();server.server_close()


if __name__=='__main__':asyncio.run(main())
