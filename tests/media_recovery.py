"""Reproduce deleted-diagram URLs, cached HTML and real image failures in Chromium."""
import asyncio
import functools
import html
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
from playwright.async_api import async_playwright
from visual_variety import Handler

ROOT=Path(__file__).resolve().parents[1]


async def main():
 Handler.base_path='/ngay-mai-minh-se'
 server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT/'standalone')))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 url=f'http://127.0.0.1:{server.server_port}{Handler.base_path}/'
 manifest=json.loads((ROOT/'public/assets/storyboard-manifest.json').read_text(encoding='utf-8'))
 canonical=manifest['scenes']['PRO_S01'];stale=[dict(s) for s in canonical]
 stale[2].update(id='ordinary_day',src='assets/visual/ordinary_day.svg',kind='illustration',ai_generated=False,caption='Old deleted diagram')
 markup=(ROOT/'standalone/index.html').read_text(encoding='utf-8')
 stale_html=re.sub(r'data-shots="[^"]+"',lambda _: 'data-shots="'+html.escape(json.dumps(stale),quote=True)+'"',markup,count=1)
 try:
  async with async_playwright() as p:
   browser=await p.chromium.launch(headless=True)
   async def ready(page):
    await page.route('https://**/*',lambda route:route.abort())
    await page.goto(url)
    await page.wait_for_function('NMMSMedia.readers.size===55 && !!window.NMMS_CINEMA_DEBUG')
   async def visible_picture(page,fragment):
    await page.wait_for_function('''fragment=>{
      const im=document.querySelector('#PRO_S01 .story-visual-viewport img');
      return im.src.includes(fragment)&&!im.hidden&&im.complete&&im.naturalWidth>0;
    }''',arg=fragment)

   # A cached page must receive both fresh pictures and fresh credits, including cinema.
   page=await browser.new_page()
   await page.route(url,lambda route:route.fulfill(body=stale_html,content_type='text/html'))
   await ready(page)
   await page.wait_for_function('!NMMSMedia.readers.get("PRO_S01").shots.some(s=>s.src.endsWith(".svg"))')
   await page.evaluate('NMMSMedia.readers.get("PRO_S01").select(2)')
   await visible_picture(page,'children_morning.webp')
   assert 'AI' in await page.locator('#PRO_S01 .archive-category').inner_text()
   await page.locator('.cinema-open-btn').click()
   await page.evaluate('NMMS_CINEMA_DEBUG.move(0,false)')
   for _ in range(2):await page.locator('#cinema-visual-navigation button').nth(1).click()
   await page.wait_for_function('document.querySelector("#cinema-media-image").src.includes("children_morning.webp")')
   assert 'AI' in await page.locator('#cinema-source-text').inner_text()
   print('PASS cached HTML: removed diagram repaired automatically, with matching reader/cinema image and credits')
   await page.close()

   # An already-mounted legacy item actually produces the 404 shown in the report.
   page=await browser.new_page();await ready(page)
   await page.evaluate('(shots)=>{const p=NMMSMedia.readers.get("PRO_S01");p.shots=shots;p.select(2);}',stale)
   await visible_picture(page,'children_morning.webp')
   assert 'AI' in await page.locator('#PRO_S01 .archive-category').inner_text()
   print('PASS deleted ordinary_day.svg: actual 404 recovers the current replacement without manual refresh')
   await page.close()

   # A genuinely unavailable current photo falls through to another item in the scene.
   page=await browser.new_page()
   await page.route('**/children_morning.webp',lambda route:route.fulfill(status=404,body='missing'))
   await ready(page);await page.evaluate('NMMSMedia.readers.get("PRO_S01").select(2)')
   await visible_picture(page,'hanoi_2024.jpg')
   assert await page.locator('#PRO_S01 [data-visual-caption]').inner_text()==canonical[3]['caption']
   assert await page.locator('#PRO_S01 .story-media-failure').is_hidden()
   print('PASS missing photo: automatically displays another scene image with the correct caption')
   await page.close()

   # Complete loss of images remains retryable and cannot loop indefinitely.
   page=await browser.new_page();await ready(page);available=False
   picture=(ROOT/'public/assets/illustrations-ai/children_morning.webp').read_bytes()
   async def missing(route):
    if available:await route.fulfill(body=picture,content_type='image/webp')
    else:await route.fulfill(status=404,body='missing')
   await page.route('**/missing-test-*.jpg',missing)
   await page.evaluate('''()=>{
     const box=document.createElement('div');box.id='recovery-test';box.className='story-visual-viewport';
     box.append(document.createElement('img'));document.body.prepend(box);
     window.recoveryTest=new NMMSMedia.VisualPlayer(box);
     recoveryTest.setShots([{src:'assets/missing-test-1.jpg',type:'image',caption:'One'},{src:'assets/missing-test-2.jpg',type:'image',caption:'Two'}]);
   }''')
   await page.locator('#recovery-test .story-media-failure').wait_for(state='visible')
   available=True;await page.locator('#recovery-test .story-media-failure button').click()
   await page.wait_for_function('document.querySelector("#recovery-test img").naturalWidth>0 && !document.querySelector("#recovery-test img").hidden')
   assert await page.locator('#recovery-test .story-media-failure').is_hidden()
   print('PASS all images unavailable: bounded recovery and a working retry button')
   await page.close();await browser.close()
 finally:server.shutdown();server.server_close()


if __name__=='__main__':asyncio.run(main())
