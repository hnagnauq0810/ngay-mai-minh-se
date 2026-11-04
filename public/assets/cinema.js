/* Cinematic continuous playback v1.3: archival imagery from Wikimedia Commons; optional pre-rendered local MP3s. */
(() => {
  'use strict';
  if (window.__NMMS_CINEMA__) return;
  window.__NMMS_CINEMA__ = true;
  const scenes = [...document.querySelectorAll('.story-scene')].map((el, index) => ({
    id: el.id, index,
    title: el.querySelector('.scene-title')?.textContent.trim() || 'Câu chuyện',
    period: el.querySelector('.scene-period')?.textContent.trim() || '',
    narration: el.querySelector('.narration')?.textContent.trim() || '',
    lines: [...el.querySelectorAll('.dialogue-line')].map(d => ({
      speaker: d.querySelector('.speaker')?.textContent.trim() || '',
      text: d.querySelector('p')?.textContent.trim() || ''
    })),
    act: el.classList.contains('act-one') ? 'act-one' : el.classList.contains('act-two') ? 'act-two' : el.classList.contains('act-three') ? 'act-three' : el.classList.contains('epilogue') ? 'epilogue' : 'prologue',
    chapter: el.dataset.chapter || '', mediaSrc:el.dataset.mediaSrc||'', mediaCaption:el.dataset.mediaCaption||'', mediaNote:el.dataset.mediaNote||'', mediaCredit:el.dataset.mediaCredit||'', mediaSource:el.dataset.mediaSource||'',
    shots:JSON.parse(el.querySelector('[data-shots]')?.dataset.shots||'[]'),timing:JSON.parse(el.dataset.audioTiming||'null'),audioSrc:el.dataset.audioSrc||'',audioProfile:el.dataset.audioProfile||'',el
  }));
  if (!scenes.length) return;
  const srcBase = document.currentScript?.src || (/^(https?:|file:)/.test(document.baseURI) ? new URL('assets/cinema.js',document.baseURI).href : 'https://offline.example/assets/cinema.js');
  const assetRoot = new URL('./voice/', srcBase);
  const voiceAsset = (id) => new URL(encodeURIComponent(id)+'.mp3', assetRoot).href;
  const sceneVoiceAsset=(s)=>s.audioSrc?new URL('../'+s.audioSrc,srcBase).href:voiceAsset(s.id);
  const storage = {
    get(k){try{return localStorage.getItem(k)}catch{return null}},
    set(k,v){try{localStorage.setItem(k,v)}catch{}}
  };
  const escapeHtml = (s) => String(s||'').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const markup = `<div class="cinema-layer" id="cinema-layer" hidden aria-label="Phim lịch sử tự động" role="dialog" aria-modal="true">
    <div class="cinema-canvas" id="cinema-canvas" data-act="prologue">
      <div class="cinema-media-backdrop" id="cinema-media-backdrop" aria-hidden="true"><img id="cinema-media-image" alt="" decoding="async" referrerpolicy="no-referrer" /><div class="cinema-media-vignette"></div></div>
      <div class="cinema-atmosphere" aria-hidden="true"><div class="cinema-moon"></div><div class="cinema-land"></div><div class="cinema-texture"></div></div>
      <div class="cinema-top"><span class="cinema-logo">✳ NGÀY MAI, MÌNH SẼ…</span><span class="cinema-count" id="cinema-count">CẢNH 01 / 55</span></div>
      <div class="cinema-stage" aria-live="off">
        <div class="cinema-period" id="cinema-period">1930—2026</div>
        <div class="cinema-story-title" id="cinema-title">Một câu chuyện về những ngày mai</div>
        <div class="cinema-narrative" id="cinema-narrative"></div>
        <div class="cinema-caption" id="cinema-caption" aria-live="polite"></div>
        <div class="cinema-role" id="cinema-role"></div>
        <div class="cinema-visual-navigation" id="cinema-visual-navigation" aria-label="Chọn tư liệu trong cảnh"></div>
        <div class="cinema-visual-label" id="cinema-visual-label"></div>
      </div>
      <div class="cinema-source-line" id="cinema-source-line"><span id="cinema-source-text"></span><a id="cinema-source-link" target="_blank" rel="noopener noreferrer">Tư liệu & giấy phép ↗</a><details class="cinema-media-note" id="cinema-media-note"><summary>Bối cảnh tư liệu</summary><p id="cinema-media-note-text"></p></details></div>
      <div class="cinema-bottom"><div class="cinema-track" id="cinema-track" aria-label="Tiến độ cảnh"><span id="cinema-track-fill"></span></div>
        <div class="cinema-controls">
          <button type="button" class="cinema-control" id="cinema-prev" aria-label="Cảnh trước">❮</button>
          <button type="button" class="cinema-control cinema-main" id="cinema-playpause" aria-label="Phát">▶ Phát</button>
          <button type="button" class="cinema-control" id="cinema-next" aria-label="Cảnh tiếp">❯</button>
          <button type="button" class="cinema-control cinema-stop" id="cinema-stop">■ Dừng</button>
          <span class="cinema-spacer"></span>
          <label class="cinema-voice-label">Nguồn giọng <select id="cinema-voice-choice" aria-label="Chọn nguồn giọng"><option value="audio">MP3 tiếng Việt tự nhiên</option><option value="browser">Giọng Việt của máy</option></select></label>
          <button type="button" class="cinema-control cinema-small" id="cinema-loop" aria-pressed="true">Lặp: Bật</button>
          <button type="button" class="cinema-control cinema-small" id="cinema-captions" aria-pressed="true">Phụ đề: Bật</button>
          <button type="button" class="cinema-control cinema-small" id="cinema-fullscreen">⛶ Toàn màn hình</button>
          <button type="button" class="cinema-control cinema-small" id="cinema-close">✕ Thoát</button>
        </div>
        <div class="cinema-feedback" id="cinema-feedback" role="status">Sẵn sàng phát toàn bộ 55 cảnh. Giọng Việt tự nhiên được dùng khi đã tạo file MP3.</div>
      </div>
    </div>
  </div>`;
  document.body.insertAdjacentHTML('beforeend',markup);
  const $=(id)=>document.getElementById(id);
  const ui={layer:$('cinema-layer'),canvas:$('cinema-canvas'),title:$('cinema-title'),period:$('cinema-period'),count:$('cinema-count'),narrative:$('cinema-narrative'),caption:$('cinema-caption'),role:$('cinema-role'),fill:$('cinema-track-fill'),play:$('cinema-playpause'),prev:$('cinema-prev'),next:$('cinema-next'),status:$('cinema-feedback'),voice:$('cinema-voice-choice'),captions:$('cinema-captions'),media:$('cinema-media-image'),backdrop:$('cinema-media-backdrop'),sourceText:$('cinema-source-text'),sourceLink:$('cinema-source-link')};
  let loopOn=true,index=0,state='idle',audio=null,utterance=null,speechParts=[],speechPosition=0,activeToken=0,rafId=0,captionTimer=0,captionsOn=true;
  let sceneStartTime=0,elapsedPause=0,lastFocus=null,loadingTimeout=0;
  let viVoices=[];
  const visuals=window.NMMSMedia?new NMMSMedia.VisualPlayer(ui.backdrop,{image:ui.media,onChange:shot=>{
    const kind=shot.type==='video'?'PHIM':shot.ai_generated?'MINH HỌA AI':shot.kind==='illustration'?'ĐỒ HỌA':shot.kind==='archive'?'ẢNH LƯU TRỮ':'ẢNH MINH HỌA';
    ui.sourceText.textContent=shot.caption+' · '+kind+' · '+shot.date;
    ui.sourceText.title=[shot.author,shot.license,shot.note].join(' · ');
    ui.sourceLink.hidden=!shot.source;ui.sourceLink.href=shot.source||'#';
    $('cinema-media-note').hidden=!shot.note;$('cinema-media-note').open=false;$('cinema-media-note-text').textContent=shot.note;
    $('cinema-visual-label').textContent=shot.label;
  }}):null;
  if(visuals)visuals.navigation($('cinema-visual-navigation'));
  document.addEventListener('nmms:shots-updated',event=>{
    const scene=scenes.find(s=>s.id===event.detail.id);if(!scene)return;
    scene.shots=event.detail.shots;
    if(scenes[index]===scene)visuals?.replaceShots(scene.shots);
  });
  const setting=storage.get('nmms_cinema_voice');
  ui.voice.value=(setting==='browser')?'browser':'audio';

  function loadVoices(){
    if(!('speechSynthesis' in window)) return;
    viVoices=speechSynthesis.getVoices().filter(v=>/^vi(?:-|_)/i.test(v.lang)||/^Vietnamese|Tiếng Việt/i.test(v.name));
    viVoices.sort((a,b)=>Number(b.localService)-Number(a.localService));
  }
  loadVoices();
  if('speechSynthesis' in window) speechSynthesis.addEventListener?.('voiceschanged',loadVoices);
  function open(){
    lastFocus=document.activeElement;
    document.body.classList.add('cinema-open');
    ui.layer.hidden=false;
    renderScene();
    ui.play.focus();
  }
  function close(){stop();ui.layer.hidden=true;document.body.classList.remove('cinema-open');if(document.fullscreenElement)document.exitFullscreen?.().catch(()=>{});lastFocus?.focus?.();}
  function setStatus(text){ui.status.textContent=text;}
  function setPlaybackState(next){state=next;
    visuals?.setPlaying(next==='playing');
    ui.play.textContent= next==='playing'?'❚❚ Tạm dừng':next==='paused'?'▶ Tiếp tục':'▶ Phát';
    ui.play.setAttribute('aria-label',next==='playing'?'Tạm dừng':next==='paused'?'Tiếp tục':'Phát');
    ui.canvas.classList.toggle('is-playing',next==='playing');
    ui.canvas.classList.toggle('is-paused',next==='paused');
  }
  function setCaption(text,speaker=''){
    if(!captionsOn){ui.caption.textContent='';ui.role.textContent='';return;}
    ui.caption.textContent=text;
    ui.role.textContent=speaker;
  }
  function splitChunks(text){
    // Split on sentence boundaries so Chromium does not lose long TTS passages.
    const raw=(text||'').match(/[^.!?…]+(?:[.!?…]+|$)/g)||[];
    const chunks=[];
    raw.forEach(p=>{
      const v=p.trim();if(!v)return;
      if(v.length<210){chunks.push(v);return;}
      const words=v.split(/\s+/);let block='';
      words.forEach(w=>{if((block+' '+w).length>170&&block){chunks.push(block);block=w;}else block+=(block?' ':'')+w;});
      if(block)chunks.push(block);
    });
    return chunks;
  }
  function getSegments(s){
    const seg=[{who:'NGƯỜI DẪN',text:s.title}];
    splitChunks(s.narration).forEach(text=>seg.push({who:'NGƯỜI DẪN',text}));
    s.lines.forEach(line=>splitChunks(line.text).forEach(text=>seg.push({who:line.speaker||'NHÂN VẬT',text})));
    return seg;
  }
  function renderScene(){
    const s=scenes[index];if(!s)return;
    ui.canvas.dataset.act=s.act;
    // Show accurate, captioned archival/contemporary image for every scene.
    // URL points to Wikimedia Commons unless local media have been installed.
    if(visuals&&s.shots.length){
      ui.canvas.classList.add('has-storyboard');visuals.setShots(s.shots);
    }else if(s.mediaSrc){
      ui.backdrop.classList.remove('is-ready');
      ui.media.onerror=()=>{ ui.backdrop.classList.remove('is-ready'); ui.backdrop.classList.add('is-error'); };
      ui.media.onload=()=>{ ui.backdrop.classList.add('is-ready'); ui.backdrop.classList.remove('is-error'); };
      ui.media.src=s.mediaSrc;
      ui.sourceText.textContent=s.mediaCaption + ' · ' + s.mediaCredit;
      ui.sourceText.title=s.mediaNote;
      $('cinema-media-note').hidden=!s.mediaNote;
      $('cinema-media-note').open=false;
      $('cinema-media-note-text').textContent=s.mediaNote;
      ui.sourceLink.href=s.mediaSource; ui.sourceLink.hidden=false;
    }else{ui.media.removeAttribute('src');ui.backdrop.classList.remove('is-ready');ui.sourceText.textContent='';ui.sourceLink.hidden=true;$('cinema-media-note').hidden=true;}
    ui.period.textContent=s.period;
    ui.count.textContent=`CẢNH ${String(index+1).padStart(2,'0')} / ${scenes.length}`;
    ui.title.textContent=s.title;
    ui.narrative.textContent=s.chapter==='07'||s.chapter==='08'?'HAI NỬA CỦA MỘT BẦU TRỜI':s.act==='act-one'?'HỒI I · TÌM ĐƯỜNG ĐỘC LẬP':s.act==='act-two'?'HỒI II · GIỮ GÌN VÀ THỐNG NHẤT':s.act==='act-three'?'HỒI III · XÂY DỰNG VÀ ĐỔI MỚI':'MỘT HÀNH TRÌNH LỊCH SỬ';
    ui.canvas.classList.toggle('is-split',s.chapter==='07'||s.chapter==='08');
    ui.fill.style.width='0%';
    ui.prev.disabled=index===0;
    ui.next.disabled=index===scenes.length-1;
    const first=splitChunks(s.narration)[0] || s.title;
    setCaption(first);
  }
  function cancelTimers(){
    activeToken++;
    clearTimeout(loadingTimeout);clearTimeout(captionTimer);
    if(rafId)cancelAnimationFrame(rafId);
    rafId=0;
    if(audio){audio.pause();audio.removeAttribute('src');audio.load();audio=null;}
    visuals?.pause();
    if('speechSynthesis' in window) speechSynthesis.cancel();
    utterance=null; speechParts=[]; speechPosition=0;
  }
  function stop(){cancelTimers();setPlaybackState('idle');renderScene();setStatus('Đã dừng. Bấm Phát để bắt đầu lại từ cảnh hiện tại.');}
  function move(to,doPlay=true){
    if(to<0||to>=scenes.length){
      if(to>=scenes.length && loopOn){to=0;}
      else {if(to>=scenes.length){stop();setStatus('Đã phát hết câu chuyện. Bấm Phát để xem lại.');}return;}
    }
    cancelTimers();index=to;renderScene();
    if(doPlay)startCurrent();else setPlaybackState('idle');
  }
  function next(){move(index+1,true);}
  function pause(){
    if(state!=='playing')return;
    clearTimeout(loadingTimeout);
    setPlaybackState('paused');
    if(audio){audio.pause();}
    else if(utterance && 'speechSynthesis' in window){speechSynthesis.pause();}
    setStatus('Đã tạm dừng. Nhấn Tiếp tục để phát từ vị trí này.');
  }
  function resume(){
    if(state!=='paused')return;
    setPlaybackState('playing');
    if(audio){const token=activeToken;audio.play().then(()=>{if(token===activeToken)progressLoop();}).catch(()=>{if(token!==activeToken)return;pause();setStatus('Trình duyệt chặn phát âm thanh. Bấm Tiếp tục thêm lần nữa.');});}
    else if(utterance && 'speechSynthesis' in window){speechSynthesis.resume();progressLoop();}
    else startCurrent();
    setStatus('Đang tiếp tục câu chuyện.');
  }
  function timerCaptions(duration,segments){
    if(!segments.length)return;
    const weights=segments.map(s=>Math.max(15,s.text.length));
    const total=weights.reduce((a,b)=>a+b,0);let intervals=[];let time=0;
    const recorded=scenes[index].timing?.segments;
    if(recorded?.length){intervals=recorded.map((p,i)=>({until:recorded[i+1]?.start||duration,seg:{text:p.text,who:p.speaker}}));}
    else weights.forEach((w,i)=>{intervals.push({until:(time+=(w/total)*duration),seg:segments[i]});});
    function draw(){
      if(state==='idle')return;
      if(state==='playing' && audio && Number.isFinite(audio.duration)){
        const now=audio.currentTime;
        visuals?.sync(now,audio.duration);
        const selected=intervals.find(q=>now<q.until)||intervals.at(-1);
        if(selected)setCaption(selected.seg.text,selected.seg.who);
      }
      captionTimer=setTimeout(draw,250);
    }
    draw();
  }
  function progressLoop(){
    if(state!=='playing')return;
    if(audio && Number.isFinite(audio.duration)&&audio.duration>0){ui.fill.style.width=(audio.currentTime/audio.duration*100)+'%';}
    else if(utterance){ui.fill.style.width=Math.min(98,(speechPosition/Math.max(1,speechParts.length))*100)+'%';}
    rafId=requestAnimationFrame(progressLoop);
  }
  async function speechFallback(token){
    if(token!==activeToken)return;
    loadVoices();
    if('speechSynthesis' in window && !viVoices.length){
      await new Promise(resolve=>{
        const ready=()=>{loadVoices();if(viVoices.length){clearTimeout(timer);speechSynthesis.removeEventListener('voiceschanged',ready);resolve();}};
        const timer=setTimeout(()=>{speechSynthesis.removeEventListener('voiceschanged',ready);resolve();},1500);
        speechSynthesis.addEventListener('voiceschanged',ready);
      });
      if(token!==activeToken)return;
      loadVoices();
    }
    if(!('speechSynthesis' in window)||!window.SpeechSynthesisUtterance||viVoices.length===0){
      setPlaybackState('idle');
      setStatus('Không tải được âm thanh và thiết bị chưa có giọng Việt. Kiểm tra kết nối rồi bấm Phát để thử lại.');
      return;
    }
    if(state==='paused'){setPlaybackState('idle');setStatus('Giọng tiếng Việt đã sẵn sàng. Bấm Phát để bắt đầu cảnh.');return;}
    setStatus(`Đang phát bằng giọng tiếng Việt của thiết bị (${viVoices[0].name}).`);
    const scene=scenes[index]; speechParts=getSegments(scene);speechPosition=0;
    function speakPart(){
      if(token!==activeToken||state==='idle')return;
      if(speechPosition>=speechParts.length){move(index+1,true);return;}
      if(visuals){const total=speechParts.reduce((sum,p)=>sum+p.text.length,0);const elapsed=speechParts.slice(0,speechPosition).reduce((sum,p)=>sum+p.text.length,0);visuals.sync(elapsed/Math.max(1,total),1,true);}
      const p=speechParts[speechPosition];setCaption(p.text,p.who);
      const ut=new SpeechSynthesisUtterance(p.text);ut.lang='vi-VN';ut.voice=viVoices[0];ut.rate=.93;ut.pitch=1;
      utterance=ut;
      ut.onend=()=>{if(token!==activeToken)return;speechPosition++;speakPart();};
      ut.onerror=(e)=>{if(token!==activeToken)return;setPlaybackState('idle');setStatus('Giọng đọc trình duyệt gặp lỗi ('+(e.error||'unknown')+'). Hãy tạo MP3 tiếng Việt để phát ổn định.');};
      speechSynthesis.speak(ut);
    }
    speakPart();progressLoop();
  }
  function startCurrent(){
    cancelTimers();
    renderScene();setPlaybackState('playing');
    const token=activeToken;
    const scene=scenes[index];
    if(ui.voice.value==='browser'){speechFallback(token);return;}
    setStatus('Đang tải giọng đọc tiếng Việt…');
    const element=new Audio();audio=element;element.preload='auto';
    let fallingBack=false;
    function fallback(){
      if(token!==activeToken||fallingBack)return;
      fallingBack=true;clearTimeout(loadingTimeout);
      element.pause();element.removeAttribute('src');element.load();audio=null;
      speechFallback(token);
    }
    element.src=sceneVoiceAsset(scene);
    element.addEventListener('loadedmetadata',()=>{
      if(token!==activeToken)return;
      timerCaptions(element.duration,getSegments(scene));
    },{once:true});
    element.addEventListener('playing',()=>{
      if(token!==activeToken||fallingBack)return;
      clearTimeout(loadingTimeout);
      if(state==='paused'){element.pause();return;}
      setStatus('Đang kể: '+(scene.audioProfile||'Giọng tiếng Việt')+'.');
    });
    element.addEventListener('ended',()=>{if(token===activeToken)move(index+1,true);},{once:true});
    element.addEventListener('error',fallback,{once:true});
    loadingTimeout=setTimeout(()=>{
      if(token!==activeToken||fallingBack)return;
      cancelTimers();setPlaybackState('idle');setStatus('Tải âm thanh quá lâu. Kiểm tra kết nối rồi bấm Phát để thử lại.');
    },15000);
    element.play().then(()=>{if(token===activeToken&&!fallingBack){clearTimeout(loadingTimeout);if(state==='paused')element.pause();else progressLoop();}}).catch(err=>{
      if(token!==activeToken||fallingBack||state==='paused'&&err.name==='AbortError')return;
      clearTimeout(loadingTimeout);
      if(err.name!=='NotAllowedError'){fallback();return;}
      setPlaybackState('paused');
      setStatus('Trình duyệt chặn phát âm thanh. Bấm Tiếp tục để cấp quyền phát. ('+(err.name||'')+')');
    });
  }
  function togglePlay(){
    if(state==='playing')pause();
    else if(state==='paused')resume();
    else startCurrent();
  }
  function startFromDocument(){
    // For explicit "Xem phim" button, always begin at prologue; playback is user-initiated.
    document.getElementById('voice-stop')?.click();
    window.NMMSMedia?.pauseReaders();
    index=0;open();startCurrent();
  }
  const topButton=document.createElement('button');topButton.type='button';topButton.className='control-btn cinema-open-btn';topButton.textContent='▶ Xem phim liên tục';
  document.querySelector('.header-actions')?.insertBefore(topButton,document.querySelector('#menu-open'));
  topButton.addEventListener('click',startFromDocument);
  const heroButton=document.createElement('button');heroButton.type='button';heroButton.className='primary-cta cinema-hero-btn';heroButton.textContent='▶ Xem như một bộ phim';
  document.querySelector('.hero-ctas')?.prepend(heroButton);
  heroButton.addEventListener('click',startFromDocument);
  ui.play.addEventListener('click',togglePlay);
  ui.prev.addEventListener('click',()=>move(index-1,state==='playing'));
  ui.next.addEventListener('click',()=>move(index+1,state==='playing'));
  $('cinema-stop').addEventListener('click',stop);
  $('cinema-close').addEventListener('click',close);
  ui.voice.addEventListener('change',()=>{storage.set('nmms_cinema_voice',ui.voice.value);if(state==='playing')startCurrent();else if(state==='paused'){cancelTimers();setPlaybackState('idle');setStatus('Đã đổi nguồn giọng. Bấm Phát để bắt đầu cảnh bằng nguồn mới.');}});
  $('cinema-loop').addEventListener('click',()=>{loopOn=!loopOn;$('cinema-loop').textContent='Lặp: '+(loopOn?'Bật':'Tắt');$('cinema-loop').setAttribute('aria-pressed',String(loopOn));});
  ui.captions.addEventListener('click',()=>{captionsOn=!captionsOn;ui.captions.textContent='Phụ đề: '+(captionsOn?'Bật':'Tắt');ui.captions.setAttribute('aria-pressed',String(captionsOn));if(captionsOn&&state==='idle')renderScene();else if(!captionsOn)setCaption('');});
  $('cinema-fullscreen').addEventListener('click',()=>{if(document.fullscreenElement)document.exitFullscreen?.();else ui.layer.requestFullscreen?.().catch(()=>setStatus('Trình duyệt không cho phép mở toàn màn hình.'));});
  document.addEventListener('keydown',(e)=>{
    if(ui.layer.hidden)return;
    if(e.key==='Escape'){close();return;}
    if(e.target instanceof HTMLElement && /^(INPUT|TEXTAREA|SELECT|BUTTON|SUMMARY|A)$/.test(e.target.tagName))return;
    if(e.code==='Space'){e.preventDefault();togglePlay();}
    if(e.key==='ArrowRight'){e.preventDefault();move(index+1,state==='playing');}
    if(e.key==='ArrowLeft'){e.preventDefault();move(index-1,state==='playing');}
  });
  window.NMMS_CINEMA_DEBUG={getState:()=>state,getIndex:()=>index,getVoice:()=>ui.voice.value,getLoop:()=>loopOn,getVisual:()=>visuals?.current,getShotCount:()=>visuals?.shots.length,play:togglePlay,move};
})();
