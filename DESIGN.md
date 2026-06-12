# DESIGN — Moving Averages Follow Price

*Dated: 2026-06-09. Phase 1 of the Research-to-Publication Standard (v1.2).*
*Ported from the v5 manuscript's Appendix B ("Complete Replication Protocol"), MD5 `ce836c756e93086252a5ad144147ae46`. Like THESIS.md, the git timestamp documents the port, not an original pre-registration; the operators and their results predate this repo (see DECISIONS.md, 2026-06-09). Amendments to this file are appended dated, never overwritten.*

Notation: all math in ASCII. logP(t) = ln(close(t)). x(t) = logP(t) - MA(t) is the displacement. S_W is the filter (moving-average) share of gap closure.

---

## 0. Data manifest

All price data are TradingView CSV exports (daily bars unless stated). Raw files are NOT committed (exchange-licensed); they live in the project-local store `C:\Users\jaek9\Documents\LaggingTruth\Moving-Averages-Follow-Price\` and are hashed in `data/SOURCES.md` (full SHA-256 per file plus the data-variability schema). Loader contract: read columns by NAME (`time`, `close`; schemas vary 5/7/11-column), parse both ISO and US date formats, drop non-positive closes, sort ascending, take ln(close).

### Core instruments (11) — main decomposition, direction test, PE-volatility

| Instrument | Ticker | Export file | Obs | Range |
|---|---|---|---|---|
| SPX | SP:SPX | `SP_SPX, 1D_5871b.csv` | 25,187 | 1871-02-01 to 2026-03-12 |
| NDX | NASDAQ:NDX | `NASDAQ_DLY_NDX, 1D_e6961.csv` | 10,359 | 1985-01-31 to 2026-03-13 |
| NI225 | TVC:NI225 | `TVC_NI225, 1D_8be07.csv` | 19,040 | 1949-05-16 to 2026-03-13 |
| DAX | XETR:DAX | `XETR_DLY_DAX, 1D_cd703.csv` | 14,143 | 1970-01-02 to 2026-03-13 |
| FTSE | IG:FTSE | `IG_FTSE, 1D_c9679.csv` | 8,615 | 1995-01-03 to 2026-03-13 |
| HSI | HKEX:HSI | `HKEX_DLY_HSI1!, 1D_57a14.csv` | 9,585 | 1987-04-21 to 2026-03-16 |
| CL | NYMEX:CL1! | `NYMEX_CL1!, 1D_de4b1.csv` | 10,798 | 1983-03-30 to 2026-03-13 |
| GC | COMEX:GC1! | `COMEX_GC1!, 1D_1e2f0.csv` | 12,878 | 1975-01-02 to 2026-03-13 |
| ZN | CBOT:ZN1! | `CBOT_ZN1!, 1D_3436b.csv` | 11,058 | 1982-05-03 to 2026-03-13 |
| 6E | CME:6E1! | `CME_6E1!, 1D_9dd8b.csv` | 6,451 | 2000-09-12 to 2026-03-13 |
| 6J | CME:6J1! | `CME_6J1!, 1D_01e58.csv` | 6,373 | 2000-09-13 to 2026-03-13 |

### Extension instruments (2) — IS/OOS and Schelling extensions only

| Instrument | Ticker | Export file | Obs | Range |
|---|---|---|---|---|
| ES | CME_MINI:ES1! | `CME_MINI_ES1!, 1D_40b30.csv` | 7,210 | 1997-09-09 to 2026-03-13 |
| NKD | CME:NKD1! | `CME_NKD1!, 1D_92650.csv` | 5,574 | 2004-02-17 to 2026-03-13 |

Provenance notes carried from the prior iteration (see DECISIONS.md):
- **NDX is the cash index** (prior discrepancy D11). The Schelling test alone uses the NQ E-mini future (CME_MINI:NQ1!) on all its timeframes, because the cash index lacks intraday history.
- Futures roll handling: TradingView default front-month splice; the decomposition operates on log prices vs. a trailing average, which adapts to roll gaps mechanically; verified by SPX (cash) vs. ES (futures) comparison.
- Full SHA-256 hashes and per-field replicator tolerances go in `data/SOURCES.md` at the data-layer step (Phase 2).

## 1. Moving-average operators (exact)

- **SMA_N(t)** = (1/N) * sum_{k=0..N-1} logP(t-k). First valid at bar N-1.
- **EMA_N(t)**, alpha = 2/(N+1): normalized running weighted average over available history — sum_{k=0..t} (1-alpha)^k logP(t-k) / sum_{k=0..t} (1-alpha)^k. Equivalently pandas `ewm(span=N, adjust=True).mean()`. Defined from bar 0. **The adjust=True form is load-bearing** (prior discrepancy D12: the recursive adjust=False form diverges up to 30 pp).
- **WMA_M(t)**: linearly decreasing weights w_k = (M-k) / (M(M+1)/2), k = 0..M-1, k=0 most recent.
- **HMA_N(t)** = WMA_floor(sqrt(N)) applied to I(t) = 2*WMA_floor(N/2)(t) - WMA_N(t). First valid needs N + floor(sqrt(N)) - 1 bars. May transiently overshoot (negative effective weights).

**Specification disclosure — what was tried.** Main battery: 4 specs (Hull-50, SMA-50, SMA-200, EMA-50) x 11 instruments = 44 combinations. Sensitivity battery: 8 specs total (Hull-20/50/100, SMA-20/50/100/200, EMA-50) on SPX. Filter-matched horizons (B.10): 4 runs. Era analysis: 4 SPX eras. Rolling windows: 18 SPX windows. Starting-offset sensitivity: all 63 offsets. These counts are the prior iteration's full tried-spec record; no specifications were tried and discarded silently.

## 2. Experiment operators and decision rules

### E1 — Core decomposition (manuscript Section 5.1; Appendix B.3)
- **Observable:** per-event (C_P, C_W, S_W); per-combination aggregate S_W = sum(C_W) / sum(C_W + C_P), median S_W, mean S_W, event count.
- **Operator:** x(t) = logP(t) - MA(t); tau(t) = expanding 75th percentile of |x| through bar t (no look-ahead; `expanding(min_periods=252).quantile(0.75)`); event when |x(t)| > tau(t) AND >= H bars since last event (non-overlapping), H = 63, min_history = 252; at each event over horizon H: dP = logP(t+H) - logP(t), dW = MA(t+H) - MA(t), C_P = -sign(x)*dP, C_W = +sign(x)*dW, S_W = C_W/(C_P + C_W) when the denominator is nonzero.
- **Sample:** 44 combinations (Section 0 core instruments x 4 main specs).
- **Decision rule (the thesis falsifier):** thesis supported if aggregate S_W > 50% across the tested combinations; **falsified if the mechanical share comes out below 50% across the tested instruments**. Prior-iteration reference values: all 44 > 50%; 33/44 > 100%; SPX/Hull-50 = 89.9% aggregate / 60.8% median / 48.1% mean / 260 events (canary, reproduced 2026-06-09).

### E2 — Next-bar direction test (Section 5.2; B.4)
- **Operator:** same x and expanding tau as E1, but EVERY qualifying bar tested (no non-overlap spacing); toward = next bar moves price toward the MA; toward_rate = toward/total; z = (toward - 0.5*total)/sqrt(0.25*total); two-sided normal p. Drift-adjusted variant: blended null p_null = f_above*(1 - p_up) + (1 - f_above)*p_up, p_up = fraction of positive daily returns.
- **Specs:** Hull-50 and SMA-200, 11 instruments.
- **Decision rule:** no systematic toward-tendency expected; a consistent cross-instrument attraction surviving drift adjustment would undercut the thesis (subsidiary falsifier). Reference: Hull-50 toward rates near 50% on 8/11, mild ~53% attraction on 3; SMA-200 mild ~47% repulsion on 3, one surviving drift adjustment.

### E3 — Synthetic zero-attraction controls (Section 5.3; B.5)
- **i.i.d.:** 20 series, length 25,000, r ~ N(0, sigma^2), sigma_daily = 0.20/sqrt(252) ~ 0.0126, logP = cumsum(r); run E1 unchanged.
- **GARCH:** per instrument, fit GARCH(1,1) with Student-t innovations on actual daily log returns (`arch` package), simulate 20 paths of original length with mu = 0; CL and GC excluded (integrated GARCH, alpha1 + beta1 >= 1); 9 instruments x 20 = 180 paths. Seed: numpy.random.seed(42); the GARCH simulator uses an explicitly seeded distribution (prior D15 fix) so the control is reproducible.
- **Decision rule:** the aggregate S_W metric must be approximately unbiased (~100%) under zero attraction. **Material upward bias is a subsidiary falsifier** (would make elevated real-data shares a metric artifact). Reference: ~100% under zero drift; elevated values reproduce only under positive drift.

### E4 — PE-volatility correlation (Section 5.7; B.6)
- **Operator:** Hull-50 displacement; PE_raw(t) = rolling 63-day mean of x^2; PE(t) = expanding percentile rank of PE_raw (min 252 bars; `expanding(min_periods=252).rank(pct=True)*100`); FwdVol(t) = std of the next 21 daily log returns * sqrt(252); Spearman rho on a 21-bar-spaced non-overlapping sample (validity of parametric p depends on this spacing).
- **Battery:** 11 instruments full-sample + IS/OOS chronological halves of the spaced sample (33 correlations) + 5,000-iteration permutation tests on SPX, NDX, NI225, GC, CL (5 tests) = 38 tests; Bonferroni threshold 0.05/38 = 0.00132.
- **Decision rule:** the positive finding stands only if significant after Bonferroni across the battery. Reference: mean rho +0.54, all 38 significant. (B.12's cross-study note: the strategy-document spec is a different, intentionally simpler operator yielding ~+0.37 — not a replication discrepancy.)

### E5 — Schelling Point test (Section 5.9; B.7)
- **Operator:** SMA toward rates per E2 (all qualifying bars) at popular windows W in {20, 50, 100, 200} vs. neighbor mean over {W-5, W-3, W+3, W+5}; premium delta_W = toward_rate(W) - mean(neighbors); min_history by timeframe: daily 252, hourly 500, 5-min 2,000, monthly 60; inclusion requires >= 200 qualifying events for the popular window AND all four neighbors; NASDAQ instrument is NQ futures on all timeframes.
- **Sample:** prior iteration: 137 combinations across daily (13 instruments), hourly (12), 5-minute (8), monthly (2).
- **Decision rule:** no detectable premium expected; a robust positive delta at popular windows is a subsidiary falsifier. Reference: delta = -0.004 pp, p = 0.58 (t-test), with Wilcoxon and sign tests concordant.
- **OPEN DESIGN DECISION (2026-06-09, awaiting JAE):** the prior repo verified the daily layer (52 combinations) from raw data and reproduced the full-137 statistics from the prior oracle's deltas; the hourly/5-minute/monthly raw-data layer was never rebuilt. Under this Standard's contract, the 137-combination numbers need committed scripts on hashed intraday/monthly data. Options: (a) locate/re-export the intraday + monthly TradingView files and hash them into the data layer (keeps the 137-combination claim); (b) re-scope the paper's Schelling claim to the daily 52 combinations (smaller claim, fully contract-clean). Resolution to be appended here, dated.

### E6 — Quarterly reversion (Section 5.8; B.8)
- **Operator:** consecutive NON-overlapping blocks of length H over the full SPX series; per block: x(t_k) = logP(t_k) - Hull50(t_k) and forward block return R(t_k) = logP(t_k + H) - logP(t_k); Pearson r across blocks; t = r*sqrt(n-2)/sqrt(1-r^2); two-sided p. H in {21, 63, 126, 252}. Specificity check: same on NI225 and GC.
- **Decision rule:** documented qualification, not a falsifier — operates at a different timescale/mechanism. Reference: SPX r = -0.095/-0.195/-0.278 at H = 21/63/126 (significant); nothing significant on NI225/GC.

### E7 — Robustness battery (Sections 5.4-5.6; B.9-B.11)
- **Era analysis (B.9):** SPX eras pre-1930 / 1930-60 / 1960-90 / 1990-2026, threshold recalibrated per era; pre-1930 reported, not interpreted (<10 events).
- **Filter-matched horizons (B.10):** E1 re-run with H = 55 (Hull-50), 50 (SMA-50), 75 (EMA-50), 200 (SMA-200).
- **Rolling windows (B.11):** SPX, 1 catch-all 1871-1936 window + 17 ten-year windows in 5-year steps from 1931; threshold recalibrates per window.
- **Starting offsets:** all 63 offsets (Section 5.4); negligible sensitivity expected.
- **Decision rule:** qualitative stability of E1's conclusion across the battery; any sign flip or sub-50% region is reported, not smoothed.

## 3. Software environment

Python 3.11; pandas ~= 2.1, numpy ~= 1.26, scipy ~= 1.11, arch ~= 6.3 (pin exact `arch` before release). Seed 42 for synthetic controls. Each analysis script reads hashed inputs from the project-local store (path via environment variable) and writes JSON to `analysis/outputs/`.

## 4. Amendment log

*(Append dated entries below; never overwrite. Test per the Standard: would I make this change if it pushed the result the other way?)*

### 2026-06-09 — E7 expanded to cover all of manuscript Sections 5.4–5.6

E7 as originally written listed four analyses (era, filter-matched horizons, rolling windows, starting offsets). The manuscript's Sections 5.4–5.6 additionally commit to: the eight-MA-spec sensitivity on SPX (Hull-20/50/100, SMA-20/50/100/200, EMA-50; B.2), threshold sensitivity (50th/75th/90th percentiles, SPX), horizon sensitivity (H = 21/63/126/252 across the 11 core instruments), log-versus-level prices (SPX, qualitative), the 13-instrument IS/OOS chronological-midpoint split (core 11 + ES + NKD, each half decomposed from scratch), and the modern-era (1990–2026) direction test. Under the contract — no committed script, no number — E7 is expanded to cover all of these in one consolidated `analysis/robustness.py` with a single JSON output. Direction-of-result test: this expansion adds falsification surface (any sub-50% region must be reported); it is made before the script is run in this repo. Reference targets are the manuscript's printed values.

### 2026-06-09 — E5 input set pinned; full 137-combination scope retained

The prior iteration's reconstruction covered only the daily Schelling slice; the hourly/5-minute/monthly inputs were never pinned in any manifest. The original replication log (`MA Adaptation - Paper 1 - Replicating a research study with exact datasets.txt`) names the exact TradingView export files used for the 137-combination run; all 22 exist in the master data store and are adopted verbatim: hourly (12) — `CME_MINI_NQ1!, 60_985ba`, `TVC_NI225, 60_b5054`, `XETR_DLY_DAX, 60_82c16`, `IG_FTSE, 60_6e958`, `HKEX_DLY_HSI1!, 60_7c166`, `NYMEX_CL1!, 60_72c46`, `COMEX_GC1!, 60_26eca`, `CBOT_ZN1!, 60_81641`, `CME_6E1!, 60_df31a`, `CME_6J1!, 60_5c795`, `CME_MINI_ES1!, 60_127a6`, `CME_NKD1!, 60_ffee5`; 5-minute (8) — `CME_MINI_ES1!, 5_28d89`, `CME_MINI_NQ1!, 5_c2781`, `COMEX_GC1!, 5_f87e8`, `NYMEX_CL1!, 5_a29b4`, `CBOT_ZN1!, 5_bdc1e`, `CME_6E1!, 5_20b27`, `CME_6J1!, 5_c0f96`, `CME_NKD1!, 5_f1b66`; monthly (2) — `SP_SPX, 1M_9ba20`, `COMEX_GC1!, 1M_958cd` (all `.csv`). These 22 files extend the data manifest (SHA-256 hashes added to `data/SOURCES.md` and verified by `data/pull.py` at the data-layer step). E5 proceeds at full scope: daily 13 + hourly 12 + 5-minute 8 + monthly 2 instrument sets, B.7 operators, min_history 252/500/2,000/60 by timeframe, ≥200-event inclusion, 137 expected combinations.

### 2026-06-09 — E5 input set verified against the original workbook; one file corrected

The pinned set was put to an empirical identity test: sampled combinations on every timeframe were recomputed from the pinned files with the B.7 operators and compared to the original workbook (`Schelling_Point_Test.xlsx`, the artifact behind the manuscript's 137-combination tables). Results: daily, hourly, and monthly files reproduce the workbook's per-combination N and toward rates (exactly or within an off-by-one boundary effect); 5-minute files reproduce for 7 of 8 instruments (GC exact; ES/NQ/CL/ZN/6J within 1–2 events; NKD within 6 — threshold-tie effects). The exception: the replication log's 6E 5-minute entry, `CME_6E1!, 5_20b27.csv` (a 2025-03→2026-03-18 export batch), does **not** reproduce the workbook (N 3,367 vs 5,718 at SMA-20), while `CME_6E1!, 5_d72d6.csv` (2025-11-30→2026-03-13, matching the other 5-minute files' window) reproduces it **exactly** (N = 5,718, toward 46.73, δ −0.0129). The workbook arbitrates; `5_d72d6` is adopted and the manifest corrected (SHA-256 `182f84d3ff659ce269be2da6af8005e2b164ff3afabc3c5d35c510d427b4300a`, 20,059 obs). The previous amendment's "adopted verbatim" claim is corrected by this entry, per the append-only rule. Note also: the replication log's contemporaneous worry that the 5-minute files could not reach the ≥200-event threshold conflated the non-overlapping decomposition with B.7's no-spacing toward rate; the pinned 5-minute files produce 3,000–7,400 qualifying events per window, and the workbook's 32 five-minute combinations are all reproducible from data on hand.

### 2026-06-09 — E7 methods adjudicated against the original artifact

Before the consolidated `analysis/robustness.py` was accepted, every E7 sub-analysis was adjudicated row-by-row against the original artifact (`MA_Adaptation_Replication.xlsx`) and, where they conflict, against the manuscript's stated algorithms. Five rulings, each made to reproduce the paper's printed numbers or to follow the paper's stated spec — never to improve a result:

1. **Instrument set (horizons, filter-matched, IS/OOS, thresholds).** The original artifact's robustness grids use **NQ (futures) in place of NDX (cash)**, while its E1 decomposition sheet uses NDX. The paper's printed robustness numbers (e.g., 8/11 above 50% at H = 252; IS mean 106.3%) derive from the NQ set and reproduce only under it. The battery therefore runs on the NQ-substituted core (`ROBUSTNESS_CORE`); the paper-internal inconsistency is disclosed in Phase 4.
2. **EMA definition.** The manuscript's B.2 specifies the normalized form (`ewm(span=N, adjust=True)`), which is what `decomposition.py` implements; the original artifact's filter-matched EMA columns were produced by a different EMA variant (every EMA row differs by 1–3 events). The rebuild follows the manuscript's stated definition; per-row EMA differences are reported, not reconciled.
3. **Era analysis.** The paper's printed era values do **not** derive from B.9's stated per-era recalibration; they reproduce (pre-1930, 1930–60, 1960–90 exactly; 1990–2026 to 0.9 pp at equal N) from the **full-history E1 event chain binned by era under a span rule** (event start AND horizon completion inside the era). The battery adopts the binned method as primary (it is what the publication's numbers are); the contradiction with B.9's text is a Phase 4 disclosure and manuscript correction. The per-era direction test (B.4 operators, full-history threshold, era-masked observations) reproduces the artifact's columns to the observation.
4. **Rolling windows.** The original artifact's interior-window method could not be identified after testing ten implementation variants (full-history binning with and without span rule, level prices, fixed whole-window threshold, end-inclusive windows, warmup-seeded thresholds, min-history sweep 50–250, full-history threshold with per-window spacing reset, window shifts); only the catch-all 1871–1936 window reproduces (exactly, under per-window recalibration). The battery implements **per-window recalibration from scratch** (mirroring B.9's stated philosophy and B.11's prose); divergences from the published interior-window values are reported in DECISIONS.md and the published 14/18 figure is superseded by the verified rebuild value in Phase 4.
5. **IS/OOS midpoint.** Chronological midpoint = `T // 2` (confirmed: 11/13 instruments reproduce both halves exactly, including SPX; the alternative `T//2 + 1` fixes ZN but breaks five others). ZN and 6J residuals (≤2.5 pp, ±1 event) are attributed to one-row source differences in the original artifact's loads and documented.

Direction-of-result test: rulings 1 and 3 move the rebuild **toward** the paper's printed values because the printed values are the reproduction targets; rulings 2, 4, and 5 follow the manuscript's stated specs and are adopted even where they move results away from the printed values (rolling 14/18 → rebuild value; per-row EMA differences). All sub-50% regions surfaced by the battery are reported per the E7 decision rule.

### 2026-06-11 — Review-born follow-up battery registered (A2/A3/A4): the certified paper's disclosed limitations converted to committed analyses

The v1.0-certified paper discloses a deferred-limitations backlog from the adversarial review. Three of the four items are registered here as committed analyses BEFORE first run (this amendment + the three scripts commit together; the git timestamp is the registration). The fourth (roll-window exclusion, review Finding 2.3) remains on the public backlog for a post-publication revision — recorded, not run. Under Standard v1.4 these are review-born analyses and pass the full gates (ledger rows, CIC, verify) before entering the paper.

**A2 — E4 inference under serial dependence** (`analysis/pe_volatility_blockperm.py`; review Finding 3.1). Operators: the SAME non-overlapping 21-bar E4 sample; (i) Pyper-Peterman/Quenouille effective-n corrected two-sided p (t approximation, lag cap min(n//4, 50), n_eff clipped [5, n]) for all 33 Spearman tests (11 full + 11 IS + 11 OOS); (ii) circular block permutation of the PE rank-z vector against fixed FwdVol rank-z for the five E4 permutation instruments, block-length ladder L ∈ {3, 6, 12, 24} samples (63/126/252/504 bars — every rung satisfies the review's ≥63-bar floor), 5,000 permutations per rung, deterministic derived seeds (42·100000 + instrument-index·100 + L); per-instrument corrected p = MAX over the ladder (most conservative). Decision rule, fixed in advance: the corrected battery REPLACES the paper's §5.7/§6.3 caveat in the same 38-test Bonferroni frame (threshold 0.05/38); the paper reports the corrected survivor count whatever it is, including zero; the cross-sectional sign test is unaffected and reported unchanged. Specs tried: one (this battery as registered); the ladder is a robustness display, not a selection menu — no rung may be promoted as the headline.

**A3 — Spec-matched SMA-200 synthetic null** (`analysis/synthetic_control_sma200.py`; review Finding 4.2). Operators: identical to E3 in every respect (seeds 42 / 20260526, lengths, sigma, GARCH instrument set and D15 seeding) except decomposition spec = SMA-200. Decision rule: the null is reported whatever it shows; if the large-sample mean departs materially from ~100% (beyond a few SE) the §5.3 caveat is REPLACED by the measured null and the 11 SMA-200 cells are reinterpreted against it, prominently if unfavorable. Specs tried: one.

**A4 — Ex-1926 decomposition variant, SPX** (`analysis/decomposition_ex1926.py`; closes the §4.1 future-work note). Operators: E1 unchanged (H=63, expanding 75th percentile, min_history 252, non-overlapping) on SPX restricted to bars dated ≥ 1926-01-01 (cutoff as registered in §4.1), all four MA specs, recomputed from scratch (threshold path and event chain re-form without the monthly-reconstruction era); full-series rows recomputed in-run for like-for-like deltas. Decision rule: deltas reported whatever they are; any 50% crossing between variants is reported prominently and triggers manuscript reinterpretation of the affected cell.

Direction-of-result test: all three are registered before running, with report-whatever-it-shows rules; each adds falsification surface to certified findings and none can be quietly dropped — a null, unfavorable, or favorable outcome lands in the paper either way.
