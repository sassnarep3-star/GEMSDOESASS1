# Why `h33-h33-2-b2…-zeros` scored 0.2778, and what it takes to beat it

*Session 2026-10-27. Every number is tagged **[measured-here]** (re-computed from bytes in this
checkout), **[official]** (organizer page / staff forum answer), or **[owner-report]** (a score copied
from a sibling site's ledger — no submission-page receipt is stored anywhere in the group).*

## 1. What the file is — re-derived from bytes, not from notes

| step | file (site) | dots | owner-reported live | construction [measured-here] |
|---|---|---|---|---|
| field | H19-5 (19GEMSDOE) | 121,131 | 0.1922 | OOF-stacked fusion of lidar openness / LRM lines + catalogue tip & step-over geometry |
| thin | `dotted-h19-5-d2-8` (GEMSDOE25) | 44,090 | 0.2600 | H19-5 emitted as isolated pixels at ≥2.8 px spacing |
| prune B=1 | `h27-4-r1-solo-d2-8` (GEMSDOE28/31) | 40,199 | 0.2708 | strict subset of d2.8 — dots ≤1 px from the catalogue removed |
| prune B=2 | `h33-h33-2-b2` (GEMSDOE32) | **37,654** | **0.2778** | **exactly** d2.8 ∩ {distance to catalogue > 2 px}: 44,090 − 6,436 = 37,654, pixel-identical (`sym diff = 0`) |

`scripts/`-free check used: `existing_faults.tif == 1` → EDT → `d2.8_dots & (d > 2)` equals the 0.2778
raster bit-for-bit (`evidence/registry_family_overlap.json`).

## 2. Why that works — the metric, not geology

**[official]** `DTI = TP_w / (TP_w + 0.2·FP_w + 0.8·FN_w)`, triangular kernel `k(d) = max(1 − d/300 m, 0)`,
truth credited by the *single best* prediction within 300 m, and **known catalogue pixels are excluded
from scoring** (staff, forum 11516). Algebraically `FN_w = |G| − TP_w`, so with `S` = emitted mass and
`M` = mass that is best-cover for some truth pixel:

```
DTI = T / (0.2·(T + S − M) + 0.8·|G|)
```

Three consequences, each visible in the ladder above:

1. **Mass is taxed at 0.2 per unit; coverage is rewarded once per truth pixel.** A solid line pays for
   every pixel but only the nearest one is credited → thinning 121k → 44k px raised the score 0.19 → 0.26.
2. **A dot on a catalogue pixel is simply ignored; a dot 1–2 px away is scored at full FP risk.** A lidar
   scarp detector re-detects the *mapped* scarp, offset by ≤2 px from the rasterised trace. Those dots
   can only earn credit if a *new* fault lies within 300 m of an *old* one — and the live ladder
   (0.2600 → 0.2708 → 0.2778 as 3,891 then 2,545 near-catalogue dots were removed) says that is rare.
3. **The marginal dot must earn `k > 0.2·DTI` ≈ 0.056 expected kernel credit at 0.28** — the group's
   whole 0.26→0.28 gain came from deleting dots below that bar, not from finding new faults.

## 3. The habitat evidence this session adds [measured-here]

| raster | median distance of dots to catalogue | live [owner-report] |
|---|---|---|
| `gems25-h66-mgd-flank` (a "flank shield" 3–15 px around the catalogue) | 5.8 px | **0.0742** |
| `dotted-h19-5-d2-8` | 15.0 px | 0.2600 |
| `h33-h33-2-b2` (0.2778) | **19.6 px** | 0.2778 |

A file whose dots live in the catalogue flank scored like noise; the champion's dots are, in the
median, 2 km from any mapped fault. **New faults in the hidden truth are predominantly far-field
(basin-interior / piedmont scarps and new systems), not re-tracings of known ones.**

## 4. Can we beat 0.2778?

Only with a **better field** at ~40k dots — emission tricks on H19-5 are exhausted (0.2708/0.2710/0.2707
are three independent attempts converging on the same number). All 12 files ≥0.24 across the nine
focus sites are ≥97.5 % within 3 px of the 0.2600 raster (`evidence/registry_family_overlap.json`):
**one field, one family**. The public #1 (0.44 on 2026-10-26 per the sibling's leaderboard snapshot)
needs a field whose top-40k pixels carry ~60 % more kernel credit than H19-5's.

This session's answer: a **segment-withheld supervised field** (E2-SWGB) that recovers withheld
catalogue segments at HOLDOUT-DTI 0.1586 vs 0.1011 for the 0.2600 base on the same evaluator, and
0.1350 vs 0.1020 when truth and domain are restricted to >500 m from visible faults. Emitted at
44,090 dots with a 600 m catalogue exclusion it is HOLDOUT-DTI **0.1401 [0.1329, 0.1452]**
(`GEMSASS1-HR-v2-segment`, 60,988 withheld positives) and is unique against the registry
(max Spearman 0.115; max 57.8 % of dots within 3 px of any registry raster).

## 5. What is *not* established

* No local instrument ranks the 0.24–0.28 family (Spearman −0.08 between holdout and live over the
  17 registry rasters; `evidence/holdout_calibration.json`). Differences inside the family are
  emission edits on one field and are below any proxy's resolution.
* The holdout truth is the *catalogue* (61k px). The live hidden truth is far smaller and farther from
  the catalogue. A holdout gain is necessary, not sufficient. **No projection in this repository is a score.**

## Sources
* Metric & submission format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
* Known-fault pixel masking: https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
* Reference solution (Tversky α=0.2, β=0.8 verified in the notebook): https://github.com/drivendataorg/gems-prize-reference-solution
* GeoDAWN survey data release: https://doi.org/10.5066/P93LGLVQ
* Sibling sites (bytes used): https://github.com/buffedlizard55-lab/GEMSDOE32 , …/GEMSDOE24 , …/GEMSDOE25 , …/GEMSDOE27 , …/GEMSDOE28 , …/GEMSDOE30 , …/GEMSDOE31 , …/GEMSDOE33 , …/GEMSDOE36
