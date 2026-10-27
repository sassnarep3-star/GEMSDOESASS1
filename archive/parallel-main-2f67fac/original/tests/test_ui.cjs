// Zero-dependency DOM simulation for the small progressive-enhancement script.
// Browser layout is additionally checked separately with a real headless browser.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('assets/app.js', 'utf8');
const head = 'b'.repeat(40);
function element(initial = {}) {
  return Object.assign({textContent:'', className:'', hidden:false, disabled:false, listeners:{},
    addEventListener(type, fn) { this.listeners[type] = fn; }}, initial);
}
async function simulate() {
  const rows = ['GEMSDOE24','GEMSDOE25','GEMSDOE32'].map((site, idx) => {
    const status = element();
    return element({dataset:{site,reviewHead:head}, textContent:`${site} sample file`,
      querySelector() { return status; }, status});
  });
  const input=element({value:''}), count=element(), empty=element(), feed=element(), refresh=element();
  const targets={'#site-search':input,'#row-count':count,'#empty-results':empty,'#source-feed':feed,'#refresh-sources':refresh};
  const storage = new Map();
  let requests = 0;
  const context={document:{querySelectorAll:()=>rows,querySelector:k=>targets[k]},
    sessionStorage:{getItem:k=>storage.get(k) || null,setItem:(k,v)=>storage.set(k,v)},
    fetch:async url => {requests++; return url.includes('GEMSDOE25') ? {ok:false} :
      {ok:true,json:async()=>({sha:url.includes('GEMSDOE32') ? 'a'.repeat(40) : head})};},
    AbortController, setTimeout, clearTimeout, Date, console};
  vm.runInNewContext(source,context);
  // Flush the asynchronous fetch/render chain.
  await new Promise(resolve => setTimeout(resolve, 20));
  assert.match(feed.textContent, /1 changed, 1 unavailable/);
  assert.match(feed.textContent, /not a score, registry, or submission-readiness check/);
  assert.equal(rows[0].status.textContent,'Head unchanged');
  assert.equal(rows[1].status.textContent,'Freshness unavailable');
  assert.equal(rows[2].status.textContent,'Source changed · re-audit');
  assert.equal(storage.size,0,'partial network results must not be cached');
  input.value='32'; input.listeners.input();
  assert.deepEqual(rows.map(r=>r.hidden),[true,true,false]);
  assert.equal(count.textContent,'1 site');
  input.value='nothing'; input.listeners.input();
  assert.equal(empty.hidden,false);
  input.value=''; input.listeners.input();
  assert.equal(count.textContent,'3 sites');
  refresh.listeners.click();
  await new Promise(resolve => setTimeout(resolve, 20));
  assert.equal(requests,6);
  assert.equal(refresh.disabled,false);
}
simulate().then(()=>console.log('UI search, freshness and error states: PASS')).catch(e=>{console.error(e);process.exit(1)});
