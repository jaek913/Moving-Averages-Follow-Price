# DECISIONS — Moving Averages Follow Price

Append-only research notebook. Dead ends, surprises, decisions and reasons. Newest at the bottom. Never edit or delete an entry; correct by appending.

---

## 2026-06-09 — Project kickoff: rebuild under the Research-to-Publication Standard v1.2

**Decision.** "Moving Averages Follow Price" is rebuilt from scratch as a standalone paper under the new Standard (ClickUp doc 2kydc08j-754), as the pilot project for the new process. The old numbered series ("Paper 1" of 10/11) and its Pre-Print Review Protocol pipeline are superseded for this project.

**Provenance — this is a port, not an original pre-registration.** The science is complete and public-facing in the prior iteration. THESIS.md (Phase 0) and DESIGN.md (Phase 1) are ported from:

- v5 manuscript: `lagging-truth-paper-01/paper/Paper1_MA_Adaptation_Core_v5.md` — MD5 `ce836c756e93086252a5ad144147ae46`, 595 lines, version dated 2026-05-27. Source of the claim, gap, falsifier, operators (Appendix B), and all empirical targets.
- Old repo analysis layer: six reconstructed scripts (`decomposition.py`, `direction_test.py`, `pe_volatility.py`, `quarterly_reversion.py`, `schelling_point.py`, `synthetic_control.py`), already verified to reproduce the manuscript's figures during the prior protocol's Stages 1.5–1.6.
- Old data manifest: `lagging-truth-paper-01/data/SOURCES.md` (13 TradingView instruments, fingerprinted to Appendix B.1).

The git timestamps in this repo therefore document **when the port happened**, not when the hypotheses were formed. Honest framing per the Standard's re-design rule: nothing here is confirmatory-by-pre-registration; the empirical targets were known before this repo existed. What the rebuild adds is the Standard's integrity machinery — hashed inputs, claims.lock, verify.py, and the capped adversarial review — applied end to end.

**Known facts carried in (so they are not re-discovered as surprises):**
- EMA-50 must be the normalized `ewm(adjust=True)` form (prior discrepancy D12); the recursive form diverges up to 30 pp.
- NDX is the **cash** NASDAQ-100 index (`NASDAQ_DLY_NDX, 1D_e6961.csv`), not the NQ future (prior discrepancy D11).
- Canary already run (2026-06-09, pre-scaffold): SPX/Hull-50 through the ported decomposition operators gives 260 events / 89.9% aggregate S_W / 60.8% median / 48.1% mean — exact reproduction. SPX input `SP_SPX, 1D_5871b.csv`, SHA-256 `c75e8fb61149f5ba606ebe5a3881db40a1015ff49e322a590cf6e7a7d537cbe7`.

**Subtitle decision.** Adopted the recommended subtitle: "A Proof and Empirical Decomposition of Moving-Average Convergence: Adaptation versus Mean Reversion."

**Commit-order rule honored.** THESIS.md + DESIGN.md land (and are committed) before the first analysis commit in this repo.

---

## 2026-06-09 — E1 committed; cross-machine float-epsilon finding sets the tolerance policy

**E1 (core decomposition) is committed and reproduced on the canonical store.** Commit `b273fb4`: `analysis/decomposition.py` (MD5 `26ce61da9f8864cc5b1821d0832a678e`) + `analysis/outputs/decomposition.json`, generated on the author's machine. Headline block reproduces the prior iteration exactly: aggregate S_W range 63.5%–166.8%, 44/44 > 50%, 33/44 > 100%, SPX/Hull-50 = 89.9% / 260 events.

**Finding (recorded, not smoothed): the same script on the same byte-identical inputs produces JSON differing across machines at machine epsilon.** Claude's reference run (`5dd4f31b0e30a33414150ea22132e446`) vs. the author's committed run (`a98e6d7af660743cc1dc1addd4f5fbf0`): input SHA-256s, params, summary, and all 44 event counts identical; 14 float fields differ, max |Δ| = 2.2e-16 on aggregates and 3.5e-13 on one mean — floating-point summation-order differences between numpy/pandas builds. At paper precision (0.1 pp; unit event counts) the runs are identical.

**Decisions:**
1. The JSON generated on the author's machine from the canonical project-local store is the canonical committed output; Claude-environment runs are pre-checks.
2. Phase 3 policy: `claims.lock` tolerances for floating-point values are **relative (~1e-12)**, never exact-float equality; event counts and other integers remain exact. `verify.py` compares within tolerance.

---

## 2026-06-09 — E2+E3 committed; tolerance policy refined per optimizer-dependence

**E2 (direction test) and E3 (synthetic controls) committed** — commit `171ba1d` (scripts MD5 `0d8ec3ce78e78add0394c7e0232255c1` / `a989a3032e1a34cfb1be45a9a995c69f`, JSONs regenerated on the author's machine, plus the prior DECISIONS entry).

**E2 reproduces the prior reconstruction value-for-value** (verified by running the old script side-by-side on identical data): Hull-50 attraction HSI 53.2 / GC 53.0 / 6E 54.0 with eight ~50%; SMA-200 repulsion SPX 47.8 / NDX 47.0 / NI225 45.8; only NI225 survives drift adjustment (z = −4.04). The paper's printed GC 52.9 and z −4.08 are the manuscript's values; the reconstruction's 53.0 / −4.04 were already adjudicated as within rounding in the prior iteration and are carried as the rebuild's canonical values. `direction_test.json` is **byte-identical** between the author's machine and the Claude pre-check — E2 is fully deterministic cross-machine.

**E3 load-bearing checks green:** GARCH control mean 99.1% across 9 instruments (deterministic, D15 seeding) and large-sample i.i.d. expectation 100.57% (SE 0.89) — the aggregate-S_W metric is approximately unbiased under zero attraction. The seed-42 20-sim batch mean is **103.94%** in the rebuild (identical on both machines); the paper's printed 104.6% remains characterized as prior discrepancy D06 (one batch from the original environment, not the metric's expectation). The rebuild's canonical batch value is 103.94%.

**Finding — tolerance policy refined.** Cross-machine comparison of `synthetic_control.json`: iid rows identical; large-sample rows differ at pure machine epsilon (max 2.2e-16); **GARCH rows differ up to 3.8e-2** in raw fitted/simulated values (persistence, per-instrument mean/sd) because scipy's MLE optimizer differs across versions — while every rounded summary value matches at 0.1 precision. Policy (supersedes the blanket ~1e-12 of the previous entry): per-claim tolerances in `claims.lock` — deterministic-arithmetic floats at relative ~1e-12; **optimizer-dependent quantities (GARCH MLE fits and their simulations) at absolute ~0.1 pp**; integers exact. The author-machine JSON remains canonical.
