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

---

## 2026-06-09 — E5 committed: data identity established by workbook reproduction; two loader traps recorded

**E5 (Schelling Point, all four timeframes) committed** — commit `bfdfe44` (`analysis/schelling_point.py` MD5 `352ff5e0c9e7800919a6a6d135e5c244` + JSON regenerated on the author's machine; preceded by data-layer commits `0996619`, `4b07142`, `6c8f887`). Result: **137 of 140 combinations included — exactly the original composition** (daily 52, hourly 48, 5-minute 32, monthly 5; same three GC-monthly exclusions) — and the **null confirmed**: mean δ −0.0051 pp, t −0.281, p(two-sided) 0.779, Wilcoxon p 0.997, sign 69/137; every timeframe and window individually non-significant. Author-machine and Claude pre-check JSONs: all 560 rows byte-identical; 10 summary p-values differ at ≤1.7e-16 (established epsilon class).

**Data identity was established empirically, not by filename.** The E5 input set was pinned from the original replication log, then verified by recomputing sampled combinations and comparing to the original workbook (`Schelling_Point_Test.xlsx`); that verification caught one wrong variant (6E 5-minute — corrected in the DESIGN amendment log and commit `4b07142`) and one missing file (NQ daily — added, `6c8f887`). The final full-battery comparison: **all 137 workbook rows reproduced**, event counts within 0–6 (83% within 2 — threshold-tie boundary effects), popular rates within 0.11 pp, deltas within 0.17 pp. Aggregate statistics sit within those tolerances of the workbook's prints (mean δ −0.0051 vs −0.0038; sign 69/137 vs 72/137); the rebuild's values are the canonical ones going forward. Lesson recorded: filenames in logs are hypotheses; original artifacts arbitrate.

**Two loader traps (now documented in the script's LOADER NOTE):**
1. Intraday TradingView exports carry **mixed UTC offsets** (DST transitions); `pd.to_datetime` without `utc=True` raises on them.
2. Some daily exports (SPX) **mix ISO and US date formats within one column**; a bare `utc=True` parse locks onto the first format and silently coerces 99% of rows to NaT — the first E5 run lost SPX daily entirely (0 events on every window) and surfaced as an inclusion count of 133, not an error. The 137-vs-133 gap was investigated, not smoothed; fix is `format="mixed"` + `utc=True`, verified to yield byte-identical sequences to the committed daily loader on all daily files. Silent-NaT coercion is a failure mode to check for in any future loader work.

---

## 2026-06-09 — E7 adjudication complete: five rulings, full-grid comparison, two paper-internal inconsistencies found

**Scope.** `analysis/robustness.py` (MD5 `7ef58a7ce6b1f01ad1c70903dd4e0f94`) consolidates all nine E7 sub-analyses. Before acceptance, every sub-battery was compared row-by-row to the original artifact (`MA_Adaptation_Replication.xlsx`). Five rulings (full text in the DESIGN.md amendment of 2026-06-09): (1) robustness grids use **NQ in place of NDX** — the paper's printed numbers derive from that substitution while its E1 uses NDX (paper-internal inconsistency #1, Phase 4 disclosure); (2) **EMA per manuscript B.2** (`adjust=True`) — the artifact's filter-matched EMA columns used a different variant; (3) **eras = full-history chain binned with a span rule** — this is provably what the published era numbers are (pre-1930 307.7/3, 1930–60 86.8/63, 1960–90 70.8/88 reproduce EXACTLY; 1990–2026 80.6/104 vs 81.5/104, single boundary-event swap), and it **contradicts the paper's own B.9 text** (paper-internal inconsistency #2, Phase 4 disclosure + correction); (4) **rolling = per-window recalibration** — the artifact's interior-window method was not recoverable after a ten-variant forensic battery (catch-all 1871–1936 reproduces exactly; interior windows correlate +0.56, mean |diff| 31.7 pp; windows are spacing-saturated, so matching event counts do not imply matching events); (5) **IS/OOS midpoint = T//2** (11/13 exact both halves; ZN/6J residuals ≤2.5 pp attributed to one-row source differences).

**Full-grid comparison (rebuild vs artifact).**
- 8-spec parameter sensitivity, SPX thresholds (102.4/89.9/65.6), and all 63 starting offsets (flat 89.85 at offsets 0–57, tail 89.91/89.62/90.05/89.25/88.31): **exact**.
- Horizons (44 rows): 32 exact; 10 misses are sub-pp boundary ties at equal/±1 N; CL carries persistent 0.5–2.7 pp offsets at equal N (same micro-diff class as ZN/6J). One real divergence: **DAX H=126 — rebuild 76.2/100 vs published 43.0/99** (one extra event cascading the H=126 spacing chain). Consequence: **H=126 is 10/11 in the rebuild vs the paper's 9/11**; H=252 reproduces the paper's 8/11 exactly (sub-50: 6J −62.2, SPX 21.5, ZN 15.3).
- Filter-matched (44 rows): Hull 6/11, SMA-50 6/11, SMA-200 9/11 rows exact; non-EMA misses ≤0.7 pp except HSI Hull matched (98.2 vs 103.6, chain swap) and SPX SMA-200 fixed (109.0/116 vs 111.0/115 — E1's known off-by-one). EMA rows 0/11 by ruling 2. Summary means within 1 pp of the paper's, SMA-200 matched mean exact at 127.8; the paper's qualitative claim (matched horizons preserve the conclusion) reproduces.
- Eras: 3/4 exact + the documented 0.9 pp residual; era direction columns reproduce to the observation (modern era 53.1%/1,832, p 0.0089 vs paper's 0.008).
- Rolling: rebuild **13/18 windows above 50% vs the published 14/18**; worst window 1991–2001 = **−8.0%** (below 50 AND below 0 — reported prominently per the E7 decision rule, alongside 1941–51 41.4, 1956–66 47.7, 1986–96 8.1, 2006–16 16.9). The published interior-window values are superseded; Phase 4 updates the manuscript figure.
- IS/OOS: 24/26 half-cells exact; **13/13 above 50% in both halves**; mean IS 106.3 exact; mean OOS 100.9 vs 100.7 (gap = exactly the ZN residual's contribution).

**Standing for Phase 3/4.** Claims to update in the manuscript: rolling 14/18 → rebuild value; H=126 9/11 → 10/11; era-method disclosure (B.9 text vs computation); NQ/NDX instrument-set disclosure; EMA-variant disclosure. The rebuild's JSON is canonical going forward. Thesis-relevant conclusions are unchanged under every ruling: the mechanical share exceeds 50% in aggregate everywhere the paper claimed it, and every sub-50% region is reported.

---

## 2026-06-10 — Phase 3 complete: ledger, checker, and RED-on-fixture selftest green on both machines

**Deliverables** (commit `dd21661`): `claims.lock` (MD5 `56ccd1fc7f6409c15a3dc770a88493d8`) — 36 hashed datasets + 20 load-bearing claims carrying 46 mechanical value checks, each claim with its 7-point CIC flags signed; `verify.py` (MD5 `bed14dd5962601b429e93a4748b8f05b`) — the four contract checks (re-hash inputs; re-run every generating script and compare within tolerance; CIC signatures; paper {{LB-id}} anchors, SKIP until Phase 4), plus `--quick`, `--replicator` (fresh-vendor-export acceptance per the SOURCES.md schema), and `--selftest`; `verification/make_fixture.py` + the deliberately broken fixture (MD5 `1367e2e948e30b410eb007361bc2c8c0`, byte-identical when generated independently on both machines — three planted defects: corrupted dataset hash, corrupted claim value, unsigned CIC).

**Verification.** Full-rerun mode GREEN on both the author machine and the Claude pre-check environment (all seven scripts regenerated from hashed data; 46/46 checks within tolerance); `--selftest` turned RED on the fixture with exactly the three planted failures on both machines, as the Standard requires. Ledger float values were drawn from the cross-machine-verified canonical outputs (documented in the lock's tolerance_policy; agreement with the author's committed JSONs is within the established ≤4.4e-16 epsilon class).

**Environment pinned.** `requirements.txt`: Python 3.12.10, arch 6.3.0, numpy 1.26.4, openpyxl 3.1.5, pandas 2.3.3, scipy 1.16.3. DESIGN §3 anticipated Python 3.11; the actual author environment is 3.12.10 and the pin records reality (correction noted here rather than editing §3, per the append-only rule). Operational trap recorded: PowerShell `>` redirection writes UTF-16 — `requirements.txt` was regenerated as UTF-8; repo text files should never be produced via PowerShell redirection.

**Claim-text note.** LB-010 (Schelling), LB-014 (H=126 10/11), and LB-019 (rolling 13/18) carry the REBUILD's canonical values where the v5 manuscript printed superseded ones; Phase 4 revises the prose to quote the ledger (the script is the truth; the paper quotes it).

---

## 2026-06-10 — Phase 4: manuscript revised to quote the ledger; CHECK4 live and green

**Naming.** Per author directive, no paper-numbering scheme: the manuscript is `paper/Moving-Averages-Follow-Price.md` and the companion is `paper/Moving-Averages-Follow-Price_companion.md`, named by the paper's title.

**Manuscript** (MD5 `89e9f33fedeadd4c75baef6f28b871f5`): produced from the v5 source (MD5 `ce836c756e93086252a5ad144147ae46`, prior-iteration repo) by 20 surgical edits applied by the deterministic transient build script `paper/_build_from_v5.py` (asserts source and output MD5s; deleted after the gate — provenance is this entry plus the conversation log). Every load-bearing number now quotes the ledger and carries its {{LB-id}} anchor (20 anchors, one per claim, at the primary claim sites in Sections 5.1–5.9). Substantive content changes: §5.1 and §5.3 synthetic-control values updated to the committed battery (103.9% iid; 100.57% ± 0.89 SE over 200 series; GARCH 99.1%); §5.4 H=126 count 9→10 of 11 and SMA-200 fixed-horizon mean 114.8→114.6, sub-50 cells named; §5.5 rewritten to the binned span rule with 1990–2026 at 80.6% and the pre-1930 era reported (307.7%, 3 events) rather than excluded; §5.6 rolling 14/18→13/18 with all five sub-50 windows named (1991–2001 = −8.0% the only negative) and OOS mean 100.7→100.9; §5.7 max ρ 0.629→0.626; §5.9 rewritten to canonical Schelling statistics (δ −0.005 pp, two-sided p 0.78, Wilcoxon 1.00, sign 69/137) with the unsupported power-analysis figure softened to a qualitative statement; B.9 corrected to the method the published values actually derive from; B.11 supersession note; B.13 actual pinned environment; new **B.14 Rebuild Reconciliation Notes** carrying the five adjudication disclosures; AI disclosure extended with the Standard-v1.2 rebuild process.

**Named defect found and removed.** v5's §5.1 contradicted itself: paragraph 1 stated 33 of 44 combinations exceed 100% (correct, ledger LB-002) while paragraph 3 stated "28 (64%) exceed 100%" — a superseded-draft remnant. The sentence was removed; the section now states the ledger value once.

**Companion** (MD5 `412184fb91cd5caf0bdca751fb21806e`): plain-English summary, education-not-advice framing, explicitly discloses that the rebuild moved one robustness count against the paper (14/18 → 13/18).

**verify.py CHECK4 patch** (new MD5 `e393de400c91c96ff8b6df7eb5524344`, supersedes `bed14dd5...` committed at dd21661): the anchor check previously matched only `paper*.md` filenames, which the title-naming convention breaks; it now matches any `.md` in `paper/` excluding companions. Re-tested in the pre-check environment: `--quick` GREEN with **0 skips** with the manuscript present (all 20 anchors found); `--selftest` still RED-on-fixture; and the check proven to FAIL with 20 missing-anchor errors against an anchor-less manuscript. With this commit, the full four-check contract is live end-to-end.

---

## 2026-06-10 — Phase 5a: adversarial review (Round 1) — certify-after-fixes; one load-bearing finding rebutted with a committed calibration

**Process.** Independent fresh-session review under the capped protocol (reviewer given only the manuscript, `claims.lock`, `SOURCES.md`; no DECISIONS, no author reasoning). Six passes, verdict **certify after fixes**: one LOAD-BEARING finding (4.1) + 14 MINOR. Full review + author fix-or-rebut recorded verbatim in `verification/adversarial_review.md` (MD5 `560f9556d2dd6032ad1f7567c84357b9`).

**Finding 4.1 (load-bearing) — REBUTTED on substance, actionable half FIXED.** The reviewer argued the 50% falsifier is unreachable by realistic reversion ("approximately unfalsifiable"). Checked empirically: new committed script `analysis/falsifier_calibration.py` (output `analysis/outputs/falsifier_calibration.json`, MD5 `b34cfe1cc421f8cd9269352467b3a880`, deterministic/byte-stable on three repeated runs) drives the paper's own `decompose()` over synthetic paths with explicit tunable attraction. Result: aggregate S_W is monotone decreasing in genuine attraction and crosses 50% at β≈0.087 (S_W: β=0→~100%; 0.03→58%; 0.08→52%; 0.20→33%). The bar is reachable; the metric is responsive. The reviewer's own "53% toward-rate" example fails on computation — the toward-rate is measurement-pinned at 64–71% across the whole β range while S_W sweeps 100→33%, which is exactly why the paper rests the headline on the aggregate share, not the toward-rate. Concession: three interpretive sentences (§7 "visual artifact", §2.1 "little residual", §6.1 adjudication claim) over-claimed beyond the S_W identity and were reanchored to the direction-test nulls; a calibration paragraph was added to §5.4.

**MINOR findings confirmed against code/data and fixed.** 2.1: CL has exactly one non-positive close (2020-04-20, -37.63), dropped by the loader's `close>0` filter (decomposition.py L101) — behavior correct, manuscript was silent → B.1 now documents it. 2.2: HSI is the front-month future (file `HKEX_DLY_HSI1!`, SOURCES line 62 "HSI front-month") mislabeled as cash index in §4.1 → relabeled. 2.4: "robust to excluding pre-1926 data" had no generating script (the one claim outside the contract) → removed, replaced with the verifiable monthly→daily transition disclosure. 4.2: synthetic null is Hull-50 only (`DECOMP_SPEC="Hull-50"`), so SMA-200@H=63 cells lack a spec-matched null → §5.3 now states this. Remaining MINORs (1.1 drift-null causality, 1.2 IS/OOS operator, 2.3 roll splices, 3.1 PE-vol serial dependence, 3.2 multiplicity, 3.3 Schelling power, 3.4 per-cell CIs, 4.3 >100% as drift, 5.1 forward-looking, 5.2 abstract omissions, 5.3 see-4.1, Pass-6 Working+Miller citations) fixed by caveat/citation. Three items explicitly deferred to a named limitations backlog (roll-window exclusion, PE-vol block permutation, SMA-200 synthetic null) rather than claimed as done.

**Manuscript.** Revised to `paper/Moving-Averages-Follow-Price.md` MD5 `baf9d1104b6f151490887c888f461483` (from committed `89e9f33f...` by the 18 review edits via transient `paper/_apply_review_edits.py`, source+output MD5 asserted, deleted after gate). All 20 {{LB-id}} anchors intact; no ledger value changed (edits are prose/caveat/disclosure only); verify.py --quick GREEN 0 skips in pre-check env. Because 4.1 was rebutted (not conceded), the thesis and 50% falsifier are retained.

**Round 2.** Triggered by the load-bearing finding per the cap. The reviewer gets one more round to accept the rebuttal+calibration or escalate; no third round.
