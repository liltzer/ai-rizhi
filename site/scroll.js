'use strict';
(() => {
 const root=document.documentElement,bar=document.createElement('div'),fill=document.createElement('span'),tools=document.createElement('div'),percent=document.createElement('span'),top=document.createElement('button');
 bar.id='reading-progress';bar.setAttribute('aria-hidden','true');bar.append(fill);tools.id='scroll-tools';tools.hidden=true;percent.id='reading-percent';top.id='back-top';top.textContent='回到顶部';top.setAttribute('aria-label','回到页面顶部');tools.append(percent,top);document.body.append(bar,tools);
 const wheel=document.createElement('div');wheel.id='wheel-feedback';wheel.setAttribute('aria-hidden','true');wheel.innerHTML='<span class="wheel-dial"><i></i></span><b>0%</b><small>滚动探索</small>';document.body.append(wheel);
 let wheelTurn=0,wheelTimer=null;
 addEventListener('wheel',event=>{if(event.ctrlKey||document.querySelector('dialog[open]')||Math.abs(event.deltaY)<=Math.abs(event.deltaX))return;const delta=event.deltaY*(event.deltaMode===1?16:1);wheelTurn+=Math.sign(delta)*Math.min(72,Math.max(12,Math.abs(delta)*.35));wheel.style.setProperty('--wheel-angle',wheelTurn+'deg');wheel.querySelector('small').textContent=delta>0?'向下探索':'向上回看';wheel.classList.add('wheeling');clearTimeout(wheelTimer);wheelTimer=setTimeout(()=>wheel.classList.remove('wheeling'),700);schedule();},{passive:true});
 let frame=null;
 function update(){frame=null;const page=document.scrollingElement||document.documentElement,y=window.scrollY||page.scrollTop||0,max=Math.max(0,page.scrollHeight-innerHeight),ratio=max?Math.max(0,Math.min(1,y/max)):0;
  for(const dialog of document.querySelectorAll('dialog[open]')){const range=Math.max(0,dialog.scrollHeight-dialog.clientHeight);dialog.style.setProperty('--dialog-progress',range?Math.max(0,Math.min(1,dialog.scrollTop/range)):0);}
  fill.style.transform=`scaleX(${ratio})`;wheel.querySelector('b').textContent=Math.round(ratio*100)+'%';wheel.style.setProperty('--wheel-progress',ratio*360+'deg');wheel.hidden=!!document.querySelector('dialog[open]')||max===0;percent.textContent='阅读 '+Math.round(ratio*100)+'%';tools.hidden=y<280||!max;
  root.style.setProperty('--scroll-turn',root.dataset.motion==='rich'?Math.min(11,y/35)+'deg':'0deg');
 }
 function schedule(){if(frame===null)frame=requestAnimationFrame(update);}
 // Passive listeners leave wheel speed and browser scrolling under the user's control.
 addEventListener('scroll',schedule,{passive:true});document.addEventListener('scroll',event=>{if(event.target instanceof HTMLDialogElement)schedule();},{passive:true,capture:true});addEventListener('resize',schedule,{passive:true});document.querySelector('#motion-mode')?.addEventListener('change',schedule);
 top.onclick=()=>window.scrollTo({top:0,behavior:root.dataset.motion==='off'||matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
 let observer=null;const seen=new WeakSet();
 if(typeof IntersectionObserver==='function')observer=new IntersectionObserver(entries=>{for(const entry of entries){if(!entry.isIntersecting)continue;if(root.dataset.motion!=='off')entry.target.classList.add('scroll-arrive');observer.unobserve(entry.target);}},{threshold:.08,rootMargin:'0px 0px -12px 0px'});
 function cards(){if(observer)for(const card of document.querySelectorAll('.news-card'))if(!seen.has(card)){seen.add(card);observer.observe(card);}schedule();}
 for(const dialog of document.querySelectorAll('dialog'))new MutationObserver(schedule).observe(dialog,{childList:true,subtree:true});
 const list=document.querySelector('#articles');if(list)new MutationObserver(records=>{if(observer)for(const record of records)for(const node of record.removedNodes)if(node instanceof Element&&node.matches('.news-card'))observer.unobserve(node);cards();}).observe(list,{childList:true});cards();update();
})();
