#!/usr/bin/env bash
# Restore the byte-verified mirrors this project depends on (competition originals require a DrivenData login
# and are unreachable from the build sandbox). Sources: sibling GitHub repositories of the same group.
#   template + catalogue + u8 feature stacks : https://github.com/buffedlizard55-lab/GEMSDOE24 (data/bridge, data/external)
#   registry rasters                         : the docs/downloads/ folder of each focus site
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
clone() { git clone -q --depth 1 --filter=blob:none --sparse "https://github.com/buffedlizard55-lab/$1.git" "$TMP/$1"; (cd "$TMP/$1" && git sparse-checkout set --no-cone "$2" >/dev/null); }
mkdir -p data/bridge data/features data/registry
clone GEMSDOE24 "data/bridge/* data/external/*_u8.tif data/external/geodawn_rad.json data/external/geodawn_extensions.json data/external/lidar_scarp_features.json docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif docs/downloads/gems24-gvc1-negative-geothermal-lineament-submod-20261025-abe8e51c719d-zeros.tif"
cp "$TMP/GEMSDOE24/data/bridge/existing_faults.tif" "$TMP/GEMSDOE24/data/bridge/sample_submission.tif" data/bridge/
cp "$TMP/GEMSDOE24/data/external/"*_u8.tif "$TMP/GEMSDOE24/data/external/"{geodawn_rad,geodawn_extensions,lidar_scarp_features}.json data/features/
cp "$TMP/GEMSDOE24/docs/downloads/"*.tif data/registry/
while read -r repo file; do
  clone "$repo" "docs/downloads/$file"; cp "$TMP/$repo/docs/downloads/$file" data/registry/
done <<'LIST'
GEMSDOE32 gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif
GEMSDOE25 gems25-h66-mgd-flank-sapd3-0-k3p5-20261025-da617550a0e9-zeros.tif
GEMSDOE27 gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif
GEMSDOE27 gems27-h29-hydrothermal-piedmont-celf-20261025-511898747886-allfinite.tif
GEMSDOE28 gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan.tif
GEMSDOE28 gems28-h32-1-prethin-tip-euler-d2-8-20261003-31e35eee884e-nan.tif
GEMSDOE28 gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif
GEMSDOE28 gems28-h38-1-hf-euler-r30-r1-20261003-56a9f473edc7-nan.tif
GEMSDOE28 gems28-s18-mxtp-20261025-3e95505c011a-allfinite.tif
GEMSDOE30 gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif
GEMSDOE30 gems30-MSDB1-edge44090-20261025-e7856ec3f14a.tif
GEMSDOE31 gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif
GEMSDOE32 gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif
GEMSDOE33 GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif
GEMSDOE36 gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif
LIST
rm -rf "$TMP"
sha256sum -c data/SHA256SUMS
echo "assets restored and verified"
