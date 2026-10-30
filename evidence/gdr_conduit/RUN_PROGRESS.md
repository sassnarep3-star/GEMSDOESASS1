# H-GDR-CONDUIT-OFFCAT run progress (2026-10-30)

This lane is a **negative**. The run is still in progress at the time of writing; the sections
below were all measured before the novelty audits were started.

| step | result |
|---|---|
| leakage canary (fold 0 AUC) | scarp 0.541, geo 0.549, cond 0.513 — **none > 0.90, pass** |
| emission | 37,654 dots, 2.8 px, 0 on catalogue, 0 within 200 m, field quantile 0.967 |
| **HOLDOUT-DTI (200 m prune)** | **0.0045** [0.0041, 0.0050], n=60988 — **equals the champion** |
| HOLDOUT-DTI (600 m prune, first run) | 0.0000 — prune-determined, not field content |
| SGMC off-catalogue DTI | 0.0887 (champion 0.0961) |
| Live Mirror calibrated | 0.2395 (champion 0.2679) |
| novelty surface (frozen 414) | **cleared=False, dup=True**, rho 0.1024, 3 px overlap 0.9989 |
| novelty dots (frozen 414) | **cleared=False, dup=True**, rho 0.0967, 3 px overlap 0.9982 |

The run card (`gdr_conduit_run_card.json`) and the validator-cleared learning-only TIFF are produced
at the end of the run, after the density diagnostic and the refreshed-registry audit. The verdict
does not depend on them: the lane fails the literal novelty rule outright.
