"""
schelling_point.py -- E5: the Schelling Point test (DESIGN.md section E5; B.7).

"Moving Averages Follow Price" -- Research-to-Publication Standard v1.2, Phase 2.
Built 2026-06-09. The prior iteration's reconstruction covered the daily slice
only; this script implements all four timeframes per B.7. Input files pinned and
workbook-verified per the DESIGN.md amendments of 2026-06-09 (the per-combination
engine below reproduced the original workbook's rows on every timeframe before
this script was assembled).

WHAT IT DOES
    If self-fulfilling prophecy drives price-MA convergence, POPULAR SMA windows
    (20, 50, 100, 200) should show higher next-bar toward rates than arbitrary
    NEIGHBOR windows (W-5, W-3, W+3, W+5). The Schelling premium for a popular
    window is delta_W = toward_rate(W) - mean(toward_rate of the 4 neighbors).
    The null (no Schelling effect) predicts delta ~ 0. The test runs across four
    timeframes and reports one-sample t, Wilcoxon signed-rank, and sign tests on
    the included deltas.

INPUTS (data/SOURCES.md; run data/pull.py first)
    Daily (13):   the 11 core instruments with NDX replaced by NQ, plus ES, NKD.
    Hourly (12):  all daily instruments except SPX (no hourly history).
    5-minute (8): ES, NQ, GC, CL, ZN, 6E, 6J, NKD.
    Monthly (2):  SPX, GC.

OUTPUT
    analysis/outputs/schelling_point.json -- input hashes, every
    instrument x timeframe x window combination (toward rates, neighbor rates,
    delta, inclusion), per-window / per-timeframe / overall statistics. Plus a
    console report.

HOW TO RUN (PowerShell)
    cd <repo root>
    python analysis\\schelling_point.py
    (requires: numpy, pandas, scipy; runtime a few minutes)

OPERATORS (DESIGN.md E5; B.7)
    Popular windows W in {20, 50, 100, 200}; neighbors {W-5, W-3, W+3, W+5}.
    For each SMA window: x = logP - SMA_W; tau = expanding 75th percentile of |x|
    (no look-ahead); EVERY qualifying bar (|x| > tau, no spacing) contributes;
    toward = next bar moves toward the MA. min_history by timeframe: daily 252,
    hourly 500, 5-minute 2,000, monthly 60. A combination is included only if the
    popular window AND all four neighbors have >= 200 qualifying events.
    Statistics on included deltas: one-sample t-test (H0: mean delta = 0),
    Wilcoxon signed-rank, sign test (two-sided binomial); one-sided p
    (H1: popular higher) also reported for comparability with the original
    workbook.

LOADER NOTE
    Intraday TradingView exports carry mixed UTC offsets (DST transitions), which
    the committed daily loader (decomposition.load_prices) rejects; and some
    daily exports (e.g. SPX) mix ISO and US date formats within one column,
    which a bare utc=True parse silently coerces to NaT. This script therefore
    parses with format="mixed" AND utc=True; on the daily files this yields the
    byte-identical price sequence to the committed loader (verified).
"""
import json
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decomposition import sha256_of, DATA_DIR

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "outputs", "schelling_point.json")

# --------------------------------------------------------------------------
# Configuration (DESIGN.md E5 / B.7)
# --------------------------------------------------------------------------
POPULAR = [20, 50, 100, 200]
NEIGHBOR_OFFSETS = [-5, -3, +3, +5]
THRESHOLD_PCT = 75
MIN_EVENTS = 200

TIMEFRAMES = {
    "1D": dict(min_history=252, files={
        "SPX":   "SP_SPX, 1D_5871b.csv",
        "NQ":    "CME_MINI_NQ1!, 1D_de2b2.csv",
        "NI225": "TVC_NI225, 1D_8be07.csv",
        "DAX":   "XETR_DLY_DAX, 1D_cd703.csv",
        "FTSE":  "IG_FTSE, 1D_c9679.csv",
        "HSI":   "HKEX_DLY_HSI1!, 1D_57a14.csv",
        "CL":    "NYMEX_CL1!, 1D_de4b1.csv",
        "GC":    "COMEX_GC1!, 1D_1e2f0.csv",
        "ZN":    "CBOT_ZN1!, 1D_3436b.csv",
        "6E":    "CME_6E1!, 1D_9dd8b.csv",
        "6J":    "CME_6J1!, 1D_01e58.csv",
        "ES":    "CME_MINI_ES1!, 1D_40b30.csv",
        "NKD":   "CME_NKD1!, 1D_92650.csv",
    }),
    "60": dict(min_history=500, files={
        "NQ":    "CME_MINI_NQ1!, 60_985ba.csv",
        "NI225": "TVC_NI225, 60_b5054.csv",
        "DAX":   "XETR_DLY_DAX, 60_82c16.csv",
        "FTSE":  "IG_FTSE, 60_6e958.csv",
        "HSI":   "HKEX_DLY_HSI1!, 60_7c166.csv",
        "CL":    "NYMEX_CL1!, 60_72c46.csv",
        "GC":    "COMEX_GC1!, 60_26eca.csv",
        "ZN":    "CBOT_ZN1!, 60_81641.csv",
        "6E":    "CME_6E1!, 60_df31a.csv",
        "6J":    "CME_6J1!, 60_5c795.csv",
        "ES":    "CME_MINI_ES1!, 60_127a6.csv",
        "NKD":   "CME_NKD1!, 60_ffee5.csv",
    }),
    "5": dict(min_history=2000, files={
        "ES":  "CME_MINI_ES1!, 5_28d89.csv",
        "NQ":  "CME_MINI_NQ1!, 5_c2781.csv",
        "GC":  "COMEX_GC1!, 5_f87e8.csv",
        "CL":  "NYMEX_CL1!, 5_a29b4.csv",
        "ZN":  "CBOT_ZN1!, 5_bdc1e.csv",
        "6E":  "CME_6E1!, 5_d72d6.csv",
        "6J":  "CME_6J1!, 5_c0f96.csv",
        "NKD": "CME_NKD1!, 5_f1b66.csv",
    }),
    "1M": dict(min_history=60, files={
        "SPX": "SP_SPX, 1M_9ba20.csv",
        "GC":  "COMEX_GC1!, 1M_958cd.csv",
    }),
}


# --------------------------------------------------------------------------
# Loader (tz-safe; see LOADER NOTE in the docstring)
# --------------------------------------------------------------------------
def load_prices_tz(path):
    """TradingView CSV -> numpy array of log close prices, tz-mixed-safe."""
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if "time" not in df.columns or "close" not in df.columns:
        raise ValueError(f"{path}: expected 'time' and 'close' columns")
    dt = pd.to_datetime(df["time"], format="mixed", utc=True, errors="coerce")
    close = pd.to_numeric(df["close"], errors="coerce")
    out = pd.DataFrame({"date": dt, "close": close}).dropna()
    out = out[out["close"] > 0]
    out = out.sort_values("date").reset_index(drop=True)
    return np.log(out["close"].to_numpy())


# --------------------------------------------------------------------------
# Toward rate (B.7; engine verified against the original workbook)
# --------------------------------------------------------------------------
def toward_rate(logP, window, min_history, pct=THRESHOLD_PCT):
    """Next-bar toward rate for one SMA window: ALL qualifying bars, no spacing.

      x[t] = logP[t] - SMA_window[t]
      tau[t] = expanding pct-percentile of |x| through t (no look-ahead)
      qualifying: |x[t]| > tau[t] and t+1 < T
      toward: x>0 and next return < 0, or x<0 and next return > 0
    Returns (rate_pct, n_events).
    """
    sma = pd.Series(logP).rolling(window).mean().to_numpy()
    x = logP - sma
    abs_x = pd.Series(np.abs(x))
    tau = abs_x.expanding(min_periods=min_history).quantile(pct / 100.0).to_numpy()
    toward = total = 0
    for t in range(len(logP) - 1):
        if np.isnan(tau[t]) or np.isnan(x[t]):
            continue
        if abs_x[t] > tau[t]:
            nr = logP[t + 1] - logP[t]
            if (x[t] > 0 and nr < 0) or (x[t] < 0 and nr > 0):
                toward += 1
            total += 1
    return (100.0 * toward / total if total else float("nan")), int(total)


def schelling_for_instrument(logP, min_history):
    """All popular-window combinations for one instrument-timeframe price path."""
    windows = sorted({W + o for W in POPULAR for o in [0] + NEIGHBOR_OFFSETS})
    rate, n = {}, {}
    for w in windows:
        rate[w], n[w] = toward_rate(logP, w, min_history)
    out = []
    for W in POPULAR:
        nbrs = [W + o for o in NEIGHBOR_OFFSETS]
        included = (n[W] >= MIN_EVENTS) and all(n[w] >= MIN_EVENTS for w in nbrs)
        nbr_rates = [rate[w] for w in nbrs]
        delta = rate[W] - float(np.mean(nbr_rates)) if included else float("nan")
        out.append(dict(window=f"SMA-{W}", n=n[W], rate_popular=rate[W],
                        neighbor_rates={f"SMA-{w}": rate[w] for w in nbrs},
                        neighbor_ns={f"SMA-{w}": n[w] for w in nbrs},
                        mean_neighbor_rate=float(np.mean(nbr_rates)),
                        delta_pp=delta, included=bool(included)))
    return out


# --------------------------------------------------------------------------
# Statistics on a set of deltas
# --------------------------------------------------------------------------
def delta_stats(deltas):
    d = np.asarray(deltas, dtype=float)
    d = d[~np.isnan(d)]
    if len(d) < 2:
        return dict(n=int(len(d)), mean=float(np.mean(d)) if len(d) else float("nan"))
    t, p_two = stats.ttest_1samp(d, 0.0)
    p_one = p_two / 2.0 if t > 0 else 1.0 - p_two / 2.0   # H1: popular higher
    try:
        w_stat, w_p = stats.wilcoxon(d)
    except ValueError:
        w_stat, w_p = float("nan"), float("nan")
    n_pos = int((d > 0).sum())
    sign_p = float(2.0 * stats.binom.cdf(min(n_pos, len(d) - n_pos), len(d), 0.5))
    return dict(n=int(len(d)), mean=float(d.mean()), median=float(np.median(d)),
                sd=float(d.std(ddof=1)), t=float(t), p_two_sided=float(p_two),
                p_one_sided_popular_higher=float(p_one),
                wilcoxon_stat=float(w_stat), wilcoxon_p=float(w_p),
                n_positive=n_pos, sign_test_p=sign_p)


# --------------------------------------------------------------------------
# Runner -> JSON
# --------------------------------------------------------------------------
def main():
    rows, input_hashes = [], {}
    tf_names = {"1D": "Daily", "60": "Hourly", "5": "5-Minute", "1M": "Monthly"}

    print("=" * 92)
    print("E5 -- SCHELLING POINT TEST (DESIGN.md E5; B.7)")
    print(f"popular {POPULAR}; neighbors W-5,W-3,W+3,W+5; threshold P{THRESHOLD_PCT}; "
          f"inclusion >= {MIN_EVENTS} events (popular AND all neighbors)")
    print("=" * 92)

    for tf, cfg in TIMEFRAMES.items():
        mh = cfg["min_history"]
        print(f"\n[{tf_names[tf]}]  min_history = {mh}")
        print(f"  {'Inst':<7}{'Window':<9}{'N':>7}{'Pop%':>8}{'NbrMean%':>10}"
              f"{'Delta(pp)':>11}{'Incl':>6}")
        print("  " + "-" * 56)
        for inst, fn in cfg["files"].items():
            path = os.path.join(DATA_DIR, fn)
            if not os.path.exists(path):
                raise FileNotFoundError(f"{inst}.{tf}: {path} not found.")
            input_hashes[f"{inst}.{tf}"] = {"file": fn, "sha256": sha256_of(path)}
            logP = load_prices_tz(path)
            for c in schelling_for_instrument(logP, mh):
                rows.append(dict(instrument=inst, timeframe=tf, **c))
                d = f"{c['delta_pp']:+.4f}" if c["included"] else "   --"
                print(f"  {inst:<7}{c['window']:<9}{c['n']:>7}{c['rate_popular']:>8.2f}"
                      f"{c['mean_neighbor_rate']:>10.2f}{d:>11}"
                      f"{'yes' if c['included'] else 'NO':>6}")

    included = [r for r in rows if r["included"]]
    deltas_all = [r["delta_pp"] for r in included]

    overall = delta_stats(deltas_all)
    by_window = {f"SMA-{W}": delta_stats([r["delta_pp"] for r in included
                                          if r["window"] == f"SMA-{W}"])
                 for W in POPULAR}
    by_timeframe = {tf_names[tf]: delta_stats([r["delta_pp"] for r in included
                                               if r["timeframe"] == tf])
                    for tf in TIMEFRAMES}

    print("\n" + "=" * 92)
    print("SUMMARY")
    print("=" * 92)
    print(f"Combinations evaluated: {len(rows)}; included (>= {MIN_EVENTS} events "
          f"on popular and all neighbors): {len(included)}; "
          f"excluded: {len(rows) - len(included)}")
    o = overall
    print(f"Overall delta: mean {o['mean']:+.4f} pp, median {o['median']:+.4f}, "
          f"t = {o['t']:+.3f}, p(two-sided) = {o['p_two_sided']:.4f}, "
          f"p(one-sided, popular higher) = {o['p_one_sided_popular_higher']:.4f}")
    print(f"Wilcoxon p = {o['wilcoxon_p']:.4f}; sign: {o['n_positive']}/{o['n']} "
          f"positive (p = {o['sign_test_p']:.4f})")
    print("\nBy timeframe:")
    for k, s in by_timeframe.items():
        if s["n"]:
            print(f"  {k:<10} n={s['n']:<4} mean {s['mean']:+.4f} pp  "
                  f"t {s['t']:+.3f}  p1s {s['p_one_sided_popular_higher']:.4f}")
    print("\nBy window:")
    for k, s in by_window.items():
        print(f"  {k:<9} n={s['n']:<4} mean {s['mean']:+.4f} pp  "
              f"t {s['t']:+.3f}  p1s {s['p_one_sided_popular_higher']:.4f}")
    verdict = "NULL CONFIRMED" if o["p_two_sided"] > 0.05 else "EFFECT DETECTED"
    print(f"\nVerdict: {verdict} -- no detectable Schelling-point premium."
          if o["p_two_sided"] > 0.05 else f"\nVerdict: {verdict}.")

    result = {
        "experiment": "E5_schelling_point",
        "design_ref": "DESIGN.md section E5; B.7",
        "params": {"popular_windows": POPULAR,
                   "neighbor_offsets": NEIGHBOR_OFFSETS,
                   "threshold_pct": THRESHOLD_PCT, "min_events": MIN_EVENTS,
                   "min_history": {tf: cfg["min_history"]
                                   for tf, cfg in TIMEFRAMES.items()}},
        "inputs": input_hashes,
        "rows": rows,
        "summary": {
            "n_evaluated": len(rows),
            "n_included": len(included),
            "overall": overall,
            "by_window": by_window,
            "by_timeframe": by_timeframe,
        },
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="\n") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"\nWritten: {OUT_PATH}")
    return result


if __name__ == "__main__":
    main()
