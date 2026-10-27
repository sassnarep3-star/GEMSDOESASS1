(() => {
  'use strict';
  const rows = Array.from(document.querySelectorAll('#site-rows tr[data-site]'));
  const input = document.querySelector('#site-search');
  const count = document.querySelector('#row-count');
  const empty = document.querySelector('#empty-results');
  const feed = document.querySelector('#source-feed');
  const refresh = document.querySelector('#refresh-sources');
  if (!rows.length || !input || !count || !empty || !feed || !refresh) return;

  input.addEventListener('input', () => {
    const term = input.value.trim().toLowerCase();
    let shown = 0;
    for (const row of rows) {
      const match = row.textContent.toLowerCase().includes(term);
      row.hidden = !match;
      if (match) shown += 1;
    }
    count.textContent = `${shown} ${shown === 1 ? 'site' : 'sites'}`;
    empty.hidden = shown !== 0;
  });

  const cacheKey = 'gems-source-heads-v1';
  const maxAge = 10 * 60 * 1000;
  const paint = (result, timestamp, cached) => {
    let changed = 0;
    let unknown = 0;
    for (const row of rows) {
      const status = row.querySelector('[data-source-status]');
      if (!status) continue;
      const sha = result[row.dataset.site];
      if (typeof sha !== 'string' || !/^[0-9a-f]{40}$/.test(sha)) {
        status.textContent = 'Freshness unavailable';
        status.className = 'status-line error';
        unknown += 1;
      } else if (sha !== row.dataset.reviewHead) {
        status.textContent = 'Source changed · re-audit';
        status.className = 'status-line changed';
        changed += 1;
      } else {
        status.textContent = 'Head unchanged';
        status.className = 'status-line current';
      }
    }
    const when = new Date(timestamp).toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
    feed.textContent = `GitHub repository heads checked ${when}${cached ? ' (cached)' : ''}: ${changed} changed, ${unknown} unavailable. This is not a score, registry, or submission-readiness check.`;
  };
  const checkOne = async (row) => {
    const name = row.dataset.site;
    if (!/^GEMSDOE\d+$/.test(name)) return [name, null];
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(`https://api.github.com/repos/buffedlizard55-lab/${name}/commits/main`, {
        headers: {Accept: 'application/vnd.github+json'}, signal: controller.signal
      });
      if (!response.ok) return [name, null];
      const body = await response.json();
      return [name, body && body.sha];
    } catch (_error) {
      return [name, null];
    } finally {
      clearTimeout(timer);
    }
  };
  const checkSources = async (force = false) => {
    if (!force) {
      try {
        const cached = JSON.parse(sessionStorage.getItem(cacheKey) || 'null');
        if (cached && Number.isFinite(cached.timestamp) && Date.now() >= cached.timestamp &&
            Date.now() - cached.timestamp < maxAge && cached.result && typeof cached.result === 'object') {
          paint(cached.result, cached.timestamp, true);
          return;
        }
      } catch (_error) { /* Storage is optional. */ }
    }
    refresh.disabled = true;
    feed.textContent = 'Checking public GitHub source heads; the submission decision remains blocked.';
    try {
      const result = Object.fromEntries(await Promise.all(rows.map(checkOne)));
      const timestamp = Date.now();
      // Do not cache partial failures; a later check may recover from rate limits or network errors.
      if (Object.values(result).every(sha => typeof sha === 'string' && /^[0-9a-f]{40}$/.test(sha))) {
        try { sessionStorage.setItem(cacheKey, JSON.stringify({result, timestamp})); } catch (_error) { /* optional */ }
      }
      paint(result, timestamp, false);
    } catch (_error) {
      paint({}, Date.now(), false);
    } finally {
      refresh.disabled = false;
    }
  };
  refresh.addEventListener('click', () => { void checkSources(true); });
  void checkSources();
})();
