"""
direction_test.py -- E2: the next-bar direction test (DESIGN.md section E2).

"Moving Averages Follow Price" -- Research-to-Publication Standard v1.2, Phase 2.
Ported 2026-06-09 from the prior iteration's verified reconstruction (see
DECISIONS.md); operators unchanged.

WHAT IT DOES
    The decomposition (decomposition.py) measures who closes the price-MA gap. The
    direction test asks a narrower, complementary question: at a displacement event,
    does the NEXT bar's price move tend to go toward the moving average or away from
    it? Under zero attraction and zero drift the "toward rate" should be 50%. A toward
    rate significantly above 50% would indicate genuine attraction; below 50%,
    repulsion. Unlike the decomposition, the direction test enforces no spacing --
    every qualifying bar is tested independently.

    A drift-adjusted variant replaces the 50% null with a drift-aware null: a long-only
    asset with positive drift moves up more often than down, which biases the raw
    toward rate, so the adjusted test compares against the drift-implied null instead.

INPUTS
    The 11 core instruments pinned in data/SOURCES.md, from the project-local store
    (LT_DATA_DIR or the default in decomposition.py). Run data/pull.py first.

OUTPUT
    analysis/outputs/direction_test.json -- input hashes, per-combination rows
    (toward rate, events, z, p, drift-adjusted z/p), and a summary. Plus a console
    table.

HOW TO RUN (PowerShell)
    cd <repo root>
    python analysis\\direction_test.py
    (requires: numpy, pandas, scipy)

OPERATORS (DESIGN.md section E2)
    Same displacement x and expanding 75th-percentile threshold as E1 (no look-ahead),
    min_history = 252, but EVERY qualifying bar is tested (no non-overlap spacing).
    Specs: Hull-50 and SMA-200. Plain z against the 0.5 null; drift-adjusted z against
    p_null = f_above*(1 - p_up) + (1 - f_above)*p_up.
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
                        "outputs", "direction_test.json")

# --------------------------------------------------------------------------
# Configuration (DESIGN.md E2)
# --------------------------------------------------------------------------
THRESHOLD_PCT = 75       # expanding percentile for "substantial deviation"
MIN_HISTORY = 252        # bars before events may be selected (~1 trading year)
DIRECTION_SPECS = ["Hull-50", "SMA-200"]   # the two specs the paper reports


# --------------------------------------------------------------------------
# Direction test (DESIGN.md E2)
# --------------------------------------------------------------------------
def direction_test(logP, MA, pct=THRESHOLD_PCT, min_hist=MIN_HISTORY):
    """Next-bar direction test for one instrument-filter combination.

      x[t]   = logP[t] - MA[t]
      tau[t] = expanding pct-percentile of |x| through t (no look-ahead, as in E1)
      qualifying bar: |x[t]| > tau[t] AND t+1 < T  (NO non-overlapping spacing)
      toward: x[t] > 0 and next return < 0, or x[t] < 0 and next return > 0
      z = (toward - 0.5*total) / sqrt(0.25*total);  p = 2*(1 - Phi(|z|))

    Drift-adjusted test: the 0.5 null is replaced by a drift-implied null
      p_up   = fraction of all daily returns that are positive
      p_null = f_above*(1 - p_up) + (1 - f_above)*p_up
    where f_above is the fraction of qualifying events with x[t] > 0.
    """
    x = logP - MA
    abs_x = pd.Series(np.abs(x))
    tau = abs_x.expanding(min_periods=min_hist).quantile(pct / 100.0).to_numpy()

    T = len(logP)
    toward = 0
    total = 0
    n_above = 0
    for t in range(T - 1):                       # t+1 < T
        if np.isnan(tau[t]) or np.isnan(x[t]):
            continue
        if abs_x[t] > tau[t]:
            nr = logP[t + 1] - logP[t]           # next-bar log return
            if x[t] > 0:
                n_above += 1
                if nr < 0:                       # price moved down, toward the MA
                    toward += 1
            elif x[t] < 0:
                if nr > 0:                       # price moved up, toward the MA
                    toward += 1
            total += 1

    if total == 0:
        return dict(toward=0, total=0, rate=float("nan"), z=float("nan"),
                    p=float("nan"), z_adj=float("nan"), p_adj=float("nan"),
                    p_null=float("nan"), f_above=float("nan"))

    rate = toward / total
    # plain test against the 0.5 null
    z = (toward - 0.5 * total) / np.sqrt(0.25 * total)
    p = 2.0 * (1.0 - stats.norm.cdf(abs(z)))

    # drift-adjusted test
    r_all = np.diff(logP)
    p_up = float((r_all > 0).mean())
    f_above = n_above / total
    p_null = f_above * (1.0 - p_up) + (1.0 - f_above) * p_up
    z_adj = (toward - p_null * total) / np.sqrt(total * p_null * (1.0 - p_null))
    p_adj = 2.0 * (1.0 - stats.norm.cdf(abs(z_adj)))

    return dict(toward=int(toward), total=int(total), rate=float(rate),
                z=float(z), p=float(p), z_adj=float(z_adj), p_adj=float(p_adj),
                p_null=float(p_null), f_above=float(f_above))


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

    rows = []
    for inst in INSTRUMENT_ORDER:
        logP = prices[inst]
        for spec in DIRECTION_SPECS:
            MA = moving_average(logP, spec)
            r = direction_test(logP, MA)
            rows.append(dict(instrument=inst, ma_spec=spec, **r))

    print("=" * 92)
    print("E2 -- NEXT-BAR DIRECTION TEST (DESIGN.md E2)")
    print(f"threshold={THRESHOLD_PCT}th pctile, min_history={MIN_HISTORY}, "
          f"no spacing; specs: {', '.join(DIRECTION_SPECS)}")
    print("=" * 92)

    summary = {}
    for spec in DIRECTION_SPECS:
        sub = [r for r in rows if r["ma_spec"] == spec]
        print(f"\n[{spec}]")
        print(f"  {'Instrument':<11}{'Toward%':>9}{'Events':>9}{'z':>8}{'p':>10}"
              f"{'z_adj':>10}{'p_adj':>10}{'  flag':>9}")
        print("  " + "-" * 86)
        for r in sub:
            direction = ""
            if r["p"] < 0.05:
                direction = "attract" if r["rate"] > 0.5 else "repel"
            sig_adj = "*" if (not np.isnan(r["p_adj"]) and r["p_adj"] < 0.05) else "-"
            print(f"  {r['instrument']:<11}{r['rate']*100:>9.1f}{r['total']:>9d}"
                  f"{r['z']:>8.2f}{r['p']:>10.4f}{r['z_adj']:>10.2f}{r['p_adj']:>10.4f}"
                  f"{('  ' + direction) if direction else '  -':>9}{'  ' + sig_adj}")
        n_sig = sum(1 for r in sub if r["p"] < 0.05)
        near50 = sum(1 for r in sub if r["p"] >= 0.05)
        n_sig_adj = sum(1 for r in sub if (not np.isnan(r["p_adj"])) and r["p_adj"] < 0.05)
        print(f"  -> {near50} of {len(sub)} indistinguishable from 50%; "
              f"{n_sig} significant at p<0.05 (plain); {n_sig_adj} after drift adjustment.")
        summary[spec] = {"near_50": near50, "significant_plain": n_sig,
                         "significant_drift_adjusted": n_sig_adj}

    result = {
        "experiment": "E2_direction_test",
        "design_ref": "DESIGN.md section E2",
        "params": {"threshold_pct": THRESHOLD_PCT, "min_history": MIN_HISTORY,
                   "ma_specs": DIRECTION_SPECS, "instruments": INSTRUMENT_ORDER},
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
