#!/usr/bin/env python3
"""Fetch hash-pinned owner mirrors for a read-only audit, not for submission.

Only public GitHub blobs named in data/inputs.json are read, normally via gh.
A tightly scoped HTTPS API fallback handles one known gh binary-transfer error.
Files are ignored by Git and are not used as training data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data' / 'inputs.json'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def check_entry(entry: dict) -> None:
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', entry['repo']):
        raise ValueError('Invalid repository')
    if not re.fullmatch(r'[0-9a-f]{40}', entry['ref']):
        raise ValueError('A full pinned commit is required')
    if not re.fullmatch(r'[0-9a-f]{64}', entry['sha256']):
        raise ValueError('Invalid SHA-256')
    if Path(entry['local_name']).name != entry['local_name']:
        raise ValueError('Local name must be a single file name')
    if Path(entry['path']).is_absolute() or '..' in Path(entry['path']).parts:
        raise ValueError('Invalid repository path')


class ApiOnlyRedirect(HTTPRedirectHandler):
    """Never forward an optional GitHub token to another host or insecure URL."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        url = urlsplit(newurl)
        if (url.scheme != 'https' or url.hostname != 'api.github.com'
                or url.port not in (None, 443) or url.username or url.password):
            raise ValueError('Refusing a redirect outside HTTPS api.github.com')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_raw_http(entry: dict, stream) -> None:
    """Bounded, exact-byte fallback for the specific gh binary transform bug."""
    repo, ref = entry['repo'], entry['ref']
    path = quote(entry['path'], safe='/')
    url = f'https://api.github.com/repos/{repo}/contents/{path}?ref={ref}'
    headers = {'Accept': 'application/vnd.github.raw+json', 'User-Agent': 'gems-witness-audit'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    request = Request(url, headers=headers)
    max_bytes = 16 * 1024 * 1024  # All pinned witnesses are much smaller; avoid unbounded downloads.
    total = 0
    with build_opener(ApiOnlyRedirect()).open(request, timeout=120) as response:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            total += len(block)
            if total > max_bytes:
                raise ValueError('Witness response exceeds the permitted transfer size')
            stream.write(block)


def fetch(entry: dict, destination: Path) -> str:
    check_entry(entry)
    target = destination / entry['local_name']
    if target.exists():
        if not target.is_file() or sha256(target) != entry['sha256']:
            raise ValueError(f'Existing file fails its pin: {target}; remove it before retrying')
        return 'cached and verified'
    endpoint = f"repos/{entry['repo']}/contents/{entry['path']}?ref={entry['ref']}"
    fd, tmp_name = tempfile.mkstemp(prefix='.fetch-', dir=destination)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, 'wb') as stream:
            try:
                subprocess.run(
                    ['gh', 'api', endpoint, '-H', 'Accept: application/vnd.github.raw+json'],
                    stdout=stream, stderr=subprocess.PIPE, check=True, timeout=120,
                )
            except subprocess.CalledProcessError as error:
                # Some gh releases incorrectly transcode binary output and emit
                # this exact error. Do not fall back on authentication or other failures.
                if error.stderr and error.stderr.strip() == b'transform: short source buffer':
                    stream.seek(0)
                    stream.truncate()
                    fetch_raw_http(entry, stream)
                else:
                    if error.stderr:
                        sys.stderr.write(error.stderr.decode('utf-8', errors='replace'))
                    raise
        if sha256(tmp) != entry['sha256']:
            raise ValueError(f"SHA-256 mismatch for {entry['id']}; not installing file")
        os.replace(tmp, target)
        return 'downloaded and verified'
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=ROOT / '.local-data' / 'audit')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if manifest['schema'] != 'gems-audit-inputs-v1':
        raise ValueError('Unexpected input manifest schema')
    entries = manifest['inputs']
    if len({entry['local_name'] for entry in entries}) != len(entries):
        raise ValueError('Duplicate destination in input manifest')
    args.input_dir.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        print(f"{entry['id']}: {fetch(entry, args.input_dir)}")
    print('Integrity only. Owner mirrors are NOT authenticated organizer data. No file is submit-approved.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
