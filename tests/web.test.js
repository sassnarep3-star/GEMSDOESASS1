const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const script = fs.readFileSync('docs/app.js', 'utf8');
const names = ['GEMSDOE24','GEMSDOE25','GEMSDOE27','GEMSDOE28','GEMSDOE30','GEMSDOE31','GEMSDOE32','GEMSDOE33','GEMSDOE36'];
const a = 'a'.repeat(40), b = 'b'.repeat(40);
function fixture() {
  return { generated_utc: '2026-10-27T00:00:00+00:00', sites: names.map(site => ({
    site, repo: `buffedlizard55-lab/${site}`, baseline_ref: a, current_ref: a, status: 'unchanged'
  })) };
}
class Element {
  constructor() { this.children = []; this.textContent = ''; this.className = ''; this.classList = { add: name => { this.className += ' ' + name; } }; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
}
async function run(feed, getHead) {
  const elements = { '#feed-list': new Element(), '#feed-time': new Element(), '#feed-status': new Element() };
  const document = { querySelector: selector => elements[selector], createElement: () => new Element() };
  const fetch = async url => {
    if (url === 'data/feed.json') return { ok: true, json: async () => feed };
    return getHead(url);
  };
  const result = vm.runInNewContext(script, { document, fetch, AbortController, setTimeout, clearTimeout, Date });
  await result;
  return elements;
}
const response = sha => ({ ok: true, json: async () => ({ sha }) });

test('live unchanged heads are displayed, without implying submission approval', async () => {
  const el = await run(fixture(), async () => response(a));
  assert.equal(el['#feed-status'].textContent, 'NO HEAD CHANGES');
  assert.equal(el['#feed-list'].children.length, 9);
  assert.equal(el['#feed-list'].children[0].children[1].textContent, 'Head unchanged');
});
test('a changed head requires re-audit', async () => {
  const el = await run(fixture(), async url => response(url.includes('GEMSDOE32/') ? b : a));
  assert.equal(el['#feed-status'].textContent, 'RE-AUDIT REQUIRED');
  assert.equal(el['#feed-list'].children[6].children[1].textContent, 'Changed · re-audit');
});
test('a partial outage is not presented as complete', async () => {
  const el = await run(fixture(), async url => url.includes('GEMSDOE28/') ? {ok:false} : response(a));
  assert.equal(el['#feed-status'].textContent, 'LIVE PARTIAL');
  assert.equal(el['#feed-list'].children[3].children[1].textContent, 'Unavailable');
});
test('total outage labels fallback as a snapshot', async () => {
  const el = await run(fixture(), async () => { throw new Error('offline'); });
  assert.equal(el['#feed-status'].textContent, 'LIVE UNAVAILABLE');
  assert.match(el['#feed-time'].textContent, /showing snapshot/);
  assert.match(el['#feed-list'].children[0].children[1].textContent, /snapshot/);
});
test('malformed or inconsistent feed fails closed', async () => {
  const data = fixture(); data.sites[0].current_ref = b; // claims unchanged despite a change
  let requested = false;
  const el = await run(data, async () => { requested = true; return response(a); });
  assert.equal(el['#feed-status'].textContent, 'UNKNOWN');
  assert.match(el['#feed-time'].textContent, /invalid/);
  assert.equal(requested, false);
});
