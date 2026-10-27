// Public GitHub metadata only. Changed heads mean re-audit, not permission to submit.
(async () => {
  const list = document.querySelector('#feed-list');
  const time = document.querySelector('#feed-time');
  const status = document.querySelector('#feed-status');
  if (!list || !time || !status) return;
  const expected = ['GEMSDOE24','GEMSDOE25','GEMSDOE27','GEMSDOE28','GEMSDOE30','GEMSDOE31','GEMSDOE32','GEMSDOE33','GEMSDOE36'];
  const sha = value => typeof value === 'string' && /^[0-9a-f]{40}$/.test(value);
  function display(rows, label, badge, style = 'neutral', snapshot = false) {
    time.textContent = label;
    status.textContent = badge;
    status.className = 'badge ' + style;
    list.replaceChildren();
    for (const item of rows) {
      const row = document.createElement('div'); row.className = 'feed-item';
      const name = document.createElement('strong'); name.textContent = item.site;
      const state = document.createElement('span'); state.className = 'feed-state';
      if (item.status === 'unavailable') { state.classList.add('unavailable'); state.textContent = 'Unavailable'; }
      else if (item.status === 'changed') { state.classList.add('changed'); state.textContent = 'Changed · re-audit'; }
      else state.textContent = snapshot ? 'Unchanged (snapshot)' : 'Head unchanged';
      row.append(name, state); list.append(row);
    }
  }
  try {
    const response = await fetch('data/feed.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('feed request failed');
    const feed = await response.json();
    if (!Array.isArray(feed.sites) || feed.sites.length !== expected.length || !Number.isFinite(Date.parse(feed.generated_utc))) throw new Error('invalid feed');
    const names = new Set(feed.sites.map(s => s.site));
    if (names.size !== expected.length || expected.some(s => !names.has(s)) || feed.sites.some(s =>
      s.repo !== `buffedlizard55-lab/${s.site}` || !sha(s.baseline_ref) ||
      !['unchanged','changed','unavailable'].includes(s.status) ||
      (s.status !== 'unavailable' && (!sha(s.current_ref) || (s.status === 'unchanged') !== (s.current_ref === s.baseline_ref)))
    )) throw new Error('invalid feed rows');
    const stamp = feed.generated_utc.replace('T', ' ').replace('+00:00', ' UTC');
    display(feed.sites, `Snapshot ${stamp} · checking public GitHub heads…`, 'CHECKING', 'neutral', true);
    const rows = await Promise.all(feed.sites.map(async item => {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 8000);
        try {
          const url = `https://api.github.com/repos/${item.repo}/commits/main`;
          const res = await fetch(url, { cache: 'no-store', signal: controller.signal, headers: { Accept: 'application/vnd.github+json' } });
          if (!res.ok) throw new Error('head unavailable');
          const body = await res.json();
          if (!sha(body.sha)) throw new Error('invalid head');
          return { site: item.site, status: body.sha === item.baseline_ref ? 'unchanged' : 'changed' };
        } finally { clearTimeout(timeout); }
      } catch (_) { return { site: item.site, status: 'unavailable' }; }
    }));
    const missing = rows.filter(s => s.status === 'unavailable').length;
    const changed = rows.some(s => s.status === 'changed');
    if (missing === rows.length) {
      display(feed.sites, `Live check unavailable; showing snapshot from ${stamp}. Rate limits or network restrictions may apply.`, 'LIVE UNAVAILABLE', '', true);
    } else {
      const label = `Live GitHub head check ${new Date().toISOString().replace('T', ' ').replace('Z', ' UTC')} · pinned evidence is separate.`;
      display(rows, label, missing ? 'LIVE PARTIAL' : changed ? 'RE-AUDIT REQUIRED' : 'NO HEAD CHANGES', missing ? '' : changed ? 'amber' : 'neutral');
    }
  } catch (_) {
    time.textContent = 'Source feed unavailable or invalid. No freshness or submission status can be inferred.';
    status.textContent = 'UNKNOWN';
  }
})();
