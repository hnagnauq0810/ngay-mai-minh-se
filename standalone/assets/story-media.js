/* Shared, narration-synchronised photo/video sequences. All media are local. */
(() => {
  'use strict';
  if(window.NMMSMedia)return;
  const readers=new Map();
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const scriptURL=document.currentScript?.src||(/^(https?:|file:)/.test(document.baseURI)?new URL('assets/story-media.js',document.baseURI).href:'');
  let manifestRequest=null,lastManifestCheck=0;
  async function refreshStoryboards(){
    if(manifestRequest)return manifestRequest;
    if(!/^https?:/.test(scriptURL)||Date.now()-lastManifestCheck<5000)return false;
    lastManifestCheck=Date.now();
    manifestRequest=(async()=>{
      const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),5000);
      try{
        const url=new URL('./storyboard-manifest.json',scriptURL);
        url.searchParams.set('v',String(Date.now()));
        const response=await fetch(url,{cache:'no-store',signal:controller.signal});
        if(!response.ok)return false;
        const data=await response.json();if(data.version!==1||!data.scenes)return false;
        let changed=false;
        for(const [id,shots] of Object.entries(data.scenes)){
          if(!Array.isArray(shots)||!shots.length||shots.some(s=>!s.src||s.src.endsWith('.svg')||(s.kind==='illustration'&&!s.ai_generated)))continue;
          const figure=document.getElementById(id)?.querySelector('[data-shots]');if(!figure)continue;
          let previous;try{previous=JSON.parse(figure.dataset.shots);}catch{previous=[];}
          if(JSON.stringify(previous)===JSON.stringify(shots)&&JSON.stringify(readers.get(id)?.shots||shots)===JSON.stringify(shots))continue;
          figure.dataset.shots=JSON.stringify(shots);readers.get(id)?.replaceShots(shots);
          document.dispatchEvent(new CustomEvent('nmms:shots-updated',{detail:{id,shots}}));changed=true;
        }
        return changed;
      }catch{return false;}finally{clearTimeout(timeout);}
    })();
    try{return await manifestRequest;}finally{manifestRequest=null;}
  }
  class VisualPlayer {
    constructor(container,{image=null,onChange=()=>{},visible=true}={}){
      this.container=container;this.image=image||container.querySelector('img');
      this.onChange=onChange;this.visible=visible;this.playing=false;this.current=-1;this.autoIndex=-1;this.shots=[];this.generation=0;this.failed=new Set();
      this.video=document.createElement('video');this.video.className='story-shot-video';
      this.video.muted=true;this.video.defaultMuted=true;this.video.playsInline=true;this.video.loop=true;this.video.preload='none';this.video.hidden=true;
      this.video.setAttribute('aria-hidden','true');container.append(this.video);
      this.badge=document.createElement('span');this.badge.className='story-shot-badge';container.append(this.badge);
      this.failure=document.createElement('div');this.failure.className='story-media-failure';this.failure.hidden=true;
      const message=document.createElement('span');message.textContent='Chưa tải được tư liệu của cảnh này.';
      const retry=document.createElement('button');retry.type='button';retry.textContent='Thử tải lại';
      retry.addEventListener('click',()=>{this.failed.clear();this.select(this.current,{force:true});});
      this.failure.append(message,retry);container.append(this.failure);
      this.video.addEventListener('error',()=>{
        this.video.hidden=true;this.image.hidden=false;container.classList.add('video-fallback');
        this.badge.textContent='Ảnh dự phòng · '+(this.current+1)+'/'+this.shots.length;
      });
      this.image.addEventListener('error',()=>this.recoverImage());
    }
    setShots(shots){
      this.generation++;this.video.pause();this.video.removeAttribute('src');this.video.load();
      this.shots=Array.isArray(shots)?shots:[];this.current=-1;this.autoIndex=-1;this.failed.clear();
      this.select(0);this.updateNavigation();
    }
    replaceShots(shots){
      const index=this.current,autoIndex=this.autoIndex;
      this.setShots(shots);this.select(Math.max(0,Math.min(index,shots.length-1)));this.autoIndex=autoIndex;
    }
    updateBadge(){
      const shot=this.shots[this.current];if(!shot)return;
      this.badge.textContent=(shot.type==='video'?'VIDEO':shot.ai_generated?'MINH HỌA AI':'ẢNH')+' · '+(this.current+1)+'/'+this.shots.length;
    }
    async recoverImage(){
      if(!this.shots.length)return;
      const generation=this.generation,index=this.current;this.failed.add(index);
      this.image.hidden=true;this.badge.textContent='Đang tải tư liệu thay thế…';
      await refreshStoryboards();
      if(generation!==this.generation)return;
      for(let step=1;step<this.shots.length;step++){
        const next=(index+step)%this.shots.length;
        if(!this.failed.has(next)){this.select(next);return;}
      }
      // When the connection fails for the whole scene, offer an actual retry.
      this.failure.hidden=false;this.badge.textContent='Tư liệu tạm thời chưa tải được';
    }
    select(index,{manual=false,force=false}={}){
      if(!this.shots.length)return;
      index=Math.max(0,Math.min(index,this.shots.length-1));
      if(index===this.current&&!force)return;
      this.current=index;const shot=this.shots[index];this.generation++;
      this.container.classList.remove('video-fallback','shot-ready');
      this.failure.hidden=true;
      this.video.pause();this.video.hidden=true;this.video.removeAttribute('src');this.video.load();
      this.image.hidden=false;this.image.alt=shot.caption||shot.label||'';
      this.image.onload=()=>{this.failed.delete(this.current);this.image.hidden=false;this.failure.hidden=true;this.updateBadge();this.container.classList.add('shot-ready');};
      this.image.src=shot.type==='video'?shot.poster:shot.src;
      if(this.image.complete&&this.image.naturalWidth)this.container.classList.add('shot-ready');
      this.video.poster=shot.poster||'';
      this.updateBadge();
      this.onChange(shot,index,this.shots.length);this.updateNavigation();
      this.updatePlayback(manual);
      // Warm only the next still image, rather than all scenes or all videos.
      const next=this.shots[index+1];if(next&&this.playing&&this.visible){const preload=new Image();preload.src=next.poster||next.src;}
    }
    sync(time,duration,useFractions=false){
      if(!this.shots.length)return;
      const now=Math.max(0,Number(time)||0);
      let next=0;
      this.shots.forEach((shot,i)=>{const start=!useFractions&&shot.at!=null?shot.at:(shot.fraction||0)*(duration||1);if(now>=start)next=i;});
      // A manually inspected photo stays selected until the narration reaches
      // its next cue; timeupdate must not immediately undo a user's choice.
      if(next!==this.autoIndex){this.autoIndex=next;this.select(next);}
    }
    setPlaying(playing){this.playing=!!playing;this.updatePlayback();}
    updatePlayback(manual=false){
      const shot=this.shots[this.current];
      const shouldPlay=shot?.type==='video'&&this.visible&&(this.playing||manual)&&(!reduced.matches||manual);
      if(!shouldPlay){this.video.pause();return;}
      if(this.container.classList.contains('video-fallback'))return;
      if(!this.video.getAttribute('src'))this.video.src=shot.src;
      const generation=this.generation;
      this.video.play().then(()=>{
        if(generation!==this.generation)return;
        this.video.hidden=false;this.image.hidden=true;
      }).catch(()=>{if(generation===this.generation){this.video.hidden=true;this.image.hidden=false;}});
    }
    pause(){this.setPlaying(false);}
    navigation(element){
      this.nav=element;
      element.replaceChildren();
      const previous=document.createElement('button');previous.type='button';previous.textContent='❮';previous.setAttribute('aria-label','Tư liệu trước');previous.addEventListener('click',()=>this.select((this.current-1+this.shots.length)%this.shots.length,{manual:true}));
      this.counter=document.createElement('span');this.counter.className='story-shot-counter';
      const next=document.createElement('button');next.type='button';next.textContent='❯';next.setAttribute('aria-label','Tư liệu tiếp');next.addEventListener('click',()=>this.select((this.current+1)%this.shots.length,{manual:true}));
      element.append(previous,this.counter,next);
      this.motionButton=document.createElement('button');this.motionButton.type='button';this.motionButton.className='story-video-toggle';this.motionButton.textContent='▶ Xem đoạn phim';
      this.motionButton.addEventListener('click',()=>{
        if(!this.video.paused){this.video.pause();this.motionButton.textContent='▶ Xem đoạn phim';}
        else{this.updatePlayback(true);this.motionButton.textContent='❚❚ Dừng hình động';}
      });
      element.append(this.motionButton);this.updateNavigation();
    }
    updateNavigation(){
      if(this.counter)this.counter.textContent=(this.current+1)+' / '+this.shots.length;
      if(this.motionButton){this.motionButton.hidden=this.shots[this.current]?.type!=='video';this.motionButton.textContent='▶ Xem đoạn phim';}
    }
    reset(){this.setPlaying(false);this.autoIndex=-1;this.select(0);}
  }
  function mountReaders(){
    document.querySelectorAll('.scene-archive-media[data-shots]').forEach(figure=>{
      const scene=figure.closest('.story-scene');if(!scene||readers.has(scene.id))return;
      let shots;try{shots=JSON.parse(figure.dataset.shots);}catch{return;}
      const viewport=figure.querySelector('.story-visual-viewport');if(!viewport)return;
      const caption=figure.querySelector('[data-visual-caption]'),credit=figure.querySelector('[data-visual-credit]'),note=figure.querySelector('[data-visual-note]'),source=figure.querySelector('[data-visual-source]'),kind=figure.querySelector('.archive-category');
      const player=new VisualPlayer(viewport,{onChange:shot=>{
        if(caption)caption.textContent=shot.caption;
        if(credit)credit.textContent=[shot.date,shot.author,shot.license].filter(Boolean).join(' · ');
        if(note)note.textContent=shot.note;
        if(kind)kind.textContent=shot.type==='video'?'TRÍCH ĐOẠN PHIM · TẮT ÂM THANH GỐC':shot.ai_generated?'MINH HỌA TÁI DỰNG (AI)':shot.kind==='illustration'?'ĐỒ HỌA GIẢI THÍCH':shot.kind==='archive'?'ẢNH LƯU TRỮ':'ẢNH MINH HỌA · XEM NGÀY CHỤP';
        if(source){source.hidden=!shot.source;source.href=shot.source||'#';}
        figure.querySelector('.media-not-loaded')?.setAttribute('hidden','');
      }});
      player.setShots(shots);player.navigation(figure.querySelector('.story-visual-navigation'));readers.set(scene.id,player);
    });
    if('IntersectionObserver' in window){
      const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
        const id=entry.target.closest('.story-scene')?.id;const player=readers.get(id);
        if(player){player.visible=entry.isIntersecting;player.updatePlayback();}
      }),{rootMargin:'150px'});
      readers.forEach(player=>observer.observe(player.container));
    }
    // Old HTML may survive a deployment in browser history or HTTP cache.
    if([...readers.values()].some(p=>p.shots.some(s=>s.src.endsWith('.svg')||(s.kind==='illustration'&&!s.ai_generated))))refreshStoryboards();
  }
  window.addEventListener('pageshow',event=>{if(event.persisted)refreshStoryboards();});
  window.NMMSMedia={VisualPlayer,readers,mountReaders,refreshStoryboards,pauseReaders:()=>readers.forEach(player=>player.pause())};
})();
