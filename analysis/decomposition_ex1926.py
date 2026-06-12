"""
decomposition_ex1926.py -- A4: the registered ex-1926 decomposition variant
(DESIGN.md amendment 2026-06-11, item A4).

"Moving Averages Follow Price" -- Research-to-Publication Standard (review-born
follow-up under the v1.4 gated-fix rule; closes the future-work note in the
paper's Section 4.1: the SPX series before 1926 derives from a reconstructed
monthly-bar historical index, and the published full-series results treat those
bars as consecutive daily bars).

WHAT IT DOES
    Re-runs the E1 gap-closure decomposition on SPX restricted to bars dated
    1926-01-01 or later (dropping the monthly-reconstruction era entirely), for
    all four MA specifications, with operators identical to E1 (H=63, expanding
    75th-percentile threshold, min_history=252, non-overlapping events). The
    full-series SPX rows are recomputed in the same run from the same input file
    for a like-for-like comparison, and per-spec deltas are reported.

    Note the variant is not merely a row-subset of the full run: dropping the
    early era changes the expanding threshold's path and the event chain, so all
    four cells are recomputed from scratch -- which is the point.

INPUTS
    The SPX daily CSV pinned in data/SOURCES.md (project-local store).

OUTPUT
    analysis/outputs/decomposition_ex1926.json

HOW TO RUN (PowerShell)
    cd <repo root>
    python analysis\\decomposition_ex1926.py
    (requires: numpy, pandas)
"""
import json
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decomposition import (moving_average, decompose, sha256_of,
                           INSTRUMENT_FILES, DATA_DIR, MA_SPECS,
                           H, THRESHOLD_PCT, MIN_HISTORY)

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "outputs", "decomposition_ex1926.json")

CUTOFF = "1926-01-01"      # registered cutoff (paper Section 4.1)
INSTRUMENT = "SPX"


def load_prices_with_dates(path):
    """E1's loader (decomposition.load_prices), step for step, but keeping dates.

    Same schema tolerance (columns by name, mixed ISO/US date formats), same
    close>0 filter, same sort. Returns (dates: DatetimeIndex-like Series,
    logP: np.ndarray) aligned.
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if "time" not in df.columns or "close" not in df.columns:
        raise ValueError(f"{path}: expected 'time' and 'close' columns, "
                         f"got {list(df.columns)}")
    dt = pd.to_datetime(df["time"], format="mixed", errors="coerce")
    close = pd.to_numeric(df["close"], errors="coerce")
    out = pd.DataFrame({"date": dt, "close": close}).dropna()
    out = out[out["close"] > 0]
    out = out.sort_values("date").reset_index(drop=True)
    return out["date"], np.log(out["close"].to_numpy())


def run_all_specs(logP):
    rows = {}
    for spec in MA_SPECS:
        MA = moving_average(logP, spec)
        rows[spec] = decompose(logP, MA)
    return rows


def main():
    path = os.path.join(DATA_DIR, INSTRUMENT_FILES[INSTRUMENT])
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{INSTRUMENT}: {path} not found. Set LT_DATA_DIR or see data/SOURCES.md.")
    input_hash = {"file": INSTRUMENT_FILES[INSTRUMENT], "sha256": sha256_of(path)}

    dates, logP_full = load_prices_with_dates(path)
    cutoff = pd.Timestamp(CUTOFF)
    mask = (dates >= cutoff).to_numpy()
    logP_var = logP_full[mask]

    print("=" * 90)
    print("A4 -- EX-1926 DECOMPOSITION VARIANT, SPX "
          "(DESIGN.md amendment 2026-06-11)")
    print(f"operators identical to E1: H={H}, threshold={THRESHOLD_PCT}th pctile, "
          f"min_history={MIN_HISTORY}")
    print("=" * 90)
    print(f"Full series:    {len(logP_full):>6d} bars, "
          f"{dates.iloc[0].date()} .. {dates.iloc[-1].date()}")
    print(f"Ex-1926 series: {len(logP_var):>6d} bars, first retained bar "
          f"{dates[mask].iloc[0].date()} ({len(logP_full)-len(logP_var)} dropped)")

    full = run_all_specs(logP_full)
    var = run_all_specs(logP_var)

    print(f"\n{'MA Spec':<10}{'full agg%':>11}{'ex26 agg%':>11}{'delta pp':>10}"
          f"{'full n':>8}{'ex26 n':>8}{'ex26>50%':>10}")
    print("-" * 90)
    rows = []
    crossings = []
    for spec in MA_SPECS:
        f, v = full[spec], var[spec]
        d_pp = (v["agg"] - f["agg"]) * 100.0
        above = bool(v["agg"] > 0.5)
        if (f["agg"] > 0.5) != above:
            crossings.append(spec)
        rows.append(dict(ma_spec=spec,
                         full=dict(agg=f["agg"], n=f["n"], median=f["median"],
                                   mean=f["mean"]),
                         ex1926=dict(agg=v["agg"], n=v["n"], median=v["median"],
                                     mean=v["mean"]),
                         delta_agg_pp=round(float(d_pp), 2),
                         ex1926_above_50=above))
        print(f"{spec:<10}{f['agg']*100:>11.1f}{v['agg']*100:>11.1f}{d_pp:>+10.2f}"
              f"{f['n']:>8d}{v['n']:>8d}{('YES' if above else 'NO'):>10}")

    print("-" * 90)
    if crossings:
        print(f"50% CROSSINGS between full and ex-1926: {crossings}  <-- report prominently")
    else:
        print("No SPX cell crosses the 50% line between the full and ex-1926 variants.")

    summary = {
        "cutoff": CUTOFF,
        "bars_full": int(len(logP_full)),
        "bars_ex1926": int(len(logP_var)),
        "bars_dropped": int(len(logP_full) - len(logP_var)),
        "first_retained_bar": str(dates[mask].iloc[0].date()),
        "max_abs_delta_pp": round(float(max(abs(r["delta_agg_pp"]) for r in rows)), 2),
        "all_ex1926_above_50": bool(all(r["ex1926_above_50"] for r in rows)),
        "crossings": crossings,
    }

    result = {
        "experiment": "A4_decomposition_ex1926",
        "design_ref": "DESIGN.md amendment 2026-06-11 (A4)",
        "params": {"instrument": INSTRUMENT, "cutoff": CUTOFF, "H": H,
                   "threshold_pct": THRESHOLD_PCT, "min_history": MIN_HISTORY,
                   "ma_specs": MA_SPECS},
        "inputs": {INSTRUMENT: input_hash},
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
