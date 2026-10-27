import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../docs/assets/source-feed.js', import.meta.url), 'utf8');
function harness({ cache = null, fail = false, noElement = false } = {}) {
  const status = { textContent: '' };
  const rows = ['GEMSDOE24', 'GEMSDOE25'].map(repo => {
    const cells = { '[data-current-head]': { textContent: '' }, '[data-advisory]': { textContent: '' } };
    return { dataset: { sourceRepo: repo, frozenRef: 'a'.repeat(40) }, cells, querySelector: key => cells[key] };
  });
  let requests = 0;
  const context = {
    document: { getElementById: () => noElement ? null : status, querySelectorAll: () => rows },
    localStorage: { getItem: () => cache === null ? null : JSON.stringify(cache), setItem: () => {} },
    setTimeout, clearTimeout, AbortController,
    fetch: async (url, options) => {
      requests += 1;
      assert.equal(options.credentials, 'omit');
      assert.ok(!('Authorization' in options.headers));
      if (fail) return { ok: false, status: 403 };
      return { ok: true, json: async () => ({ sha: url.includes('GEMSDOE24') ? 'a'.repeat(40) : 'b'.repeat(40) }) };
    },
  };
  return { run: () => vm.runInNewContext(source, context), status, rows, count: () => requests };
}

test('fetches advisory heads without credentials, never changes approvals', async () => {
  const h = harness(); await h.run();
  assert.equal(h.count(), 2);
  assert.equal(h.rows[0].cells['[data-advisory]'].textContent, 'Matches experiment snapshot');
  assert.equal(h.rows[1].cells['[data-advisory]'].textContent, 'Changed — registry audit required');
  assert.match(h.status.textContent, /1 changed; 0 unavailable/);
  assert.match(h.status.textContent, /No live leaderboard or submission approval/);
});

test('HTTP errors cannot be displayed as current or matching', async () => {
  const h = harness({ fail: true }); await h.run();
  assert.equal(h.count(), 2);
  assert.match(h.status.textContent, /0 changed; 2 unavailable/);
  assert.match(h.rows[0].cells['[data-advisory]'].textContent, /HTTP 403/);
});

test('valid hourly cache avoids redundant API requests', async () => {
  const cache = { at: Date.now(), rows: ['GEMSDOE24','GEMSDOE25'].map(repo => ({ repo, sha: 'a'.repeat(40), error: null })) };
  const h = harness({ cache }); await h.run();
  assert.equal(h.count(), 0);
  assert.match(h.status.textContent, /0 changed; 0 unavailable/);
});

test('future or malformed cache is not trusted', async () => {
  const h = harness({ cache: { at: Date.now() + 86400000, rows: [] } }); await h.run();
  assert.equal(h.count(), 2);
});

test('non-feed pages make no API requests', async () => {
  const h = harness({ noElement: true }); await h.run();
  assert.equal(h.count(), 0);
});
