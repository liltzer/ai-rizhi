'use strict';
(() => {
 const stage=document.querySelector('.signal-art'),orb=document.querySelector('#signal-orb');if(!stage||!orb)return;
 const targets=[...stage.querySelectorAll('[data-explore]')],name=document.querySelector('#explore-name'),copy=document.querySelector('#explore-copy'),enter=document.querySelector('#explore-enter'),hint=document.querySelector('#interaction-hint');
 const scenes=[{id:'model',name:'开源模型',copy:'看具体能力、模型规格和使用门槛',badge:'模型'},{id:'workflow',name:'工作流与在线体验',copy:'找 ComfyUI 流程、HF Spaces 和演示入口',badge:'创作'},{id:'software',name:'GitHub 软件',copy:'按用途挑工具，查看安装方式和许可',badge:'工具'}];
 let selected=0,drag=null,suppressClickUntil=0,wheelDelta=0,wheelAt=-Infinity,wheelInputAt=-Infinity;
 function select(index,source='select'){
  selected=(index+scenes.length)%scenes.length;const s=scenes[selected];stage.dataset.scene=s.id;
  targets.forEach((b,i)=>{b.classList.toggle('explore-selected',i===selected);b.setAttribute('aria-pressed',String(i===selected));});
  name.textContent=s.name;copy.textContent=s.copy;enter.textContent='进入'+s.name;orb.querySelector('span').textContent=s.badge;orb.querySelector('small').textContent='拖动选择 · 松开进入';orb.setAttribute('aria-label','进入'+s.name+'，方向键或滚轮切换，拖动后松开进入');
  stage.style.setProperty('--explore-angle',selected*120+'deg');if(source==='drag')hint.textContent='松开鼠标，进入「'+s.name+'」。';
 }
 function navigate(){const s=scenes[selected];hint.textContent='已进入「'+s.name+'」。';document.dispatchEvent(new CustomEvent('rizhi:explore',{detail:{kind:s.id}}));}
 function move(x,y){orb.style.setProperty('--orb-x',x+'px');orb.style.setProperty('--orb-y',y+'px');orb.dataset.position=Math.round(x)+','+Math.round(y);}
 function targetAt(x,y,dx,dy){
  // Use real screen rectangles, including responsive scaling and browser zoom.
  const hit=targets.findIndex(b=>{const r=b.getBoundingClientRect();return r.width&&x>=r.left-16&&x<=r.right+16&&y>=r.top-16&&y<=r.bottom+16;});
  if(hit>=0)return hit;
  if(dx>Math.abs(dy)*.45)return 1;return dy>0?2:0;
 }
 orb.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,moved:false};orb.classList.add('dragging');orb.setPointerCapture?.(e.pointerId);e.preventDefault();});
 orb.addEventListener('pointermove',e=>{if(!drag||e.pointerId!==drag.id)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y,r=stage.getBoundingClientRect();drag.moved=drag.moved||Math.hypot(dx,dy)>12;move(Math.max(-r.width/2+60,Math.min(r.width/2-60,dx)),Math.max(-r.height/2+50,Math.min(r.height/2-50,dy)));if(drag.moved)select(targetAt(e.clientX,e.clientY,dx,dy),'drag');});
 function cancel(){drag=null;orb.classList.remove('dragging');move(0,0);}
 orb.addEventListener('pointerup',e=>{if(!drag||drag.id!==e.pointerId)return;const moved=drag.moved;cancel();if(moved){suppressClickUntil=performance.now()+350;navigate();}});
 orb.addEventListener('pointercancel',cancel);orb.addEventListener('lostpointercapture',()=>{if(drag)cancel();});
 orb.addEventListener('click',()=>{if(performance.now()>=suppressClickUntil)navigate();});
 orb.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowUp','ArrowRight','ArrowDown','Home'].includes(e.key)){e.preventDefault();cancel();select(e.key==='Home'?0:selected+(['ArrowLeft','ArrowUp'].includes(e.key)?-1:1));}});
 targets.forEach((b,i)=>b.addEventListener('click',()=>{select(i);navigate();}));enter.addEventListener('click',navigate);
 // Scrolling changes the live preview, while the browser keeps native page scrolling.
 stage.addEventListener('wheel',e=>{
  if(e.ctrlKey||drag||Math.abs(e.deltaY)<=Math.abs(e.deltaX))return;
  const now=performance.now();if(now-wheelInputAt>350)wheelDelta=0;wheelInputAt=now;wheelDelta+=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?innerHeight:1);
  if(Math.abs(wheelDelta)<30||now-wheelAt<280)return;
  select(selected+(wheelDelta>0?1:-1),'wheel');wheelDelta=0;wheelAt=now;stage.classList.remove('wheel-switched');void stage.offsetWidth;stage.classList.add('wheel-switched');
 },{passive:true});
 select(0);move(0,0);
})();
