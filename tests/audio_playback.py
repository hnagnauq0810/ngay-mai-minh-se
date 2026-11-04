"""Real MP3 decoding and playback regression tests; no TTS account or OS voice.

Run after generating the bundled MP3s: python tests/audio_playback.py
Requires Playwright + Chromium (python -m playwright install chromium).
"""
import asyncio
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import re
from pathlib import Path
import threading

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


TRACK_AUDIO = """window.__audioLog=[];
const NativeAudio=window.Audio;
window.Audio=function(...args){const a=new NativeAudio(...args);window.__audioLog.push(a);return a;};
window.__speechCalls=0;
window.speechSynthesis.speak=()=>{window.__speechCalls++;};
"""


async def main(skip_decode=False):
    handler = functools.partial(QuietHandler, directory=str(ROOT / 'standalone'))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/'
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            for width, height in [(1440, 900), (390, 844)]:
                page = await browser.new_page(viewport={'width': width, 'height': height}, reduced_motion='reduce')
                await page.route('https://**/*', lambda route: route.abort())
                await page.add_init_script(TRACK_AUDIO)
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                await page.goto(url)
                assert await page.evaluate('__audioLog.length') == 0
                await page.locator('#PRO_S01 .speak-scene').click()
                await page.wait_for_function('__audioLog.at(-1)?.currentTime > .2')
                await page.locator('#voice-pause').click()
                position = await page.evaluate('__audioLog.at(-1).currentTime')
                await page.wait_for_timeout(250)
                assert abs(await page.evaluate('__audioLog.at(-1).currentTime') - position) < .08
                await page.locator('#voice-pause').click()
                await page.wait_for_function('(t)=>__audioLog.at(-1).currentTime > t+.15', arg=position)
                await page.locator('#voice-stop').click()
                await page.locator('#PRO_S01 .speak-scene').click()
                await page.wait_for_function('__audioLog.at(-1)?.currentTime > .1')
                assert await page.evaluate('__audioLog.at(-1).currentTime') < 2
                await page.locator('.cinema-open-btn').click()
                await page.wait_for_function('__audioLog.at(-1)?.currentTime > .2')
                assert await page.locator('#voice-dock').is_hidden()
                await page.locator('#cinema-playpause').click()
                position = await page.evaluate('__audioLog.at(-1).currentTime')
                await page.locator('#cinema-playpause').click()
                await page.wait_for_function('(t)=>__audioLog.at(-1).currentTime > t+.15', arg=position)
                # SimpleHTTPRequestHandler has no byte-range seeking. Accelerate
                # actual playback to exercise a real ended event instead.
                await page.evaluate('__audioLog.at(-1).playbackRate=16')
                await page.wait_for_function('NMMS_CINEMA_DEBUG.getIndex()===1', timeout=7000)
                await page.wait_for_function('__audioLog.at(-1)?.currentTime > .1')
                await page.locator('#cinema-stop').click()
                await page.locator('#cinema-playpause').click()
                await page.wait_for_function('__audioLog.at(-1)?.currentTime > .1')
                assert await page.evaluate('__audioLog.at(-1).currentTime') < 2
                await page.locator('#cinema-media-note summary').click()
                assert await page.locator('#cinema-media-note-text').is_visible()
                assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                assert await page.evaluate('__speechCalls') == 0
                assert not errors, errors
                await page.screenshot(path=str(ROOT / f'tests/audio_cinema_{width}.png'))
                print(f'PASS real MP3 playback {width}: reader, replay, pause/resume, cinema, auto-next, no OS TTS')
                await page.close()

            page=await browser.new_page(reduced_motion='reduce')
            await page.route('https://**/*', lambda route: route.abort())
            await page.add_init_script(TRACK_AUDIO)
            await page.goto(url+'#PRO_S01')
            await page.locator('#PRO_S01 .speak-scene').click()
            await page.locator('#voice-stop').click()
            # Cinema CSS intentionally hides the legacy auto-reader button.
            # Exercise its retained handler after a real user audio activation.
            await page.evaluate('document.getElementById("auto-narrate-toggle").click()')
            await page.wait_for_function('__audioLog.at(-1)?.currentTime > .1')
            await page.evaluate('__audioLog.at(-1).playbackRate=16')
            await page.wait_for_function('__audioLog.at(-1)?.src.endsWith("PRO_S02.mp3") && __audioLog.at(-1).currentTime > .1',timeout=9000)
            assert await page.locator('#auto-narrate-toggle').get_attribute('aria-pressed')=='true'
            await page.locator('#voice-stop').click()
            await page.close()
            print('PASS real MP3 auto-narration: advances to next reading scene')

            # Missing MP3 + no Vietnamese OS voice must show an actionable error.
            page=await browser.new_page(reduced_motion='reduce')
            await page.route('https://**/*', lambda route: route.abort())
            await page.route(re.compile(r'/assets/voice(?:-[a-z0-9]+)*/[^/]+\.mp3'), lambda route: route.abort())
            await page.add_init_script("speechSynthesis.getVoices=()=>[];")
            await page.goto(url)
            await page.locator('#PRO_S01 .speak-scene').click()
            await page.wait_for_function('document.getElementById("voice-status").textContent.includes("chưa có giọng Việt")')
            await page.locator('.cinema-open-btn').click()
            await page.wait_for_function('NMMS_CINEMA_DEBUG.getState()==="idle"')
            assert 'chưa có giọng Việt' in await page.locator('#cinema-feedback').inner_text()
            await page.close()
            print('PASS missing MP3 + missing Vietnamese voice: visible errors in both players')

            # The media error event and rejected play() promise describe the same
            # failure; they must not each start another browser utterance.
            page=await browser.new_page(reduced_motion='reduce')
            await page.route('https://**/*', lambda route: route.abort())
            await page.route(re.compile(r'/assets/voice(?:-[a-z0-9]+)*/[^/]+\.mp3'), lambda route: route.abort())
            await page.add_init_script("""
              window.__spoken=[];
              speechSynthesis.getVoices=()=>[{lang:'vi-VN',name:'Test Vietnamese',localService:true}];
              window.SpeechSynthesisUtterance=class{constructor(text){this.text=text;}};
              speechSynthesis.speak=(u)=>{__spoken.push(u);u.onstart?.();};
            """)
            await page.goto(url)
            await page.locator('#PRO_S01 .speak-scene').click()
            await page.wait_for_function('__spoken.length===1')
            await page.wait_for_timeout(250)
            assert await page.evaluate('__spoken.length')==1
            await page.locator('.cinema-open-btn').click()
            await page.wait_for_function('__spoken.length===2')
            await page.wait_for_timeout(250)
            assert await page.evaluate('__spoken.length')==2
            await page.close()
            print('PASS media failure starts Vietnamese fallback once per player')

            for cinema in (False,True):
                page=await browser.new_page(reduced_motion='reduce')
                await page.route('https://**/*', lambda route: route.abort())
                await page.add_init_script("""
                  const original=HTMLMediaElement.prototype.play;let first=true;
                  HTMLMediaElement.prototype.play=function(){
                    if(first&&this instanceof HTMLAudioElement){first=false;return Promise.reject(new DOMException('Blocked for test','NotAllowedError'));}
                    return original.call(this);
                  };
                """)
                await page.goto(url)
                await page.locator('.cinema-open-btn' if cinema else '#PRO_S01 .speak-scene').click()
                status='#cinema-feedback' if cinema else '#voice-status'
                await page.wait_for_function('(s)=>/cho phép|cấp quyền/.test(document.querySelector(s).textContent)',arg=status)
                await page.locator('#cinema-playpause' if cinema else '#voice-pause').click()
                await page.wait_for_function('(s)=>document.querySelector(s).textContent.includes("Đang")',arg=status)
                await page.close()
            print('PASS blocked play(): explicit resume recovers both players')

            if skip_decode:
                await browser.close()
                return
            # Decode the actual exported files and inspect PCM samples. A nonempty
            # MP3 or successful play() alone cannot prove that a file has sound.
            page = await browser.new_page()
            await page.goto(url)
            ids = [s['id'] for s in json.loads((ROOT / 'content/story_manifest.v1.json').read_text(encoding='utf-8'))['scenes']]
            paths=await page.evaluate('(ids)=>ids.map(id=>({id,url:document.getElementById(id).dataset.audioSrc||"assets/voice/"+id+".mp3"}))',ids)
            decoded = await page.evaluate("""async(paths)=>{
              const ctx=new AudioContext();const result=[];
              for(const {id,url} of paths){
                const response=await fetch(url);
                if(!response.ok)throw new Error(id+': HTTP '+response.status);
                const buffer=await ctx.decodeAudioData(await response.arrayBuffer());
                const samples=buffer.getChannelData(0);let power=0;
                for(let i=0;i<samples.length;i++)power+=samples[i]*samples[i];
                const rms=Math.sqrt(power/samples.length);
                if(buffer.duration<2||rms<.001)throw new Error(id+': silent/short recording');
                result.push({id,url,duration:buffer.duration,rms});
              }
              await ctx.close();return result;
            }""", paths)
            (ROOT / 'tests/audio_decode_report.json').write_text(json.dumps(decoded, indent=2) + '\n', encoding='utf-8')
            print(f'PASS {len(decoded)} real MP3s: decode, duration, nonzero speech samples')
            await browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-full-decode', action='store_true', help='Only check playback while remaining scenes are being generated')
    asyncio.run(main(parser.parse_args().skip_full_decode))
