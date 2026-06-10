"""
pe_volatility.py -- E4: the displacement-volatility correlation (DESIGN.md section E4).

"Moving Averages Follow Price" -- Research-to-Publication Standard v1.2, Phase 2.
Ported 2026-06-09 from the prior iteration's verified reconstruction (see
DECISIONS.md); operators unchanged. Instrument key "Nikkei" renamed "NI225" to
match this repo's manifest (label-only change).

WHAT IT DOES
    For each instrument it builds two series and correlates them:
      PE  (displacement energy) -- how far price has been sitting from its Hull-50
          moving average lately, expressed as an expanding percentile rank.
      FwdVol -- the realized volatility of the NEXT 21 trading days (annualized),
          a purely forward window with no overlap with the PE window.
    A positive Spearman correlation means: when price is far from its average, the
    next month tends to be more volatile. The test is run full-sample, on in-sample
    and out-of-sample halves, and -- for the five longest instruments -- against a
    5,000-iteration permutation null. Bonferroni correction is applied across 38 tests.

NOTE ON METHOD (prior discrepancy D13)
    The prior manuscript's Appendix B.6 described this analysis inaccurately in two
    respects; this code follows what the paper's results actually used (verified
    against the original oracle workbook to within 0.003 with sample sizes matching
    exactly):
      (1) Sampling. The correlation is computed on NON-OVERLAPPING samples spaced by
          the 21-day forward-vol window (one observation every 21 bars), so the
          forward-volatility windows do not overlap -- the statistically correct
          choice, since overlapping forward windows are heavily autocorrelated.
      (2) IS/OOS split. The halves are formed by computing PE/FwdVol on the FULL
          series, taking the 21-day sample, and splitting that sample at its midpoint.
    DESIGN.md section E4 documents the operator as actually run.

INPUTS
    The 11 core instruments pinned in data/SOURCES.md, from the project-local store
    (LT_DATA_DIR or the default in decomposition.py). Run data/pull.py first.

OUTPUT
    analysis/outputs/pe_volatility.json -- input hashes, per-instrument full/IS/OOS
    correlations, permutation results, Bonferroni summary. Plus a console report.

HOW TO RUN (PowerShell)
    cd <repo root>
    python analysis\\pe_volatility.py
    (requires: numpy, pandas, scipy)

OPERATORS (DESIGN.md section E4)
    Hull-50 displacement; PE_raw = rolling 63-day mean of x^2; PE = expanding
    percentile rank (min_history 252). FwdVol = std of the 21 forward daily returns,
    annualized by sqrt(252). Spearman on the 21-bar-spaced non-overlapping sample.
    Permutation seed 42. Battery: 11 full + 22 IS/OOS + 5 permutation = 38 tests;
    Bonferroni threshold 0.05/38.
"""
import json
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

# allow `from decomposition import ...` regardless of the working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decomposition import (load_prices, moving_average, sha256_of,
                           INSTRUMENT_FILES, INSTRUMENT_ORDER, DATA_DIR)

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "outputs", "pe_volatility.json")

# --------------------------------------------------------------------------
# Configuration (DESIGN.md E4)
# --------------------------------------------------------------------------
MA_SPEC = "Hull-50"          # displacement uses the Hull-50 MA
PE_WINDOW = 63               # rolling window for the mean of squared displacement
FWDVOL_WINDOW = 21           # forward realized-volatility window (trading days)
SPACING = FWDVOL_WINDOW      # sample spacing -> non-overlapping forward windows (D13)
MIN_HISTORY = 252            # min history for the expanding percentile rank
ANNUALIZE = np.sqrt(252)     # volatility annualization factor
N_PERM = 5000                # permutation iterations
SEED = 42                    # pre-registered seed
PERM_INSTRUMENTS = ["SPX", "NDX", "NI225", "GC", "CL"]   # 5 longest histories
BONFERRONI_N = 38            # 33 IS/OOS correlations + 5 permutation tests
BONFERRONI_THRESH = 0.05 / BONFERRONI_N


# --------------------------------------------------------------------------
# PE and forward volatility (DESIGN.md E4)
# --------------------------------------------------------------------------
def pe_and_fwdvol(logP):
    """Build the PE (displacement energy) and forward-volatility series for one path.

    PE:     x = logP - Hull50; PE_raw = rolling 63-day mean of x^2;
            PE = expanding percentile rank of PE_raw (min_history 252), in [0,100].
    FwdVol: std of the 21 forward daily returns r[t+1..t+21], annualized by sqrt(252).
    Returns (PE, FwdVol) as numpy arrays aligned to the logP bar index.
    """
    T = len(logP)
    MA = moving_average(logP, MA_SPEC)
    x = logP - MA

    # PE -- displacement energy
    pe_raw = pd.Series(x ** 2).rolling(PE_WINDOW).mean()
    PE = (pe_raw.expanding(min_periods=MIN_HISTORY).rank(pct=True) * 100.0).to_numpy()

    # FwdVol -- realized vol of the next 21 daily returns (purely forward, no overlap)
    d = np.diff(logP)                                  # d[i] = logP[i+1] - logP[i]
    roll = pd.Series(d).rolling(FWDVOL_WINDOW).std().to_numpy()   # roll[j]=std(d[j-20..j])
    fwd = np.full(T, np.nan)
    n_valid = len(d) - (FWDVOL_WINDOW - 1)
    if n_valid > 0:
        fwd[:n_valid] = roll[FWDVOL_WINDOW - 1:] * ANNUALIZE   # FwdVol[t]=std(d[t..t+20])
    return PE, fwd


def sampled_pairs(PE, fwd, spacing=SPACING):
    """Valid (PE, FwdVol) pairs, sampled every `spacing` bars (non-overlapping; D13)."""
    mask = ~(np.isnan(PE) | np.isnan(fwd))
    idx = np.where(mask)[0][::spacing]
    return PE[idx], fwd[idx]


def corr(pe_v, fwd_v):
    """Spearman rank correlation on an already-sampled pair of arrays."""
    if len(pe_v) < 30:
        return dict(rho=float("nan"), p=float("nan"), n=len(pe_v))
    rho, p = stats.spearmanr(pe_v, fwd_v)
    return dict(rho=float(rho), p=float(p), n=int(len(pe_v)))


def correlation_full_is_oos(logP):
    """Full-sample, in-sample-half and out-of-sample-half Spearman correlations.

    Per the procedure actually run (prior discrepancy D13): PE and FwdVol are computed
    on the FULL series, the non-overlapping 21-day sample is taken, and that sample is
    split at its midpoint to form the in-sample and out-of-sample halves.
    """
    PE, fwd = pe_and_fwdvol(logP)
    pe_v, fwd_v = sampled_pairs(PE, fwd)
    m = len(pe_v) // 2
    return dict(full=corr(pe_v, fwd_v),
                is_half=corr(pe_v[:m], fwd_v[:m]),
                oos_half=corr(pe_v[m:], fwd_v[m:]))


# --------------------------------------------------------------------------
# Permutation test -- 5,000 shuffles of PE against fixed FwdVol
# --------------------------------------------------------------------------
def permutation_test(logP, n_perm=N_PERM, seed=SEED):
    """Permutation p-value: fraction of shuffled correlations exceeding the real one.

    Runs on the same non-overlapping 21-day sample as the main correlation (D13).
    Spearman rho equals the Pearson correlation of the rank vectors, so each shuffle
    is a fast rank-vector dot product rather than a fresh spearmanr call.
    """
    PE, fwd = pe_and_fwdvol(logP)
    pe_v, fwd_v = sampled_pairs(PE, fwd)

    r_pe = stats.rankdata(pe_v)
    r_fv = stats.rankdata(fwd_v)
    z_pe = (r_pe - r_pe.mean()) / r_pe.std()
    z_fv = (r_fv - r_fv.mean()) / r_fv.std()
    real_rho = float(np.mean(z_pe * z_fv))             # = Spearman rho

    np.random.seed(seed)
    shuffled = np.empty(n_perm)
    for i in range(n_perm):
        shuffled[i] = np.mean(np.random.permutation(z_pe) * z_fv)
    exceed = int((shuffled > real_rho).sum())
    return dict(rho=real_rho, n=int(len(pe_v)), exceed=exceed, n_perm=n_perm,
                shuffled_max=float(shuffled.max()), shuffled_mean=float(shuffled.mean()),
                p_perm=exceed / n_perm,
                p_report=(exceed / n_perm if exceed > 0 else 1.0 / n_perm))


# --------------------------------------------------------------------------
# Runner -> JSON
# --------------------------------------------------------------------------
def main():
    prices, input_hashes = {}, {}
    for inst, fn in INSTRUMENT_FILES.items():
        path = os.path.join(DATA_DIR, fn)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{inst}: {path} not found. Set LT_DATA_DIR or see data/SOURCES.md.")
        input_hashes[inst] = {"file": fn, "sha256": sha256_of(path)}
        prices[inst] = load_prices(path)

    print("=" * 92)
    print("E4 -- PE-VOLATILITY CORRELATION (DESIGN.md E4)")
    print(f"displacement MA: {MA_SPEC}; PE window {PE_WINDOW}d; forward vol "
          f"{FWDVOL_WINDOW}d; non-overlapping sampling every {SPACING} bars (D13)")
    print("=" * 92)

    rows = []
    print(f"\n{'Instrument':<11}{'rho(full)':>11}{'p(full)':>12}"
          f"{'rho(IS)':>10}{'rho(OOS)':>11}{'n(full)':>10}")
    print("-" * 92)
    for inst in INSTRUMENT_ORDER:
        c = correlation_full_is_oos(prices[inst])
        rows.append(dict(instrument=inst,
                          rho_full=c["full"]["rho"], p_full=c["full"]["p"],
                          n_full=c["full"]["n"],
                          rho_is=c["is_half"]["rho"], p_is=c["is_half"]["p"],
                          rho_oos=c["oos_half"]["rho"], p_oos=c["oos_half"]["p"]))
        print(f"{inst:<11}{c['full']['rho']:>+11.3f}{c['full']['p']:>12.2e}"
              f"{c['is_half']['rho']:>+10.3f}{c['oos_half']['rho']:>+11.3f}"
              f"{c['full']['n']:>10d}")

    rho_full = np.array([r["rho_full"] for r in rows])
    print("-" * 92)
    print(f"Full-sample rho: mean {rho_full.mean():+.3f}, "
          f"min {rho_full.min():+.3f}, max {rho_full.max():+.3f}")
    n_pos = int((rho_full > 0).sum())
    sign_p = float(2.0 * stats.binom.cdf(min(n_pos, 11 - n_pos), 11, 0.5))
    print(f"Sign test: {n_pos}/11 positive, two-sided p = {sign_p:.5f}")

    # the 33 IS/OOS correlation tests
    p33 = np.array([r["p_full"] for r in rows] + [r["p_is"] for r in rows]
                   + [r["p_oos"] for r in rows])
    print(f"\n33 Spearman tests (full+IS+OOS): max p = {np.nanmax(p33):.2e}")

    # permutation tests on the 5 longest instruments
    print(f"\nPermutation tests ({N_PERM} shuffles, seed {SEED}):")
    print(f"  {'Instrument':<11}{'rho':>9}{'n':>8}{'shuffled max':>15}"
          f"{'# exceed real':>16}{'p':>11}")
    print("  " + "-" * 70)
    perm_rows = []
    for inst in PERM_INSTRUMENTS:
        pr = permutation_test(prices[inst])
        perm_rows.append(dict(instrument=inst, **pr))
        ptxt = f"<{1.0/N_PERM:.4f}" if pr["exceed"] == 0 else f"{pr['p_perm']:.4f}"
        print(f"  {inst:<11}{pr['rho']:>+9.3f}{pr['n']:>8d}"
              f"{pr['shuffled_max']:>+15.3f}{pr['exceed']:>16d}{ptxt:>11}")

    # Bonferroni summary
    all_p = list(p33) + [pr["p_report"] for pr in perm_rows]
    n_below = int(np.sum(np.array(all_p) < BONFERRONI_THRESH))
    print(f"\nBonferroni: {BONFERRONI_N} tests, threshold 0.05/{BONFERRONI_N} = "
          f"{BONFERRONI_THRESH:.5f}")
    print(f"  {n_below} of {BONFERRONI_N} tests significant after correction.")

    summary = {
        "rho_full_mean": round(float(rho_full.mean()), 3),
        "rho_full_min": round(float(rho_full.min()), 3),
        "rho_full_max": round(float(rho_full.max()), 3),
        "n_positive_of_11": n_pos,
        "sign_test_p": sign_p,
        "bonferroni_n": BONFERRONI_N,
        "bonferroni_threshold": BONFERRONI_THRESH,
        "n_significant_after_bonferroni": n_below,
    }

    result = {
        "experiment": "E4_pe_volatility",
        "design_ref": "DESIGN.md section E4",
        "params": {"ma_spec": MA_SPEC, "pe_window": PE_WINDOW,
                   "fwdvol_window": FWDVOL_WINDOW, "spacing": SPACING,
                   "min_history": MIN_HISTORY, "n_perm": N_PERM, "seed": SEED,
                   "perm_instruments": PERM_INSTRUMENTS,
                   "bonferroni_n": BONFERRONI_N},
        "inputs": input_hashes,
        "rows": rows,
        "permutation_rows": perm_rows,
        "summary": summary,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="\n") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"\nWritten: {OUT_PATH}")
    return result


if __name__ == "__main__":
    main()
