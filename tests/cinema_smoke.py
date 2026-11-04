"""Inline Chromium smoke test with simulated MP3 backend. No npm or network needed."""
import asyncio,re,os
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parent.parent
MOCK_AUDIO=r'''
window.Audio = class FakeAudio extends EventTarget {
  constructor(){ super(); this.duration=3.2; this.currentTime=0; this.paused=true; this.src=''; window.lastCinemaAudio=this; }
  play(){ this.paused=false;setTimeout(()=>{if(!this.paused)this.dispatchEvent(new Event('loadedmetadata'))},15);return Promise.resolve(); }
  pause(){this.paused=true;}
  load(){}
  removeAttribute(k){if(k==='src')this.src='';}
  end(){this.dispatchEvent(new Event('ended'));}
};
'''
async def main():
  page_html=(ROOT/'standalone/index.html').read_text(encoding='utf-8')
  # Prevent browser external resource loading, and script loading before mocks.
  page_html=re.sub(r'<link[^>]*>', '', page_html)
  page_html=re.sub(r'<script[^>]*></script>', '', page_html)
  async with async_playwright() as p:
    browser=await p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or None,args=['--no-sandbox','--disable-gpu'])
    for w,h in [(1440,900),(390,844)]:
      page=await browser.new_page(viewport={'width':w,'height':h})
      errors=[]
      page.on('pageerror',lambda e: errors.append(str(e)))
      await page.set_content(page_html,wait_until='domcontentloaded')
      for name in ('site.css','cinema.css','story-media.css'):
        css=(ROOT/'public/assets'/name).read_text(encoding='utf-8')
        css=re.sub(r'^@import[^\n]*\n','',css)
        await page.add_style_tag(content=css)
      await page.add_script_tag(content=MOCK_AUDIO)
      for name in ('story-media.js','site.js','cinema.js'):
        await page.add_script_tag(content=(ROOT/'public/assets'/name).read_text(encoding='utf-8'))
      assert await page.locator('.story-scene').count()==55
      assert await page.locator('#cinema-layer').is_hidden()
      await page.locator('.cinema-hero-btn').click()
      assert await page.locator('#cinema-layer').is_visible()
      assert await page.evaluate('NMMS_CINEMA_DEBUG.getState()')=='playing'
      assert await page.evaluate('NMMS_CINEMA_DEBUG.getIndex()')==0
      await page.evaluate('lastCinemaAudio.currentTime=1.2')
      await page.locator('#cinema-playpause').click()
      assert await page.evaluate('lastCinemaAudio.currentTime')==1.2
      assert await page.evaluate('NMMS_CINEMA_DEBUG.getState()')=='paused'
      assert await page.locator('#cinema-playpause').inner_text()=='▶ Tiếp tục'
      await page.locator('#cinema-playpause').click()
      assert await page.evaluate('NMMS_CINEMA_DEBUG.getState()')=='playing'
      assert await page.evaluate('lastCinemaAudio.currentTime')==1.2
      # Dispatch audio.end and test seamless change to second scene
      await page.evaluate('lastCinemaAudio.end()')
      await page.wait_for_timeout(80)
      assert await page.evaluate('NMMS_CINEMA_DEBUG.getIndex()')==1
      await page.locator('#cinema-next').click()
      assert await page.evaluate('NMMS_CINEMA_DEBUG.getIndex()')==2
      await page.evaluate('NMMS_CINEMA_DEBUG.move(54,true)')
      assert await page.evaluate('NMMS_CINEMA_DEBUG.getIndex()')==54
      await page.evaluate('lastCinemaAudio.end()')
      assert await page.evaluate('NMMS_CINEMA_DEBUG.getIndex()')==0
      await page.locator('#cinema-stop').click()
      assert await page.evaluate('NMMS_CINEMA_DEBUG.getState()')=='idle'
      await page.locator('#cinema-close').click()
      assert await page.locator('#cinema-layer').is_hidden()
      # Take picture of film itself
      await page.locator('.cinema-hero-btn').click()
      await page.screenshot(path=str(ROOT/f'tests/cinema_{w}.png'))
      assert not errors,errors
      print('PASS cinematic',w,h,'continuous transition, pause, resume, stop, close, screenshot')
      await page.close()
    await browser.close()
if __name__=='__main__':asyncio.run(main())
