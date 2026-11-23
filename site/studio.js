'use strict';
(() => {
 const root=document.documentElement, canvas=document.querySelector('#ambient-effects'), glow=document.querySelector('#cursor-glow'), orb=document.querySelector('#signal-orb'), stage=document.querySelector('.signal-art'), modeSelect=document.querySelector('#motion-mode');
 const palettes={day:['#5552dc','#67cce2','#f3f6fc'],night:['#b1a5ff','#64dace','#101521'],forest:['#24705b','#8bc99d','#edf4f0'],cyber:['#00e5ff','#fb43d6','#0a1224'],sakura:['#ca4e91','#9c8bf1','#fff5fa'],sunset:['#d35838','#eeb65d','#fff4ed'],ocean:['#167ca7','#37c5c8','#effbff'],grape:['#8139a6','#ce7ecc','#f7f1fc'],mono:['#232323','#858585','#f6f6f6'],aurora:['#8ce4c8','#b9a1ff','#101d28']};
 let mode='rich';try{mode=localStorage.getItem('rizhi-motion')||(matchMedia('(prefers-reduced-motion: reduce)').matches?'soft':'rich');}catch{}
 if(!['rich','soft','off'].includes(mode))mode='rich';
 root.dataset.motion=mode;modeSelect.value=mode;
 let accent=palettes.day[0],secondary=palettes.day[1];
 function syncTheme(){const palette=palettes[root.dataset.theme]||palettes.day;[accent,secondary]=palette;document.querySelector('meta[name="theme-color"]').content=palette[2];root.style.setProperty('--fx-accent',accent);root.style.setProperty('--fx-secondary',secondary);}
 window.RizhiStudio={syncTheme};syncTheme();
 modeSelect.addEventListener('change',()=>{mode=modeSelect.value;root.dataset.motion=mode;try{localStorage.setItem('rizhi-motion',mode);}catch{}if(mode==='off'){particles=[];rings=[];glow.style.opacity='0';document.querySelectorAll('.news-card').forEach(n=>{n.style.removeProperty('--tilt-x');n.style.removeProperty('--tilt-y');});}wake();});
 let ctx=null;try{ctx=canvas.getContext('2d');}catch{}
 let width=0,height=0,particles=[],rings=[],raf=0,last=0,pointer={x:-200,y:-200};
 function resize(){width=innerWidth;height=innerHeight;const scale=Math.min(devicePixelRatio||1,2);canvas.width=width*scale;canvas.height=height*scale;canvas.style.width=width+'px';canvas.style.height=height+'px';ctx?.setTransform(scale,0,0,scale,0,0);}
 addEventListener('resize',resize);resize();
 function wake(){if(ctx&&!raf&&!document.hidden)raf=requestAnimationFrame(draw);}
 function burst(x,y,count=15){if(mode==='off')return;for(let i=0;i<count;i++){const angle=Math.PI*2*i/count;particles.push({x,y,vx:Math.cos(angle)*(1+Math.random()*3),vy:Math.sin(angle)*(1+Math.random()*3),life:1,size:1.5+Math.random()*2,color:i%2?accent:secondary});}rings.push({x,y,r:6,life:1});if(particles.length>100)particles.splice(0,particles.length-100);wake();}
 function draw(time){raf=0;if(!ctx)return;ctx.clearRect(0,0,width,height);if(mode==='off'||document.hidden)return;const dt=Math.min((time-last)/16.67||1,2);last=time;
  for(const ring of rings){ring.r+=4*dt;ring.life-=.035*dt;ctx.globalAlpha=Math.max(0,ring.life)*.65;ctx.strokeStyle=accent;ctx.lineWidth=1.8;ctx.beginPath();ctx.arc(ring.x,ring.y,ring.r,0,Math.PI*2);ctx.stroke();}
  for(const p of particles){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=.025*dt;p.life-=.022*dt;ctx.globalAlpha=Math.max(0,p.life)*.8;ctx.fillStyle=p.color;ctx.beginPath();ctx.arc(p.x,p.y,p.size*Math.max(.15,p.life),0,Math.PI*2);ctx.fill();}
  ctx.globalAlpha=1;particles=particles.filter(p=>p.life>0);rings=rings.filter(r=>r.life>0);if(particles.length||rings.length)wake();
 }
 document.addEventListener('visibilitychange',()=>{if(document.hidden&&raf){cancelAnimationFrame(raf);raf=0;}else wake();});
 // A short monochrome curve, with no cursor replacement or bead particles.
 const trailToggle=document.querySelector('#trail-enabled');let trailEnabled=true;try{trailEnabled=localStorage.getItem('rizhi-trail')!=='off';}catch{}if(trailToggle)trailToggle.checked=trailEnabled;
 const svgNS='http://www.w3.org/2000/svg',trail=document.createElement('div');trail.id='pointer-trail';trail.hidden=true;trail.setAttribute('aria-hidden','true');
 const svg=document.createElementNS(svgNS,'svg'),defs=document.createElementNS(svgNS,'defs'),gradient=document.createElementNS(svgNS,'linearGradient'),path=document.createElementNS(svgNS,'path');
 gradient.id='cursor-trail-gradient';gradient.setAttribute('gradientUnits','userSpaceOnUse');
 for(const [offset,opacity] of [['0%','0'],['60%','.24'],['100%','.65']]){const stop=document.createElementNS(svgNS,'stop');stop.setAttribute('offset',offset);stop.setAttribute('stop-opacity',opacity);stop.setAttribute('stop-color','var(--fx-accent)');gradient.append(stop);}
 defs.append(gradient);path.classList.add('cursor-curve');path.setAttribute('fill','none');path.setAttribute('stroke','url(#cursor-trail-gradient)');path.setAttribute('stroke-width','1.8');path.setAttribute('stroke-linecap','round');path.setAttribute('stroke-linejoin','round');svg.append(defs,path);trail.append(svg);document.body.append(trail);
 let trailPoints=[],trailRaf=null,trailSampleAt=-Infinity;
 function clearTrail(){trailPoints=[];trail.hidden=true;path.setAttribute('d','');if(trailRaf!==null){cancelAnimationFrame(trailRaf);trailRaf=null;}}
 function paintTrail(now){
  trailRaf=null;const duration=mode==='rich'?220:110;trailPoints=trailPoints.filter(p=>now-p.at<duration);
  if(!trailEnabled||mode==='off'||document.hidden||!trailPoints.length){clearTrail();return;}
  const points=trailPoints,first=points[0],last=points[points.length-1];trail.hidden=points.length<2;
  if(points.length>1){let d=`M ${first.x} ${first.y}`;for(let i=1;i<points.length-1;i++){const p=points[i],n=points[i+1];d+=` Q ${p.x} ${p.y} ${(p.x+n.x)/2} ${(p.y+n.y)/2}`;}d+=` L ${last.x} ${last.y}`;path.setAttribute('d',d);path.style.opacity=Math.max(0,1-(now-last.at)/duration).toFixed(3);path.setAttribute('stroke-width',mode==='rich'?'1.8':'1.2');gradient.setAttribute('x1',first.x);gradient.setAttribute('y1',first.y);gradient.setAttribute('x2',last.x+.01);gradient.setAttribute('y2',last.y+.01);}
  trailRaf=requestAnimationFrame(paintTrail);
 }
 function followTrail(event){
  if(!trailEnabled||mode==='off'||event.pointerType==='touch')return;
  const now=performance.now(),host=event.target.closest?.('dialog[open]')||document.body;
  if(trail.parentNode!==host){host.append(trail);trailPoints=[];}
  if(now-trailSampleAt<8&&trailPoints.length)return;
  const prev=trailPoints[trailPoints.length-1];if(prev&&Math.hypot(event.clientX-prev.x,event.clientY-prev.y)>180)trailPoints=[];
  trailSampleAt=now;trailPoints.push({x:event.clientX,y:event.clientY,at:now});const max=mode==='rich'?14:7;if(trailPoints.length>max)trailPoints.splice(0,trailPoints.length-max);
  if(trailRaf===null)trailRaf=requestAnimationFrame(paintTrail);
 }
 trailToggle?.addEventListener('change',()=>{trailEnabled=trailToggle.checked;try{localStorage.setItem('rizhi-trail',trailEnabled?'on':'off');}catch{}clearTrail();});
 modeSelect.addEventListener('change',clearTrail);document.addEventListener('pointermove',followTrail,{passive:true});
 document.addEventListener('pointerout',event=>{if(!event.relatedTarget)clearTrail();},{passive:true});document.addEventListener('visibilitychange',()=>{if(document.hidden)clearTrail();});addEventListener('blur',clearTrail);

 document.addEventListener('pointermove',event=>{if(mode!=='rich'||event.pointerType==='touch')return;pointer={x:event.clientX,y:event.clientY};glow.style.transform=`translate3d(${pointer.x}px,${pointer.y}px,0)`;glow.style.opacity='.35';
  const card=event.target.closest('.news-card');if(card){const r=card.getBoundingClientRect(),x=(event.clientX-r.left)/r.width-.5,y=(event.clientY-r.top)/r.height-.5;card.style.setProperty('--tilt-x',(-y*5).toFixed(2)+'deg');card.style.setProperty('--tilt-y',(x*5).toFixed(2)+'deg');card.style.setProperty('--spot-x',((x+.5)*100)+'%');card.style.setProperty('--spot-y',((y+.5)*100)+'%');}
 },{passive:true});
 document.addEventListener('pointerout',event=>{const card=event.target.closest?.('.news-card');if(card&&(!(event.relatedTarget instanceof Node)||!card.contains(event.relatedTarget))){card.style.removeProperty('--tilt-x');card.style.removeProperty('--tilt-y');}if(!event.relatedTarget)glow.style.opacity='0';},{passive:true});
 document.addEventListener('pointerdown',event=>{const hit=event.target.closest('button,a,.news-card');if(mode==='off'||hit?.disabled||event.target.closest('input,select,textarea,[contenteditable]'))return;burst(event.clientX,event.clientY,mode==='rich'?16:5);if(!hit)return;const r=hit.getBoundingClientRect(),wave=document.createElement('span');wave.className='click-wave';wave.setAttribute('aria-hidden','true');wave.style.setProperty('--wave-size',Math.max(r.width,r.height)*2+'px');wave.style.left=(event.clientX-r.left)+'px';wave.style.top=(event.clientY-r.top)+'px';hit.append(wave);setTimeout(()=>wave.remove(),650);},{passive:true});
 document.addEventListener('rizhi:save',event=>{if(!event.detail.saved)return;const r=event.detail.button.getBoundingClientRect();burst(r.left+r.width/2,r.top+r.height/2,24);});
 let ox=0,oy=0,drag=null;
 function moveOrb(x,y){const r=stage.getBoundingClientRect();ox=Math.max(-Math.max(10,r.width/2-80),Math.min(Math.max(10,r.width/2-80),x));oy=Math.max(-Math.max(10,r.height/2-65),Math.min(Math.max(10,r.height/2-65),y));orb.style.setProperty('--orb-x',ox+'px');orb.style.setProperty('--orb-y',oy+'px');orb.dataset.position=Math.round(ox)+','+Math.round(oy);}
 orb.addEventListener('pointerdown',event=>{if(event.button!==0)return;drag={id:event.pointerId,x:event.clientX,y:event.clientY,ox,oy};orb.classList.add('dragging');orb.setPointerCapture?.(event.pointerId);event.preventDefault();});
 orb.addEventListener('pointermove',event=>{if(!drag||event.pointerId!==drag.id)return;moveOrb(drag.ox+event.clientX-drag.x,drag.oy+event.clientY-drag.y);});
 function release(event){if(!drag||event.pointerId!==drag.id)return;drag=null;orb.classList.remove('dragging');document.querySelector('#interaction-hint').textContent='AI 星球已移动，双击或按 Home 复位。';burst(event.clientX,event.clientY,12);}
 orb.addEventListener('pointerup',release);orb.addEventListener('pointercancel',release);orb.addEventListener('lostpointercapture',()=>{drag=null;orb.classList.remove('dragging');});
 orb.addEventListener('dblclick',()=>moveOrb(0,0));orb.addEventListener('keydown',event=>{const vectors={ArrowLeft:[-22,0],ArrowRight:[22,0],ArrowUp:[0,-22],ArrowDown:[0,22]};if(vectors[event.key]){event.preventDefault();moveOrb(ox+vectors[event.key][0],oy+vectors[event.key][1]);}else if(event.key==='Home'){event.preventDefault();moveOrb(0,0);}});
 const interestList=document.querySelector('#interest-list'),defaults=['开源模型','GitHub 软件','ComfyUI 工作流','自动化工作流','视频与动画','图像与设计','音频与语音','本地部署','编程与 Agent','论文与研究'];let order=[...defaults],dragged=null,draggingUntil=0;
 try{const old=JSON.parse(localStorage.getItem('rizhi-interests')||'[]');if(Array.isArray(old))order=[...new Set([...old.filter(t=>defaults.includes(t)),...defaults])];}catch{}
 function persistOrder(){order=[...interestList.children].map(n=>n.dataset.topic);try{localStorage.setItem('rizhi-interests',JSON.stringify(order));}catch{}document.querySelector('#interaction-hint').textContent='关注方向的顺序已保存。';}
 for(const topic of order){const b=document.createElement('button');b.className='interest-chip';b.dataset.topic=topic;b.draggable=true;b.setAttribute('aria-label',topic+'，可拖动排序，Alt 加左右方向键调整');const handle=document.createElement('span');handle.textContent='⠿';handle.className='drag-handle';handle.setAttribute('aria-hidden','true');b.append(handle,document.createTextNode(topic));interestList.append(b);}
 interestList.addEventListener('click',event=>{const b=event.target.closest('[data-topic]');if(b&&performance.now()>draggingUntil)document.dispatchEvent(new CustomEvent('rizhi:topic',{detail:b.dataset.topic}));});
 interestList.addEventListener('dragstart',event=>{dragged=event.target.closest('[data-topic]');if(!dragged)return;dragged.classList.add('sorting');event.dataTransfer?.setData('text/plain',dragged.dataset.topic);if(event.dataTransfer)event.dataTransfer.effectAllowed='move';});
 interestList.addEventListener('dragover',event=>{const over=event.target.closest('[data-topic]');if(dragged&&over&&over!==dragged){event.preventDefault();const r=over.getBoundingClientRect();interestList.insertBefore(dragged,event.clientX<r.left+r.width/2?over:over.nextSibling);}});
 interestList.addEventListener('drop',event=>{if(!dragged)return;event.preventDefault();persistOrder();dragged.classList.remove('sorting');dragged=null;draggingUntil=performance.now()+350;});
 interestList.addEventListener('dragend',()=>{if(dragged){dragged.classList.remove('sorting');persistOrder();dragged=null;}draggingUntil=performance.now()+350;});
 interestList.addEventListener('keydown',event=>{if(!event.altKey||!['ArrowLeft','ArrowRight'].includes(event.key))return;const b=event.target.closest('[data-topic]');if(!b)return;event.preventDefault();if(event.key==='ArrowLeft'&&b.previousElementSibling)interestList.insertBefore(b,b.previousElementSibling);if(event.key==='ArrowRight'&&b.nextElementSibling)interestList.insertBefore(b.nextElementSibling,b);persistOrder();b.focus();});
})();
