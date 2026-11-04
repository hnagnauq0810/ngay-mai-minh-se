/* Ngày mai, mình sẽ… — Client enhancement layer.
   Source: generated accessible HTML, not runtime-scraped historical information.
   No analytics, cookies, third-party APIs or server writes. */
(() => {
  'use strict';
  if (document.documentElement.dataset.nmmsInitialized === 'yes') return;
  document.documentElement.dataset.nmmsInitialized = 'yes';
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const storage = {
    get(key) { try { return localStorage.getItem(key); } catch { return null; } },
    set(key,value) { try { localStorage.setItem(key,value); } catch {} },
    del(key) { try { localStorage.removeItem(key); } catch {} }
  };
  // If Commons cannot be reached, preserve source attribution and show an explicit fallback.
  $$('.scene-archive-media img').forEach(img => {
    img.addEventListener('error',()=>{
      if(window.NMMSMedia&&img.closest('[data-shots]'))return;
      img.hidden=true;const message=img.closest('figure')?.querySelector('.media-not-loaded');
      if(message)message.hidden=false;
    });
  });
  const sceneEls = $$('.story-scene');
  const sceneById = new Map(sceneEls.map(el => [el.id, el]));
  const progress = $('#read-progress'), progressFill=$('#read-progress-fill');
  const period=$('#current-period');
  const drawer=$('#chapter-drawer'), backdrop=$('#drawer-backdrop');
  const openBtn=$('#menu-open'), closeBtn=$('#menu-close');
  const readingBtn=$('#reading-toggle'), drawerReadingBtn=$('#drawer-reading-toggle');
  let openMenu=false, lastFocused=null, activeScene=null, progressQueued=false, autoSpeech=null;

  function setMenu(open){
    openMenu = !!open;
    drawer.classList.toggle('open',openMenu);
    drawer.setAttribute('aria-hidden', String(!openMenu));
    if(openMenu){
      lastFocused=document.activeElement;
      drawer.removeAttribute('inert');
      backdrop.hidden=false;
      document.body.style.overflow='hidden';
      openBtn.setAttribute('aria-expanded','true');
      closeBtn.focus();
    } else {
      drawer.setAttribute('inert','');
      backdrop.hidden=true;
      document.body.style.overflow='';
      openBtn.setAttribute('aria-expanded','false');
      if(lastFocused && document.contains(lastFocused))lastFocused.focus();
    }
  }
  openBtn?.addEventListener('click',()=>setMenu(true));
  closeBtn?.addEventListener('click',()=>setMenu(false));
  backdrop?.addEventListener('click',()=>setMenu(false));
  $$('.chapter-link,.drawer-footer-link').forEach(a=>a.addEventListener('click',()=>setMenu(false)));
  document.addEventListener('keydown',(e)=>{
    if(e.key==='Escape') {if(openMenu)setMenu(false);else stopSpeech();}
    if(openMenu && e.key==='Tab'){
      const elements=$$('a[href],button:not([disabled]),[tabindex]:not([tabindex="-1"])').filter(el=>drawer.contains(el));
      if(elements.length){const first=elements[0],last=elements[elements.length-1];
        if(e.shiftKey && document.activeElement===first){last.focus();e.preventDefault()}
        if(!e.shiftKey && document.activeElement===last){first.focus();e.preventDefault()}
      }
    }
  });
  $('#open-overview')?.addEventListener('click',()=>$('#overview')?.scrollIntoView({behavior:document.body.classList.contains('reduce-motion')?'auto':'smooth'}));

  const savedRead=storage.get('nmms_read_mode')==='1';
  function setReading(enabled){
    document.body.classList.toggle('reading-mode',enabled);
    readingBtn?.setAttribute('aria-pressed',String(enabled));
    drawerReadingBtn?.setAttribute('aria-pressed',String(enabled));
    if(readingBtn)readingBtn.textContent=enabled?'Chế độ điện ảnh':'Chế độ đọc';
    if(drawerReadingBtn)drawerReadingBtn.textContent=enabled?'Trở về chế độ điện ảnh':'Chế độ đọc dễ nhìn';
    storage.set('nmms_read_mode',enabled?'1':'0');
  }
  setReading(savedRead);
  readingBtn?.addEventListener('click',()=>setReading(!document.body.classList.contains('reading-mode')));
  drawerReadingBtn?.addEventListener('click',()=>setReading(!document.body.classList.contains('reading-mode')));
  const prefersReduced=matchMedia('(prefers-reduced-motion: reduce)');
  if(prefersReduced.matches) document.body.classList.add('reduce-motion');
  if(prefersReduced.addEventListener) prefersReduced.addEventListener('change',(e)=>document.body.classList.toggle('reduce-motion',e.matches));

  // CSS-reveal is progressive enhancement; failure leaves text readable.
  if ('IntersectionObserver' in window) {
    const revealObs=new IntersectionObserver(entries=>{
      entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('has-revealed');revealObs.unobserve(e.target)}});
    },{rootMargin:'0px 0px -14% 0px',threshold:0.05});
    sceneEls.forEach(el=>revealObs.observe(el));

    const sceneObs=new IntersectionObserver(entries=>{
      const visible=entries.filter(x=>x.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio);
      if(visible.length){setActive(visible[0].target);}
    },{rootMargin:'-23% 0px -44% 0px',threshold:[0,.1,.4,.7]});
    sceneEls.forEach(el=>sceneObs.observe(el));
  } else {sceneEls.forEach(el=>el.classList.add('has-revealed'));}
  function setActive(el){
    if(activeScene===el)return;
    activeScene?.classList.remove('is-current');
    activeScene=el;activeScene.classList.add('is-current');
    period.textContent=el.querySelector('.scene-period')?.textContent || '1930—2026';
    storage.set('nmms_last_scene',el.id);
    $$('.chapter-link').forEach(link=>{
      const isCurrent=link.dataset.chapterLink===el.dataset.chapter;
      if(isCurrent)link.setAttribute('aria-current','true');
      else link.removeAttribute('aria-current');
    });
  }
  function updateScroll(){
    progressQueued=false;
    const max=Math.max(document.documentElement.scrollHeight-innerHeight,1);
    const value=Math.max(0,Math.min(100,Math.round(scrollY/max*100)));
    progressFill.style.width=value+'%';
    progress?.setAttribute('aria-valuenow',String(value));
  }
  addEventListener('scroll',()=>{if(!progressQueued){progressQueued=true;requestAnimationFrame(updateScroll)}},{passive:true});
  addEventListener('resize',updateScroll,{passive:true});
  updateScroll();

  async function copyText(text){
    if(!text)return false;
    try{await navigator.clipboard.writeText(text);return true;}catch{
      const temp=document.createElement('textarea');temp.value=text;temp.style.position='fixed';temp.style.left='-9999px';document.body.append(temp);temp.select();
      let ok=false;try{ok=document.execCommand('copy')}catch{}temp.remove();return ok;
    }
  }
  function flashButton(btn,message){
    const before=btn.textContent;btn.textContent=message;
    setTimeout(()=>{if(document.contains(btn))btn.textContent=before},1700);
  }
  $$('.copy-scene').forEach(btn=>btn.addEventListener('click',async()=>{
    const el=sceneById.get(btn.dataset.copyScene);if(!el)return;
    const title=el.querySelector('.scene-title')?.textContent||'';
    const text=el.querySelector('.narration')?.textContent||'';
    const ok=await copyText(title+'\n\n'+text.trim()+'\n\nBản thảo kịch bản “Ngày mai, mình sẽ…”');
    flashButton(btn,ok?'Đã sao chép':'Không thể sao chép');
  }));

  // Normalize all text to NFC to avoid broken Vietnamese combining marks on some renderers.
  if (window.NodeFilter && document.createTreeWalker) {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let textNode;
    while ((textNode = walker.nextNode())) {
      if (textNode.textContent) textNode.textContent = textNode.textContent.normalize('NFC');
    }
  }

  // Prefer bundled Vietnamese MP3s; use an installed Vietnamese voice only as fallback.
  window.NMMSMedia?.mountReaders();
  const dock=$('#voice-dock'),voiceStatus=$('#voice-status'),pauseBtn=$('#voice-pause');
  let speaking=false,paused=false,autoNarrating=false,autoIndex=-1,autoStartTimer=0,autoScrollFrame=0,autoScrollState=null;
  let voiceAudio=null, speechToken=0, voiceLoadTimer=0, readerVisual=null;
  const scriptSource=document.currentScript?.src || new URL('assets/site.js', /^(https?:|file:)/.test(document.baseURI)?document.baseURI:'https://offline.example/').href;
  const voiceRoot=new URL('./voice/',scriptSource);

  function enhanceVoiceControls(){
    const headerActions=$('.header-actions');
    if(headerActions && !$('#auto-narrate-toggle')){
      const autoBtn=document.createElement('button');
      autoBtn.type='button';autoBtn.id='auto-narrate-toggle';
      autoBtn.className='control-btn auto-play-btn';
      autoBtn.setAttribute('aria-pressed','false');
      autoBtn.textContent='Tự kể';
      headerActions.insertBefore(autoBtn, $('#menu-open'));
    }
    if(dock && !dock.querySelector('.voice-mode')){
      const badge=document.createElement('span');
      badge.className='voice-mode';badge.id='voice-mode';badge.textContent='Nghe từng cảnh';
      dock.prepend(badge);
      const existing=dock.querySelector('div');
      if(existing) existing.classList.add('voice-actions');
    }
  }
  enhanceVoiceControls();
  const autoBtn=$('#auto-narrate-toggle');
  const voiceMode=$('#voice-mode');

  function updateAutoUi(){
    if(!autoBtn)return;
    autoBtn.classList.toggle('is-active',autoNarrating);
    autoBtn.setAttribute('aria-pressed',String(autoNarrating));
    autoBtn.textContent=autoNarrating?'Dừng tự kể':'Tự kể';
    if(voiceMode) voiceMode.textContent=autoNarrating?'Tự kể & tự cuộn':'Nghe từng cảnh';
  }
  function stopSceneAutoscroll(){
    if(autoScrollFrame) cancelAnimationFrame(autoScrollFrame);
    autoScrollFrame=0; autoScrollState=null;
  }
  function scheduleAutoScroll(el, durationMs){
    stopSceneAutoscroll();
    if(!autoNarrating || !el) return;
    const top=window.scrollY;
    const maxY=Math.max(document.documentElement.scrollHeight - window.innerHeight, 0);
    const sceneTop=el.getBoundingClientRect().top + window.scrollY;
    const target=Math.min(maxY, Math.max(top, sceneTop + el.offsetHeight - window.innerHeight + 110));
    if(target-top < 36) return;
    const duration=Math.max(4000, Math.min(durationMs, 30000));
    const start=performance.now()+420;
    autoScrollState={startY:top,targetY:target,duration,start};
    const step=(now)=>{
      if(!autoScrollState || paused || !autoNarrating) return;
      const elapsed=Math.max(0, now-autoScrollState.start);
      const ratio=Math.min(1, elapsed/autoScrollState.duration);
      const eased=ratio<0.5 ? 2*ratio*ratio : 1-Math.pow(-2*ratio+2,2)/2;
      window.scrollTo(0, autoScrollState.startY + (autoScrollState.targetY-autoScrollState.startY)*eased);
      if(ratio<1) autoScrollFrame=requestAnimationFrame(step);
      else stopSceneAutoscroll();
    };
    autoScrollFrame=requestAnimationFrame(step);
  }
  function clearAutoTimers(){
    if(autoStartTimer) clearTimeout(autoStartTimer);
    autoStartTimer=0;
    stopSceneAutoscroll();
  }
  function hideDock(){dock.hidden=true;speaking=false;paused=false;autoSpeech=null;pauseBtn.textContent='Tạm dừng';}
  function stopSpeech(){
    clearAutoTimers();
    autoNarrating=false; updateAutoUi();
    cancelVoice();
    hideDock();
  }
  function cancelVoice(){
    speechToken++;
    clearTimeout(voiceLoadTimer);
    readerVisual?.pause();readerVisual=null;
    autoSpeech=null;
    if(voiceAudio){voiceAudio.pause();voiceAudio.removeAttribute('src');voiceAudio.load();voiceAudio=null;}
    if ('speechSynthesis' in window) speechSynthesis.cancel();
  }
  function getSceneText(el){
    const title=el.querySelector('.scene-title')?.textContent?.trim()||'';
    const text=el.querySelector('.narration')?.textContent?.trim()||'';
    const dialogue=[...el.querySelectorAll('.dialogue-line')].map(line=>(line.querySelector('.speaker')?.textContent||'Nhân vật')+' nói: '+(line.querySelector('p')?.textContent||'')).join(' ');
    return (title? title+'. ': '') + text + ' ' + dialogue;
  }
  function estimatedDuration(text, rate){
    const words=(text.match(/\S+/g)||[]).length;
    return Math.max(5000, Math.round(words*380/Math.max(rate||1,.5)));
  }
  function speakElement(el, {auto=false}={}){
    if(!el) return;
    const text=getSceneText(el); if(!text) return;
    clearAutoTimers();
    cancelVoice();
    const token=speechToken;
    readerVisual=window.NMMSMedia?.readers.get(el.id)||null;readerVisual?.reset();
    if(readerVisual&&!auto)el.querySelector('.scene-archive-media')?.scrollIntoView({block:'start',behavior:document.body.classList.contains('reduce-motion')?'auto':'smooth'});
    dock.hidden=false; speaking=true; paused=false;
    voiceStatus.textContent='Đang tải giọng đọc tiếng Việt…';
    pauseBtn.textContent='Tạm dừng';
    const started=()=>{
      if(token!==speechToken)return;
      clearTimeout(voiceLoadTimer);
      if(paused){voiceAudio?.pause();return;}
      readerVisual?.setPlaying(true);
      speaking=true; paused=false; dock.hidden=false;
      voiceStatus.textContent=(auto?'Tự kể: ':'Đang đọc: ')+(el.querySelector('.scene-title')?.textContent||'')+(el.dataset.audioProfile?' · '+el.dataset.audioProfile:'');
      pauseBtn.textContent='Tạm dừng';
      if(auto){
        updateAutoUi();
        scheduleAutoScroll(el, voiceAudio?.duration*1000 || estimatedDuration(text, .94));
      }
    };
    const ended=()=>{
      if(token!==speechToken)return;
      readerVisual?.pause();
      speaking=false; autoSpeech=null; voiceAudio=null; stopSceneAutoscroll();
      if(autoNarrating){
        const nextIndex=autoIndex+1;
        if(nextIndex < sceneEls.length){
          autoStartTimer=setTimeout(()=>playAutoFromIndex(nextIndex), 650);
        } else {
          autoNarrating=false; updateAutoUi(); dock.hidden=false;
          voiceStatus.textContent='Đã đọc xong toàn bộ hành trình.';
          pauseBtn.textContent='Tạm dừng';
          autoStartTimer=setTimeout(()=>hideDock(), 2200);
        }
      } else {
        hideDock();
      }
    };
    const failed=(message)=>{
      if(token!==speechToken)return;
      stopSpeech(); dock.hidden=false; voiceStatus.textContent=message;
    };
    let fallingBack=false;
    const fallback=async()=>{
      if(token!==speechToken||fallingBack)return;
      fallingBack=true;
      clearTimeout(voiceLoadTimer);
      readerVisual?.pause();
      voiceAudio?.pause();voiceAudio=null;
      const vietnamese=()=>window.speechSynthesis?.getVoices().find(v=>/^vi(?:-|_|$)/i.test(v.lang));
      let voice=vietnamese();
      if(!voice && 'speechSynthesis' in window){
        await new Promise(resolve=>{
          const ready=()=>{if(vietnamese()){clearTimeout(timer);speechSynthesis.removeEventListener('voiceschanged',ready);resolve();}};
          const timer=setTimeout(()=>{speechSynthesis.removeEventListener('voiceschanged',ready);resolve();},1500);
          speechSynthesis.addEventListener('voiceschanged',ready);
        });
        voice=vietnamese();
      }
      if(token!==speechToken)return;
      if(!voice||!window.SpeechSynthesisUtterance){failed('Không tải được âm thanh và thiết bị chưa có giọng Việt. Kiểm tra kết nối rồi bấm Nghe lại.');return;}
      const utter=new SpeechSynthesisUtterance(text);
      utter.lang='vi-VN';utter.voice=voice;utter.rate=.94;utter.volume=1;
      utter.onstart=()=>{started();if(paused)speechSynthesis.pause();};
      utter.onend=ended;
      utter.onerror=()=>failed('Giọng đọc thiết bị gặp lỗi. Bấm Nghe lại để thử lại.');
      autoSpeech=utter;speechSynthesis.speak(utter);
    };
    const element=new Audio();voiceAudio=element;element.preload='auto';
    element.src=el.dataset.audioSrc?new URL('../'+el.dataset.audioSrc,scriptSource).href:new URL(encodeURIComponent(el.id)+'.mp3',voiceRoot).href;
    element.addEventListener('timeupdate',()=>{if(token===speechToken)readerVisual?.sync(element.currentTime,element.duration);});
    element.addEventListener('playing',started);
    element.addEventListener('ended',ended,{once:true});
    element.addEventListener('error',fallback,{once:true});
    voiceLoadTimer=setTimeout(()=>failed('Tải âm thanh quá lâu. Kiểm tra kết nối rồi bấm Nghe lại.'),15000);
    element.play().catch(err=>{
      if(token!==speechToken||fallingBack)return;
      clearTimeout(voiceLoadTimer);
      if(err.name==='NotAllowedError'){
        paused=true;pauseBtn.textContent='Tiếp tục';voiceStatus.textContent='Bấm Tiếp tục để cho phép phát âm thanh.';
      }else fallback();
    });
  }
  function playAutoFromIndex(index){
    if(index<0 || index>=sceneEls.length){autoNarrating=false; updateAutoUi(); hideDock(); return;}
    autoIndex=index;
    const el=sceneEls[index];
    setActive(el);
    const reduce=document.body.classList.contains('reduce-motion');
    el.scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'});
    autoStartTimer=setTimeout(()=>speakElement(el,{auto:true}), reduce?60:700);
  }
  function currentSceneIndex(){
    if(activeScene) return sceneEls.indexOf(activeScene);
    const hash=decodeURIComponent(location.hash.replace('#',''));
    const byHash=sceneEls.findIndex(el=>el.id===hash);
    if(byHash>=0) return byHash;
    const visible=sceneEls.findIndex(el=>{const r=el.getBoundingClientRect(); return r.top<window.innerHeight*0.66 && r.bottom>100;});
    return visible>=0?visible:0;
  }
  function toggleAutoNarration(){
    if(autoNarrating){ stopSpeech(); return; }
    autoNarrating=true; updateAutoUi();
    playAutoFromIndex(currentSceneIndex());
  }
  $$('.speak-scene').forEach(btn=>btn.addEventListener('click',()=>{autoNarrating=false; updateAutoUi(); const el=sceneById.get(btn.dataset.speak); speakElement(el,{auto:false});}));
  autoBtn?.addEventListener('click',toggleAutoNarration);
  $('#voice-stop')?.addEventListener('click',stopSpeech);
  $('#voice-pause')?.addEventListener('click',()=>{
    if(!speaking)return;
    if(paused){
      paused=false;pauseBtn.textContent='Tạm dừng';
      readerVisual?.setPlaying(true);
      if(voiceAudio){const token=speechToken;voiceAudio.play().catch(()=>{if(token!==speechToken)return;readerVisual?.pause();paused=true;pauseBtn.textContent='Tiếp tục';voiceStatus.textContent='Không phát được âm thanh. Bấm Tiếp tục để thử lại.';});}
      else window.speechSynthesis?.resume();
      if(autoNarrating && activeScene) scheduleAutoScroll(activeScene, 6000);
    }
    else{voiceAudio?.pause();readerVisual?.pause();if(autoSpeech)window.speechSynthesis?.pause();paused=true;pauseBtn.textContent='Tiếp tục'; stopSceneAutoscroll();}
  });
  document.addEventListener('visibilitychange',()=>{
    if(document.hidden && speaking && !paused){voiceAudio?.pause();readerVisual?.pause();if(autoSpeech)window.speechSynthesis?.pause();paused=true;pauseBtn.textContent='Tiếp tục'; stopSceneAutoscroll();}
  });

  const reflection=$('#reflection-text'),status=$('#reflection-status');
  const saved=storage.get('nmms_reflection');if(saved!==null)reflection.value=saved;
  $('#save-reflection')?.addEventListener('click',()=>{
    storage.set('nmms_reflection',reflection.value.slice(0,500));
    status.textContent='Đã lưu trên thiết bị này. Không có dữ liệu nào được gửi đi.';
  });
  $('#copy-reflection')?.addEventListener('click',async()=>{
    const ok=await copyText(reflection.value.trim());status.textContent=ok?'Đã sao chép nội dung.':'Chưa có nội dung hoặc trình duyệt không cho phép sao chép.';
  });
  $('#clear-reflection')?.addEventListener('click',()=>{
    reflection.value='';storage.del('nmms_reflection');status.textContent='Đã xóa ghi chú trên thiết bị này.';
  });

  // Hash links are the canonical deep-link format, including #C07_S03.
  if(location.hash){
    const id=decodeURIComponent(location.hash.slice(1));
    if(document.getElementById(id)) requestAnimationFrame(()=>document.getElementById(id).scrollIntoView({block:'start',behavior:'instant'}));
  }
  // Useful for QA without a framework; no data leaves the browser.
  window.NMMS_DEBUG=Object.freeze({sceneCount:sceneEls.length,chapterCount:$$('.chapter-link').length,getActiveScene:()=>activeScene?.id||null});
})();
