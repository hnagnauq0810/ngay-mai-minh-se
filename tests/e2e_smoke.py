"""Browser smoke test (standalone version; same generated HTML/JS/CSS as Next).
Requires playwright Python and a Chromium executable/browser installation.
Launches its own static HTTP server, no npm needed.
"""
import asyncio, os, subprocess, socket, time, re, sys
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parent.parent
PORT=8766
async def main():
 server=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1','--directory',str(ROOT/'standalone')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  await asyncio.sleep(.7)
  async with async_playwright() as p:
   chromium_bin=os.environ.get('CHROMIUM_PATH') or None
   browser=await p.chromium.launch(headless=True,executable_path=chromium_bin,args=['--no-sandbox'])
   for width,height in [(1440,900),(390,844)]:
    page=await browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
    # Test UI offline: archived photos are remote and may be blocked in CI.
    # This deliberately tests captions, layout, and fallback, not Wikimedia reachability.
    await page.route('https://**/*', lambda route: route.abort())
    errors=[]
    page.on('pageerror',lambda err: errors.append(str(err)))
    await page.set_content((ROOT/'standalone/index.html').read_text(encoding='utf-8'),wait_until='domcontentloaded')
    css=(ROOT/'standalone/assets/site.css').read_text(encoding='utf-8')
    css=re.sub(r'@import url\([^;]+;','',css) # remote Google fonts intentionally disabled for offline test
    await page.add_style_tag(content=css)
    await page.add_style_tag(content=(ROOT/'standalone/assets/story-media.css').read_text(encoding='utf-8'))
    await page.add_script_tag(content=(ROOT/'standalone/assets/story-media.js').read_text(encoding='utf-8'))
    await page.add_script_tag(content=(ROOT/'standalone/assets/site.js').read_text(encoding='utf-8'))
    await page.wait_for_timeout(700)
    assert await page.locator('.story-scene').count()==55
    assert await page.locator('.story-section').count()==14
    assert await page.locator('.split-lives').count()==10
    assert await page.locator('.fiction-label').count()==55
    assert await page.locator('#chapter-drawer .chapter-link').count()==12
    assert await page.locator('h1').inner_text()=='Ngày mai,\nmình sẽ…'
    await page.screenshot(path=str(ROOT/f'tests/preview_{width}.png'),full_page=False)
    await page.locator('#menu-open').click()
    assert await page.locator('#chapter-drawer').get_attribute('aria-hidden')=='false'
    await page.keyboard.press('Escape')
    assert await page.locator('#chapter-drawer').get_attribute('aria-hidden')=='true'
    await page.evaluate("location.hash='#C07_S03'")
    await page.wait_for_timeout(800)
    sc=page.locator('#C07_S03')
    assert await sc.is_visible()
    assert await sc.locator('.split-panel').count()==2
    await sc.screenshot(path=str(ROOT/f'tests/split_{width}.png'))
    await page.locator('#reflection-text').fill('Đọc thêm lịch sử gia đình')
    await page.locator('#save-reflection').click()
    assert await page.locator('#reflection-text').input_value()=='Đọc thêm lịch sử gia đình'
    await page.locator('#clear-reflection').click()
    assert await page.locator('#reflection-text').input_value()==''
    assert not errors, f'JavaScript runtime errors: {errors}'
    print(f'PASS viewport {width}x{height}: 55 scenes, 12 chapters, split-screen, drawer, hash, editable reflection, no JS errors (inline-loaded browser test)')
    await page.close()
   await browser.close()
 finally:
  server.terminate()
  try:server.wait(timeout=5)
  except:server.kill()

if __name__=='__main__': asyncio.run(main())
