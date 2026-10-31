#!/usr/bin/env bash
# Git-clone fallback restore (no GitHub API quota) for the pinned upstream mirrors.
# Same pins as registry/upstream_data_manifest.json and vendor/gems57/prepare_data.py.
# Sources: buffedlizard55-lab/GEMSDOE (feature-stack parts), buffedlizard55-lab/GEMSDOE24
# (bridge + external layers). Verifies every sha256 against the manifest; fails closed.
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python - <<'PY'
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent if False else Path.cwd()
MAN = json.loads((ROOT / "registry/upstream_data_manifest.json").read_text())
PIN = {  # from vendor/gems57/prepare_data.py (assembled feature stack)
    "training_features.tif": "4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5",
}
PARTS = [
    (94371840, "0a330f8951af6c921029e25c84a579319d2db554d62d30d894d6ddc97f98cff7"),
    (94371840, "3c98037b2c997e3bbfcdfc2d9a982e8b820a77410dd7404b05cdb80594922c50"),
    (94371840, "c375c4dbc40c59bbaece572b5e348700b75935f9a30c879c82b6417e0836f31c"),
    (94371840, "b164159e6d0cb2595bc9f63a948af2646b124114a9c5921880c7516092137320"),
    (41425484, "fa0a6f9c936fac1d6f20ca37f5929b2d60bf7a80f3d477dcab886f941aee2696"),
]

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as s:
        for c in iter(lambda: s.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

def sparse_fetch(repo: str, ref: str, paths: list[str], dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        subprocess.run(["git", "init", "-q", str(dest)], check=True)
        subprocess.run(["git", "-C", str(dest), "remote", "add", "origin",
                        f"https://github.com/{repo}.git"], check=True)
    subprocess.run(["git", "-C", str(dest), "sparse-checkout", "init", "--no-cone"], check=True)
    subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", "--no-cone", *paths], check=True)
    head = subprocess.run(["git", "-C", str(dest), "rev-parse", "HEAD"], capture_output=True, text=True)
    cur = head.stdout.strip() if head.returncode == 0 else ""
    if cur != ref:
        subprocess.run(["git", "-C", str(dest), "fetch", "-q", "--depth", "1", "origin", ref], check=True)
        subprocess.run(["git", "-C", str(dest), "checkout", "-q", "FETCH_HEAD"], check=True)

# ---- group manifest items by (repo, ref)
groups: dict[tuple[str, str], list[dict]] = {}
for item in MAN["files"]:
    if item["group"] not in ("core", "external"):
        continue
    if item["id"] == "training_features":
        continue  # handled via GEMSDOE parts below
    groups.setdefault((item["repo"], item["ref"]), []).append(item)

TMP = ROOT / ".cache" / "git-restore"
for (repo, ref), items in groups.items():
    repo_dir = TMP / repo.replace("/", "_")
    rels = []
    for it in items:
        rel = it.get("path")
        if rel is None:
            continue
        rels.append(rel)
    print(f"sparse {repo}@{ref[:10]}: {len(rels)} files", flush=True)
    sparse_fetch(repo, ref, rels, repo_dir)
    for it in items:
        rel = it.get("path")
        if rel is None:
            continue
        src = repo_dir / rel
        target_group = it["dest"].split("/")[0]  # official | external
        dest = ROOT / "data" / target_group / Path(rel).name
        if target_group == "official":
            dest = ROOT / "data" / "official" / Path(rel).name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
        got = sha256(dest)
        if got != it["sha256"] or dest.stat().st_size != it["bytes"]:
            raise SystemExit(f"hash/size mismatch: {it['id']} -> {dest}")
        if dest.name.endswith("_u8.tif"):
            feat_dest = ROOT / "data" / "features" / dest.name
            shutil.copy2(dest, feat_dest)
        print("verified", it["id"], flush=True)

# ---- training features from GEMSDOE parts
feat_dir = TMP / "GEMSDOE"
rels = [f"data/bridge/gems-geodawn-numerical-features.tif.part-{i:03d}" for i in range(5)]
print("sparse GEMSDOE feature parts", flush=True)
sparse_fetch("buffedlizard55-lab/GEMSDOE", "c0c06ac82178f26b94fce3397036ef8f12a2f3a0", rels, feat_dir)
cache = ROOT / ".cache" / "source_parts"
cache.mkdir(parents=True, exist_ok=True)
part_paths = []
for i, (size, digest) in enumerate(PARTS):
    src = feat_dir / rels[i]
    dest = cache / f"gems-geodawn-numerical-features.tif.part-{i:03d}"
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    if dest.stat().st_size != size or sha256(dest) != digest:
        raise SystemExit(f"part mismatch {i}")
    part_paths.append(dest)
    print("verified part", i, flush=True)
cache_target = ROOT / ".cache" / "training_features.tif"
if not (cache_target.exists() and sha256(cache_target) == PIN["training_features.tif"]):
    tmp = cache_target.with_suffix(".tif.partial")
    with tmp.open("wb") as out:
        for p in part_paths:
            with p.open("rb") as s:
                shutil.copyfileobj(s, out, length=1 << 20)
    if sha256(tmp) != PIN["training_features.tif"]:
        raise SystemExit("reassembled feature stack hash mismatch")
    os.replace(tmp, cache_target)
official = ROOT / "data" / "official" / "training_features.tif"
official.parent.mkdir(parents=True, exist_ok=True)
official.unlink(missing_ok=True)
official.symlink_to(os.path.relpath(cache_target, official.parent))
print("training_features assembled + linked", flush=True)
print("ALL RESTORED", flush=True)
PY
