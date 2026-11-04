"""Decode all served visuals and verify AI disclosure in reader/cinema on both layouts."""
import argparse
import asyncio
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from urllib.parse import urlsplit
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
 base_path=''
 def log_message(self,*args):pass
 def do_GET(self):
  if self.base_path and not self.path.startswith(self.base_path+'/'):
   self.send_error(404);return
  super().do_GET()
 def translate_path(self,path):
  if self.base_path and path.startswith(self.base_path+'/'):path=path[len(self.base_path):]
  return super().translate_path(path)
 def handle(self):
  try:super().handle()
  except (ConnectionResetError,ConnectionAbortedError,BrokenPipeError):pass


async def main(directory,base_path='',remote_url=None):
 server=None
 if remote_url:
  url=remote_url.rstrip('/')+'/'
 else:
  Handler.base_path=base_path.rstrip('/')
  server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT/directory)))
  threading.Thread(target=server.serve_forever,daemon=True).start()
  url=f'http://127.0.0.1:{server.server_port}{Handler.base_path}/'
 origin=urlsplit(url).netloc
 try:
  async with async_playwright() as p:
   browser=await p.chromium.launch(headless=True)
   for width,height in [(1440,900),(390,844)]:
    page=await browser.new_page(viewport={'width':width,'height':height})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    await page.route('**/*',lambda route:route.continue_() if urlsplit(route.request.url).netloc==origin else route.abort())
    await page.goto(url)
    await page.wait_for_function('window.NMMSMedia?.readers.size===55 && !!window.NMMS_CINEMA_DEBUG')
    assert await page.evaluate('[...document.querySelectorAll(".story-scene")].every(s=>s.dataset.audioProfile.includes("Thiện Minh"))')
    data=await page.evaluate('''async()=>{
      const shots=[...NMMSMedia.readers.values()].flatMap(p=>p.shots);
      const paths=[...new Set(shots.map(s=>s.poster||s.src))];
      // Limit concurrent requests while decoding every raster/SVG/poster.
      for(let i=0;i<paths.length;i+=6)await Promise.all(paths.slice(i,i+6).map(async path=>{
        const im=new Image();im.src=path;await im.decode();
        if(!im.naturalWidth||!im.naturalHeight)throw new Error('Empty image '+path);
      }));
      return {count:paths.length,ai:[...new Set(shots.filter(s=>s.ai_generated).map(s=>s.id))]};
    }''')
    assert data['count']==140 and len(data['ai'])==14,data
    assert 'MINH HỌA TÁI DỰNG (AI)' in await page.locator('#PRO_S02 .archive-category').inner_text()
    await page.locator('#PRO_S02').scroll_into_view_if_needed()
    await page.screenshot(path=str(ROOT/f'tests/illustrated_reader_{width}.png'))
    await page.locator('.cinema-open-btn').click()
    await page.evaluate('NMMS_CINEMA_DEBUG.move(1,false)')
    await page.wait_for_function('document.querySelector("#cinema-media-image").complete && document.querySelector("#cinema-media-image").naturalWidth>0')
    assert 'MINH HỌA AI' in await page.locator('#cinema-source-text').inner_text()
    assert await page.locator('#cinema-source-link').is_hidden()
    box=await page.locator('#cinema-media-backdrop').bounding_box()
    assert box and box['height']>=160
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    await page.screenshot(path=str(ROOT/f'tests/illustrated_cinema_{width}.png'))
    assert not errors,errors
    print(f'PASS {url} {width}: all 140 visuals decode; male voice retained; 14 AI illustrations disclosed; gallery/cinema visible')
    await page.close()
   await browser.close()
 finally:
  if server:server.shutdown();server.server_close()


if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--directory',choices=['standalone','out'],default='out')
 parser.add_argument('--base-path',default='');parser.add_argument('--url')
 args=parser.parse_args();asyncio.run(main(args.directory,args.base_path,args.url))
