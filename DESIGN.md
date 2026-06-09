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
