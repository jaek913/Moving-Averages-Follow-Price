"""
quarterly_reversion.py -- E6: the quarterly-reversion test (DESIGN.md section E6).

"Moving Averages Follow Price" -- Research-to-Publication Standard v1.2, Phase 2.
Ported 2026-06-09 from the prior iteration's verified reconstruction (see
DECISIONS.md); operators unchanged.

WHAT IT DOES
    The thesis is that price-MA convergence is mostly mechanical. This test is the
    honest qualification: at quarterly-and-longer horizons the S&P 500 does show
    genuine mean reversion, measured in a way the mechanical adaptation cannot
    manufacture. The test divides the price history into strictly non-overlapping
    blocks of H trading days; for each block it records the signed displacement from
    the Hull-50 MA at the block's start and the block's own forward return; and it
    correlates the two across blocks. A negative correlation means "far above the
    average -> lower forward return" -- genuine reversion. Strictly non-overlapping
    blocks are what make this distinct from the mechanical effect: consecutive
    observations share no data, so no filter artifact links them.

    Run on SPX at four horizons (H = 21, 63, 126, 252 trading days) and, as a
    specificity check, on the Nikkei 225 and gold.

INPUTS
    SPX, NI225, GC daily CSVs pinned in data/SOURCES.md (project-local store;
    LT_DATA_DIR or the default in decomposition.py). Run data/pull.py first.

OUTPUT
    analysis/outputs/quarterly_reversion.json -- input hashes, per-instrument
    per-horizon r / t / p / n. Plus a console report.

HOW TO RUN (PowerShell)
    cd <repo root>
    python analysis\\quarterly_reversion.py
    (requires: numpy, pandas, scipy)

OPERATORS (DESIGN.md section E6)
    Displacement x = logP - Hull50. Blocks start at the first valid Hull-50 bar and
    step by H (strictly non-overlapping); each block contributes (x at block start,
    logP[start+H] - logP[start]). Pearson r across blocks; t = r*sqrt(n-2)/sqrt(1-r^2);
    two-sided p. H in {21, 63, 126, 252}.
"""
import json
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decomposition import load_prices, hma, sha256_of, DATA_DIR

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "outputs", "quarterly_reversion.json")

HORIZONS = [21, 63, 126, 252]

INSTRUMENT_FILES = {
    "SPX":   "SP_SPX, 1D_5871b.csv",
    "NI225": "TVC_NI225, 1D_8be07.csv",
    "GC":    "COMEX_GC1!, 1D_1e2f0.csv",
}


def quarterly_reversion(logP, H):
    """Non-overlapping displacement / forward-return correlation at horizon H.

    Displacement x = logP - Hull50; blocks start at the first valid Hull-50 bar and
    step by H; each block contributes (x at block start, logP[start+H] - logP[start]).
    Returns (r, t_stat, p_value, n_blocks).
    """
    logP = np.asarray(logP, dtype=float)
    hull = hma(logP, 50)
    x = logP - hull
    T = len(logP)
    first = int(np.argmax(~np.isnan(x)))               # first valid Hull-50 bar

    starts = range(first, T - H, H)                    # non-overlapping block starts
    disp, fwd = [], []
    for t in starts:
        if np.isnan(x[t]):
            continue
        disp.append(x[t])
        fwd.append(logP[t + H] - logP[t])
    disp, fwd = np.asarray(disp), np.asarray(fwd)
    n = len(disp)
    r, p = stats.pearsonr(disp, fwd)
    t_stat = r * np.sqrt(n - 2) / np.sqrt(1 - r ** 2)
    return float(r), float(t_stat), float(p), int(n)


def main():
    print("=" * 84)
    print("E6 -- QUARTERLY-REVERSION TEST (DESIGN.md E6)")
    print(f"Hull-50 displacement; strictly non-overlapping blocks; horizons {HORIZONS}")
    print("=" * 84)

    rows, input_hashes = [], {}
    for inst, fname in INSTRUMENT_FILES.items():
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            raise FileNotFoundError(f"{inst}: {path} not found. Set LT_DATA_DIR.")
        input_hashes[inst] = {"file": fname, "sha256": sha256_of(path)}
        logP = load_prices(path)
        print(f"\n{inst}  ({len(logP)} bars)")
        print(f"  {'H':>5}{'n blocks':>10}{'r':>12}{'t-stat':>10}{'p-value':>12}")
        for H in HORIZONS:
            r, t_stat, p, n = quarterly_reversion(logP, H)
            rows.append(dict(instrument=inst, horizon=H, n=n, r=r,
                             t_stat=t_stat, p_value=p))
            print(f"  {H:>5}{n:>10}{r:>+12.4f}{t_stat:>+10.3f}{p:>12.6f}")

    spx = {r["horizon"]: r for r in rows if r["instrument"] == "SPX"}
    summary = {
        "spx_r_by_horizon": {str(H): round(spx[H]["r"], 4) for H in HORIZONS},
        "spx_p_by_horizon": {str(H): spx[H]["p_value"] for H in HORIZONS},
        "spx_significant_horizons_p_lt_05":
            [H for H in HORIZONS if spx[H]["p_value"] < 0.05],
        "specificity_significant_elsewhere":
            [f"{r['instrument']}@{r['horizon']}" for r in rows
             if r["instrument"] != "SPX" and r["p_value"] < 0.05],
    }

    print("\n" + "-" * 84)
    print("SPX summary:")
    for H in HORIZONS:
        print(f"  H={H:>3}  r = {spx[H]['r']:+.4f}  p = {spx[H]['p_value']:.6f}")
    print(f"Specificity (NI225/GC results with p < 0.05): "
          f"{summary['specificity_significant_elsewhere'] or 'none'}")

    result = {
        "experiment": "E6_quarterly_reversion",
        "design_ref": "DESIGN.md section E6",
        "params": {"ma": "Hull-50", "horizons": HORIZONS,
                   "instruments": list(INSTRUMENT_FILES.keys())},
        "inputs": input_hashes,
        "rows": rows,
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
