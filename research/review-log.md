# Three-pass review

Completed 2026-10-27 UTC. These are software/evidence reviews, not model experiments or organizer validation.

## Pass 1 — input integrity and evidence

- Re-fetched the nine historical TIFFs, three auxiliary rasters and later peer candidates using immutable GitHub refs and full SHA-256 pins; regenerated all 72 directional overlap comparisons and the lattice lower bound.
- Found and fixed a cache-name collision between a historical site TIFF and a later candidate: unique entry IDs now take precedence and duplicate destinations are rejected before downloads. Added a regression test.
- Checked the mirrored example against labels; recorded the contradiction with the official blank-sample description and do not claim organizer provenance. Separately documented the historical champion's outside-mask failure without asserting a portal rejection.

## Pass 2 — website, status and source changes

- Rendered the nine historical rows from the same hash-bound manifest and audit, with consistency tests, explicit USER-REPORTED labels, no upload authorization and local-link checks. Reviewed the desktop and 390-pixel-wide layouts in headless Chromium; no page errors or document-wide horizontal overflow. Added a keyboard-focusable scroll region and a small-screen table hint.
- Fixed a feed/schema mismatch that could otherwise have shown changed or unavailable repositories as unchanged. Added browser unit tests for changed, partial, total-failure and malformed feeds, and made the fallback explicitly a snapshot.
- The source watch detected a new GEMSDOE24 head. Inspected its change list and hash-checked two new negative peer artifacts. Independent lattice overlaps were 37,722/37,722 and 1,810/1,814. Neither peer holdout was replayed, and the historical table remains pinned.
- Verified that the shared surface-stage overlap issue is reproducible on a synthetic example at the pinned template, and linked existing upstream reports instead of creating a private fork or duplicate issue.

## Pass 3 — fail-closed edge cases and repeatability

- Found that matching an arbitrary template alone could accept a mutually consistent but wrong-size grid. The checker now also requires the shape and transform observed in the pinned mirror by default, while stating that mirror authentication remains unresolved. Added synthetic tests for a wrong grid and wrong template dtype.
- Fixed the validator CLI to write a negative JSON receipt even on unreadable input. Corrected the forensic outside-mask diagnostic for unmasked infinities, and made the duplicate threshold use the literal positive correlation boundary with undefined comparisons failing closed. Added edge tests.
- Required unique cache destinations; checked cached template restore code, manifest and imported helper hashes before execution. Re-ran input restore with all 14 files hash-verified, plus both full-byte forensic audits and site generation.
- Final local automated suite: 28 Python tests and 5 browser-script unit tests pass (Rasterio emits dependency deprecation warnings). The sandbox browser could not verify its proxy's TLS certificate and correctly fell back to the snapshot; a separate sandbox-only test with HTTPS errors ignored reached the real GitHub API and showed RE-AUDIT REQUIRED for GEMSDOE24. Production code does not disable TLS verification. Mocked partial, total-failure and changed cases also passed. CI and Pages require separate GitHub-side verification; neither local tests nor a Pages build grants submission approval.
