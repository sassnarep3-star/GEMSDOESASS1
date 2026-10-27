# Source register and verification notes

**Audit date:** 2026-10-27 UTC. Links below are for review. “Opened” means the page was fetched/rendered during this review, not that every claim or downloadable artifact was independently reproduced. Dynamic pages may change. This register deliberately separates official competition sources from owner-maintained GEMSDOE research pages.

## Official sources

| Source | Publisher / status | What it supports | Review performed / limitation |
|---|---|---|---|
| [GEMS Prize problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | DrivenData competition page | Goal is detecting geological faults; existing public fault data are incomplete; challenge provides GeoDAWN/INGENIOUS-related data; listed layers, coordinate system/resolution, metric and GeoTIFF requirements | Opened 2026-10-27. The description states EPSG:32611, 100 m grid; one float32 layer; values [0,1]; same bounds; outside is null/NaN. It describes distance-weighted Tversky, triangular range 300 m, alpha 0.2, beta 0.8. This is an official rules/format reference, not validation of any local TIFF. |
| [Competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) | DrivenData gated data endpoint | Location of official downloadable training features, labels, sample submission, and DEM link list | Opened 2026-10-27; redirected to `/accounts/login/`. No credential or dataset was available in this workspace. This prevents exact grid and holdout validation. |
| [Live public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | DrivenData | Current public display of ranked teams and public DW-Tversky | Opened 2026-10-27. The page displayed **LIVE PUBLIC LEADERBOARD OBSERVATION (not HOLDOUT-DTI and not a submission-page receipt): 0.4544** in its top row at time of fetch. This is a volatile public display, not a submission-page receipt for our project and not an estimate of a candidate’s score. Do not cite it as ORGANIZER-CONFIRMED under the strict receipt rule. |
| [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) | DrivenData organization on GitHub | Upstream baseline/reference implementation and its notebook/environment files | GitHub page opened 2026-10-27. It instructs competitors to download competition data and use the `data/` directory. This checkout does not contain a copy of that implementation. |
| [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) | U.S. Geological Survey (`.gov`) | Official data-release description for airborne magnetic/radiometric surveys; associated airborne lidar; public deliverable grids; DOI `10.5066/P93LGLVQ`; page reports CC0 rights | Opened 2026-10-27. Page says deliverables include magnetic/radiometric grid products and GeoTIFF images. Direct download, exact competition-footprint match, and processing equivalence were not tested. |
| [USGS GeoDAWN DOI](https://doi.org/10.5066/P93LGLVQ) | USGS DOI | Persistent reference to GeoDAWN data release | Link recorded; DOI landing/download files were not independently enumerated in this review. |
| [INGENIOUS project](https://gbcge.org/current-projects/ingenious/) | Great Basin Center for Geothermal Energy | Project context associated with the competition’s label/data sources | Link provided in official competition problem statement; page not independently fetched in this review. |
| [EPSG:32611](https://epsg.io/32611) | EPSG.io reference to EPSG registry | UTM zone 11N CRS identifier | Link recorded; exact source grid comparison not possible without sample TIFF. |
| [DOE GEMS competition guidance PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | National Laboratory of the Rockies / DOE publication host | User-specified submission guidance document | Link recorded; PDF was not fetched or parsed during this review. Do not assert uninspected contents beyond its existence/title context. |
| [Tversky index background](https://en.wikipedia.org/wiki/Tversky_index) | Wikipedia, secondary source | General metric background | Not used as authoritative competition rules; use DrivenData metric page above. |

## Nine focus-site pages (owner-published, mutable)

These pages were opened for current status and claimed evidence. They are not official organizer receipts. Claims about performance, hashes, holdout setup, or uniqueness should be reproduced from files and code before adoption.

| Project | Page reviewed | Main decision/status observed |
|---|---|---|
| GEMSDOE24 | [overview](https://buffedlizard55-lab.github.io/GEMSDOE24/) | Recent artifacts marked download-for-research only and DO NOT SUBMIT; page notes no assigned lane in an audit. |
| GEMSDOE25 | [overview](https://buffedlizard55-lab.github.io/GEMSDOE25/) | H74 marked testing-only / DO NOT SUBMIT; another diagnostic blocked by missing cache. |
| GEMSDOE27 | [overview](https://buffedlizard55-lab.github.io/GEMSDOE27/) | H31-1 described as automated evidence-pass, but selector required and not authorized for a weekly slot. |
| GEMSDOE28 | [overview](https://buffedlizard55-lab.github.io/GEMSDOE28/) | Contains conflicting sections: S22C promotion-style banner, then a later audit saying no current artifact approved; later fail-closed text should govern. |
| GEMSDOE30 | [overview](https://buffedlizard55-lab.github.io/GEMSDOE30/) | CSR-1 format/novelty pass but explicitly OK to download / NOT OK to submit because pooled holdout does not beat incumbent. |
| GEMSDOE31 | [overview](https://buffedlizard55-lab.github.io/GEMSDOE31/docs/) | Current release audit says literal registry stop; no current artifact approved; historical permissions withdrawn. |
| GEMSDOE32 | [overview](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) | H33 historical score reported as owner-reported and already submitted; current artifacts marked DO NOT SUBMIT due to evidence/uniqueness concerns. |
| GEMSDOE33 | [overview](https://buffedlizard55-lab.github.io/GEMSDOE33/) | Latest candidate marked negative; holdout gate failed; public score not estimable per page. |
| GEMSDOE36 | [decision/evidence](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/) | Conflicting page state: initial KPL-36 promotion banner versus later registry preflight that says research-only/DO NOT SUBMIT. Fail closed. |

## Specific irregularities and unresolved questions

1. The prompt’s claimed leaderboard high scores **0.3195 and 0.4413** conflict with each other. The official live page displayed **0.4544** on this review date. These are not treated as comparable HOLDOUT-DTI results, and the live observation may change.
2. The focus-site 0.2778 value is reported by the owner page but is not linked there to an organizer submission-page receipt. It cannot be labeled ORGANIZER-CONFIRMED under the run-card definition.
3. Latest public pages describe changing status and conflicting calls to action, especially GEMSDOE28 and GEMSDOE36. A top-of-page “submit” banner is not sufficient; use the latest signed/machine-bound audit and selector result or stop.
4. Public owner pages mention extensive overlap with a synthetic calibration lattice. Such a registry item must be evaluated under the stated literal rule unless protocol governance explicitly defines an exclusion; do not silently exempt it. A dense registry can make the required overlap threshold mathematically impossible at a particular dot budget, which should be preflighted before modeling.
5. Competition data are gated. The official USGS GeoDAWN source may be publicly accessible, but it is not a substitute for the exact competition-aligned stack and labels.
6. No external scientific paper or DOI was independently searched/reviewed beyond the official sources above. The hypotheses document is a test plan, not a literature review or validated geological conclusion.
