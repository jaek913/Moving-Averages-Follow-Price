# REPLICATION.md - Moving Averages Follow Price
Version 1.0 - 2026-08-07. ASCII-only. This document makes the paper
rebuildable from text: it consolidates the environment, the committed
scripts, the hashed inputs, the run commands, and the verification levels.
The frozen operators and decision rules live in DESIGN.md and the dated
DECISIONS.md record - this document POINTS to them and never restates them,
so it cannot drift from the record.

## 0. Environment

- OS: Windows 11 (author machine); analyses are pure Python and run on any OS.
- Python 3.12 with numpy, pandas, scipy (see requirements.txt).
- Repo: github.com/jaek913/Moving-Averages-Follow-Price.
- Data store: git-ignored; 36 input files pinned by SHA-256 in claims.lock's
  datasets block and documented in data/SOURCES.md. Set LT_DATA_DIR if the
  store is not at the default location recorded there.
- Every analysis writes JSON to analysis/outputs/ (committed).

## 1. The contract

A number may appear in the paper only if a committed script, run on hashed
input data, regenerates it on demand. The paper's source prints every
load-bearing value with an adjacent {{LB-nnn}} anchor tag; verify.py CHECK 4
ties each printed value to the machine-checked ledger (claims.lock, 24
claims, 73 checks) at its anchor. The PDF build strips the anchor tags
(they are verification plumbing, not prose); see build_pdf.ps1.

## 2. Analysis scripts (committed; outputs in analysis/outputs/)

| Script | Subject |
|---|---|
| analysis/decomposition.py | Gap-closure decomposition, 44 instrument-filter combinations (aggregate + individual-event MA shares) |
| analysis/decomposition_ex1926.py | Registered robustness: SPX decomposition restricted to 1926-onward bars |
| analysis/direction_test.py | Next-bar toward-rate test (Hull-50, SMA-200) with drift adjustment |
| analysis/falsifier_calibration.py | Committed calibration experiment behind the 50% falsifier (adversarial-review challenge) |
| analysis/pe_volatility.py | Displacement -> forward realized volatility (Spearman battery) |
| analysis/pe_volatility_blockperm.py | Registered robustness: serial-dependence-corrected inference (Pyper-Peterman + circular block permutations) |
| analysis/quarterly_reversion.py | SPX quarterly (126-day) return reversion |
| analysis/robustness.py | Horizon and specification robustness checks |
| analysis/schelling_point.py | Self-fulfilling-prophecy test, 137 instrument-window-timeframe combinations |
| analysis/synthetic_control.py | Random-walk + GARCH-calibrated decomposition bias controls |
| analysis/synthetic_control_sma200.py | Registered robustness: specification-matched SMA-200 synthetic null |

Theory results (Lemmas 1-4, Theorems 2-3) are proven in the paper with
convergence-rate derivations in Appendix A; the disclosure records the
three-way checking of the mathematical results (hand, randomized numerical
stress test of 28,000+ cases, symbolic machine-checking).

## 3. Verification levels available to a replicator

```
python verify.py --selftest      # checker vs the deliberately broken fixture; PASS only if it turns RED
python verify.py --quick         # re-hash inputs + compare committed outputs + CIC + paper anchors
python verify.py                 # full: re-run every generating script (~15-30 min) + all checks
python verify.py --replicator    # fresh vendor exports: hash mismatches downgrade to WARN under schema rules
```

Tolerances (DECISIONS.md 2026-06-09): integers/booleans exact; deterministic
floats rel 1e-12; optimizer-dependent (GARCH MLE) abs 0.1 percentage points.

## 4. Reviews and records

The two-round adversarial review is committed verbatim at
verification/adversarial_review.md (prompts alongside). Citation
verification is recorded in verification/citation_check.md (31/31).
CORRECTIONS.md at the repo root is the public post-publication log.
The PDF is built by build_pdf.ps1 (series Cambria preamble, stale-output
guard); Appendix B in the paper gives the full replication protocol for
every empirical claim.
