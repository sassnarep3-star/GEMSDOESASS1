#!/usr/bin/env python3
"""Update GitHub source freshness only. Never update scores or experimental evidence."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    inventory = json.loads((ROOT / 'registry/focus_inventory.json').read_text())
    rows = []
    for repo, frozen in inventory['refs'].items():
        try:
            head = json.loads(subprocess.check_output(['gh', 'api', f'repos/buffedlizard55-lab/{repo}/commits/main'], timeout=60))['sha']
            rows.append(dict(repo=repo, frozen_ref=frozen, current_ref=head, changed_since_experiment=head != frozen, status='checked'))
        except (subprocess.SubprocessError, KeyError, ValueError) as error:
            rows.append(dict(repo=repo, frozen_ref=frozen, current_ref=None, changed_since_experiment=None, status='unavailable', error=str(error)[:160]))
    out = dict(checked_utc=datetime.now(timezone.utc).isoformat(), sources=rows,
        feed_scope='GitHub commit freshness only. Not a live competition leaderboard; no scores, experiments or approvals refreshed.',
        requires_registry_refresh=any(r['status'] != 'checked' or r['changed_since_experiment'] for r in rows))
    (ROOT / 'knowledge/source_feed.json').write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
