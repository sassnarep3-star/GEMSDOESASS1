/* Advisory GitHub freshness only. No scores, experiments, approvals or downloads mutate. */
(async () => {
  'use strict';
  const status = document.getElementById('feed-live-status');
  if (!status) return;
  const rows = [...document.querySelectorAll('[data-source-repo]')];
  const key = 'gems-source-heads-v1';
  const ttl = 60 * 60 * 1000;
  const valid = record => record && typeof record.repo === 'string' && rows.some(r => r.dataset.sourceRepo === record.repo)
    && (record.sha === null || /^[a-f0-9]{40}$/.test(record.sha));
  let results;
  let checked;
  try {
    const cached = JSON.parse(localStorage.getItem(key) || 'null');
    if (cached && Number.isFinite(cached.at) && cached.at <= Date.now() && Date.now() - cached.at < ttl
        && Array.isArray(cached.rows) && cached.rows.length === rows.length && cached.rows.every(valid)) {
      results = cached.rows;
      checked = cached.at;
    }
  } catch (_) { /* Storage access is optional. */ }
  if (!results) {
    status.textContent = 'Checking current public GitHub source heads… Experimental results remain frozen.';
    results = await Promise.all(rows.map(async row => {
      const repo = row.dataset.sourceRepo;
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 12000);
      try {
        const response = await fetch(`https://api.github.com/repos/buffedlizard55-lab/${encodeURIComponent(repo)}/commits/main`,
          { headers: { Accept: 'application/vnd.github+json' }, signal: controller.signal, credentials: 'omit' });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (typeof data.sha !== 'string' || !/^[a-f0-9]{40}$/.test(data.sha)) throw new Error('Invalid source response');
        return { repo, sha: data.sha, error: null };
      } catch (error) {
        return { repo, sha: null, error: error.name === 'AbortError' ? 'Timed out' : String(error.message).slice(0, 80) };
      } finally { clearTimeout(timer); }
    }));
    checked = Date.now();
    try { localStorage.setItem(key, JSON.stringify({ at: checked, rows: results })); } catch (_) { /* Optional cache. */ }
  }
  let changed = 0;
  let failed = 0;
  rows.forEach(row => {
    const result = results.find(r => r.repo === row.dataset.sourceRepo);
    const head = row.querySelector('[data-current-head]');
    const advisory = row.querySelector('[data-advisory]');
    if (!result || result.sha === null) {
      failed += 1;
      head.textContent = 'unavailable';
      advisory.textContent = `Freshness unavailable${result && result.error ? ` (${result.error})` : ''}`;
    } else {
      head.textContent = result.sha.slice(0, 12);
      const differs = result.sha !== row.dataset.frozenRef;
      changed += Number(differs);
      advisory.textContent = differs ? 'Changed — registry audit required' : 'Matches experiment snapshot';
    }
  });
  status.textContent = `GitHub heads checked ${new Date(checked).toISOString()}. ${changed} changed; ${failed} unavailable. Cached for one hour. No live leaderboard or submission approval is implied.`;
})();
