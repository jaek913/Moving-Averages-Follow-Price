"""
robustness.py -- E7: the consolidated robustness battery (DESIGN.md section E7,
as amended 2026-06-09; manuscript Sections 5.4-5.6; B.2, B.9, B.10, B.11).

"Moving Averages Follow Price" -- Research-to-Publication Standard v1.2, Phase 2.
Built 2026-06-09. The prior iteration never consolidated these analyses into a
committed script; this file makes every Section 5.4-5.6 number reproducible.

NINE SUB-BATTERIES (amended DESIGN E7)
    1. eight_spec      -- SPX, H=63: Hull-20/50/100, SMA-20/50/100/200, EMA-50.
    2. thresholds      -- SPX Hull-50, H=63: 50th / 75th / 90th percentile.
    3. horizons        -- robustness core 11, Hull-50: H = 21 / 63 / 126 / 252.
    4. filter_matched  -- robustness core 11 x 4 main specs at each filter's
                          convergence horizon (Hull-50:55, SMA-50:50, EMA-50:75,
                          SMA-200:200), compared to the same grid at H=63 (B.10).
    5. offsets         -- SPX Hull-50, H=63: all 63 starting offsets (the event
                          scan begins `offset` bars after min_history).
    6. log_vs_level    -- SPX, 4 main specs, H=63, on LEVEL prices (qualitative).
    7. eras            -- SPX Hull-50, H=63: the FULL-HISTORY event sequence
                          (E1's chain) binned by era -- pre-1930 / 1930-60 /
                          1960-90 / 1990-2026 -- keeping only events whose
                          horizon also ends inside the era; pre-1930 reported,
                          not interpreted. Per-era direction test (B.4
                          operators, full-history threshold, observations
                          restricted to the era). Method adjudicated against
                          the original artifact: see DESIGN.md amendment of
                          2026-06-09 (the manuscript's per-era-recalibration
                          prose does not match the artifact behind its
                          printed numbers; the artifact arbitrates).
    8. rolling         -- SPX Hull-50, H=63: 1 catch-all 1871-1936 window + 17
                          ten-year windows in 5-year steps from 1931; threshold,
                          MA, and event chain recalibrate from scratch per
                          window (B.11 prose; the original artifact's per-window
                          implementation could not be exactly identified --
                          divergences recorded in DECISIONS.md).
    9. is_oos          -- 13 instruments (robustness core 11 + ES + NKD),
                          Hull-50, H=63: chronological-midpoint split, each
                          half decomposed from scratch.

INSTRUMENT-SET NOTE (adjudicated 2026-06-09)
    The original study's robustness batteries (manuscript Sections 5.4-5.6) ran
    on a variant core set in which NDX (cash) is replaced by NQ (futures) --
    confirmed from the original artifact (MA_Adaptation_Replication.xlsx),
    whose Decomposition Results sheet (= Section 5.1, E1) uses NDX while its
    Horizon/Filter-Matched/IS-OOS/Threshold sheets use NQ. The paper's printed
    robustness numbers derive from the NQ set, so this battery uses it
    (ROBUSTNESS_CORE below); the inconsistency is recorded in DECISIONS.md and
    must be disclosed in the manuscript (Phase 4).

DECISION RULE (DESIGN E7): qualitative stability of E1's conclusion across the
battery; any sign flip or sub-50% region is reported, not smoothed.

INPUTS
    The 13 daily instruments pinned in data/SOURCES.md (core 11 + ES + NKD).
    Run data/pull.py first.

OUTPUT
    analysis/outputs/robustness.json -- input hashes and one results block per
    sub-battery. Plus a console report.

HOW TO RUN (PowerShell)
    cd <repo root>
    python analysis\\robustness.py
    (requires: numpy, pandas, scipy; runtime ~5-15 minutes, Hull MAs dominate)

LOADER NOTE
    Era and rolling-window slicing need dates. The date-aware loader below uses
    the committed loader's parsing (format="mixed") and was verified to yield
    the identical price sequence; SPX daily mixes ISO and US date formats in one
    column (see DECISIONS.md, E5 entry).
"""
import json
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decomposition import (decompose, sma, ema, hma, sha256_of,
                           INSTRUMENT_FILES, INSTRUMENT_ORDER, DATA_DIR,
                           H, THRESHOLD_PCT, MIN_HISTORY)

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "outputs", "robustness.json")

# --------------------------------------------------------------------------
# Configuration (amended DESIGN E7)
# --------------------------------------------------------------------------
EIGHT_SPECS = [("Hull", 20), ("Hull", 50), ("Hull", 100),
               ("SMA", 20), ("SMA", 50), ("SMA", 100), ("SMA", 200),
               ("EMA", 50)]
THRESHOLD_GRID = [50, 75, 90]
HORIZON_GRID = [21, 63, 126, 252]
FILTER_MATCHED = {"Hull-50": 55, "SMA-50": 50, "EMA-50": 75, "SMA-200": 200}
N_OFFSETS = 63
ERAS = [("pre-1930", "1871-01-01", "1930-01-01"),
        ("1930-1960", "1930-01-01", "1960-01-01"),
        ("1960-1990", "1960-01-01", "1990-01-01"),
        ("1990-2026", "1990-01-01", "2099-01-01")]
ROLLING_CATCHALL = ("1871-1936", "1871-01-01", "1936-01-01")
ROLLING_START_YEARS = list(range(1931, 2012, 5))          # 1931 ... 2011 (17)

# Robustness core set: NDX replaced by NQ (see INSTRUMENT-SET NOTE above).
ROBUSTNESS_CORE = ["SPX", "NQ", "NI225", "DAX", "FTSE", "HSI",
                   "CL", "GC", "ZN", "6E", "6J"]
ISOOS_INSTRUMENTS = ROBUSTNESS_CORE + ["ES", "NKD"]
EXTRA_FILES = {"NQ":  "CME_MINI_NQ1!, 1D_de2b2.csv",
               "ES":  "CME_MINI_ES1!, 1D_40b30.csv",
               "NKD": "CME_NKD1!, 1D_92650.csv"}


def make_ma(logP, family, N):
    if family == "Hull":
        return hma(logP, N)
    if family == "SMA":
        return sma(logP, N)
    if family == "EMA":
        return ema(logP, N)
    raise ValueError(family)


def spec_ma(logP, spec):
    family, N = spec.split("-")
    return make_ma(logP, family, int(N))


# --------------------------------------------------------------------------
# Date-aware loader (era / rolling slicing); parse identical to committed loader
# --------------------------------------------------------------------------
def load_prices_dated(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    dt = pd.to_datetime(df["time"], format="mixed", errors="coerce")
    close = pd.to_numeric(df["close"], errors="coerce")
    out = pd.DataFrame({"date": dt, "close": close}).dropna()
    out = out[out["close"] > 0].sort_values("date").reset_index(drop=True)
    return out["date"].to_numpy(), np.log(out["close"].to_numpy())


def slice_by_date(dates, logP, start, end):
    mask = (dates >= np.datetime64(start)) & (dates < np.datetime64(end))
    return logP[mask]


# --------------------------------------------------------------------------
# Offset variant of the decomposition: scan starts `offset` bars after
# min_history; offset = 0 is EXACTLY the committed decompose() (verified).
# --------------------------------------------------------------------------
def decompose_offset(logP, MA, offset, horizon=H, pct=THRESHOLD_PCT,
                     min_hist=MIN_HISTORY):
    x = logP - MA
    abs_x = pd.Series(np.abs(x))
    tau = abs_x.expanding(min_periods=min_hist).quantile(pct / 100.0).to_numpy()
    T = len(logP)
    CP, CW = [], []
    last_event = -horizon
    for t in range(min_hist + offset, T - horizon - 1):
        if np.isnan(tau[t]) or np.isnan(x[t]) or np.isnan(MA[t]):
            continue
        if abs_x[t] > tau[t] and (t - last_event) >= horizon:
            if np.isnan(MA[t + horizon]):
                continue
            dP = logP[t + horizon] - logP[t]
            dW = MA[t + horizon] - MA[t]
            sgn = np.sign(x[t])
            CP.append(-sgn * dP)
            CW.append(sgn * dW)
            last_event = t
    CP, CW = np.array(CP), np.array(CW)
    n = len(CP)
    if n == 0:
        return dict(n=0, agg=float("nan"))
    s = float(CW.sum() + CP.sum())
    return dict(n=n, agg=float(CW.sum() / s) if s != 0 else float("nan"))


# --------------------------------------------------------------------------
# Full-history event chain with dates (for era binning) and binned direction
# test (B.4 operators, full-history threshold, observations restricted by mask)
# --------------------------------------------------------------------------
def event_chain(dates, logP, MA, horizon=H, pct=THRESHOLD_PCT,
                min_hist=MIN_HISTORY):
    """E1's exact non-overlapping event sequence, with event/horizon-end dates
    and per-event contributions. decompose() on the full series equals the
    aggregate over this chain (verified)."""
    x = logP - MA
    abs_x = pd.Series(np.abs(x))
    tau = abs_x.expanding(min_periods=min_hist).quantile(pct / 100.0).to_numpy()
    out, last = [], -horizon
    for t in range(min_hist, len(logP) - horizon - 1):
        if np.isnan(tau[t]) or np.isnan(x[t]) or np.isnan(MA[t]):
            continue
        if abs_x[t] > tau[t] and (t - last) >= horizon:
            if np.isnan(MA[t + horizon]):
                continue
            sgn = np.sign(x[t])
            out.append(dict(t=t, d0=dates[t], d1=dates[t + horizon],
                            cp=-sgn * (logP[t + horizon] - logP[t]),
                            cw=sgn * (MA[t + horizon] - MA[t])))
            last = t
    return out


def bin_events(chain, start, end):
    """Era binning (span rule): an event belongs to the era iff its event date
    AND its horizon-end date fall inside [start, end). Aggregate S_W over the
    binned events."""
    A, B = np.datetime64(start), np.datetime64(end)
    sel = [e for e in chain if A <= e["d0"] and e["d1"] < B]
    if not sel:
        return dict(n=0, agg=float("nan"))
    cp = sum(e["cp"] for e in sel)
    cw = sum(e["cw"] for e in sel)
    s = cp + cw
    return dict(n=len(sel), agg=float(cw / s) if s != 0 else float("nan"))


def direction_binned(dates, logP, MA, start, end, pct=THRESHOLD_PCT,
                     min_hist=MIN_HISTORY):
    """B.4 direction test (every qualifying bar, no spacing) with the
    FULL-HISTORY expanding threshold, observations restricted to [start, end)."""
    A, B = np.datetime64(start), np.datetime64(end)
    x = logP - MA
    abs_x = pd.Series(np.abs(x))
    tau = abs_x.expanding(min_periods=min_hist).quantile(pct / 100.0).to_numpy()
    toward = total = 0
    for t in range(min_hist, len(logP) - 1):
        if not (A <= dates[t] < B):
            continue
        if np.isnan(tau[t]) or np.isnan(x[t]) or np.isnan(MA[t]):
            continue
        if abs_x[t] > tau[t]:
            nr = logP[t + 1] - logP[t]
            if (x[t] > 0 and nr < 0) or (x[t] < 0 and nr > 0):
                toward += 1
            total += 1
    if total == 0:
        return dict(rate=float("nan"), total=0, z=float("nan"), p=float("nan"))
    rate = toward / total
    z = (rate - 0.5) / np.sqrt(0.25 / total)
    p = float(2.0 * (1.0 - stats.norm.cdf(abs(z))))
    return dict(rate=float(rate), total=int(total), z=float(z), p=p)


# --------------------------------------------------------------------------
# Runner -> JSON
# --------------------------------------------------------------------------
def main():
    files = {inst: fn for inst, fn in INSTRUMENT_FILES.items() if inst != "NDX"}
    files.update(EXTRA_FILES)
    input_hashes, dated, prices = {}, {}, {}
    for inst, fn in files.items():
        path = os.path.join(DATA_DIR, fn)
        if not os.path.exists(path):
            raise FileNotFoundError(f"{inst}: {path} not found.")
        input_hashes[inst] = {"file": fn, "sha256": sha256_of(path)}
        d, lp = load_prices_dated(path)
        dated[inst] = d
        prices[inst] = lp

    results = {}
    print("=" * 92)
    print("E7 -- ROBUSTNESS BATTERY (DESIGN.md E7, amended; Sections 5.4-5.6)")
    print("=" * 92)

    # ---- 1. eight-spec sensitivity (SPX, H=63) ----
    spx = prices["SPX"]
    rows = []
    print("\n[1] EIGHT-SPEC SENSITIVITY (SPX, H=63)")
    for family, N in EIGHT_SPECS:
        r = decompose(spx, make_ma(spx, family, N))
        rows.append(dict(spec=f"{family}-{N}", agg=r["agg"], n=r["n"]))
        print(f"    {family}-{N:<5} agg {r['agg']*100:>7.1f}%   events {r['n']}")
    aggs = [r["agg"] * 100 for r in rows]
    print(f"    range: {min(aggs):.1f}% to {max(aggs):.1f}%  "
          f"({sum(1 for a in aggs if a > 50)}/8 > 50%)")
    results["eight_spec"] = dict(rows=rows,
                                 range_pct=[round(min(aggs), 1), round(max(aggs), 1)],
                                 n_above_50=sum(1 for a in aggs if a > 50))

    # ---- 2. threshold sensitivity (SPX, Hull-50, H=63) ----
    hull50_spx = hma(spx, 50)
    rows = []
    print("\n[2] THRESHOLD SENSITIVITY (SPX, Hull-50, H=63)")
    for pct in THRESHOLD_GRID:
        r = decompose(spx, hull50_spx, pct=pct)
        rows.append(dict(threshold_pct=pct, agg=r["agg"], n=r["n"]))
        print(f"    P{pct:<3} agg {r['agg']*100:>7.1f}%   events {r['n']}")
    results["thresholds"] = dict(rows=rows,
                                 all_above_50=all(r["agg"] > 0.5 for r in rows))

    # ---- 3. horizon sensitivity (robustness core 11, Hull-50) ----
    rows, per_h = [], {}
    print("\n[3] HORIZON SENSITIVITY (robustness core 11, Hull-50)")
    hulls = {inst: hma(prices[inst], 50) for inst in ROBUSTNESS_CORE}
    for Hx in HORIZON_GRID:
        above = 0
        for inst in ROBUSTNESS_CORE:
            r = decompose(prices[inst], hulls[inst], horizon=Hx)
            rows.append(dict(instrument=inst, horizon=Hx, agg=r["agg"], n=r["n"]))
            if r["agg"] > 0.5:
                above += 1
        per_h[str(Hx)] = above
        print(f"    H={Hx:<4} {above}/11 above 50%")
    results["horizons"] = dict(rows=rows, above_50_by_horizon=per_h)

    # ---- 4. filter-matched horizons (robustness core 11 x 4 specs) ----
    rows = []
    print("\n[4] FILTER-MATCHED HORIZONS (robustness core 11 x 4 specs; B.10)")
    print(f"    {'Spec':<9}{'H':>5}{'mean agg% (matched)':>21}{'mean agg% (H=63)':>18}")
    fm_summary = {}
    for spec, Hm in FILTER_MATCHED.items():
        m_aggs, b_aggs = [], []
        for inst in ROBUSTNESS_CORE:
            MA = spec_ma(prices[inst], spec)
            rm = decompose(prices[inst], MA, horizon=Hm)
            rb = decompose(prices[inst], MA, horizon=H)
            rows.append(dict(instrument=inst, spec=spec, matched_h=Hm,
                             agg_matched=rm["agg"], n_matched=rm["n"],
                             agg_h63=rb["agg"], n_h63=rb["n"]))
            m_aggs.append(rm["agg"] * 100)
            b_aggs.append(rb["agg"] * 100)
        fm_summary[spec] = dict(matched_h=Hm,
                                mean_agg_matched_pct=round(float(np.mean(m_aggs)), 1),
                                mean_agg_h63_pct=round(float(np.mean(b_aggs)), 1))
        print(f"    {spec:<9}{Hm:>5}{np.mean(m_aggs):>20.1f}%{np.mean(b_aggs):>17.1f}%")
    results["filter_matched"] = dict(rows=rows, summary=fm_summary)

    # ---- 5. starting offsets (SPX, Hull-50, H=63) ----
    print("\n[5] STARTING OFFSETS (SPX, Hull-50, H=63; 63 offsets)")
    offs = []
    for off in range(N_OFFSETS):
        r = decompose_offset(spx, hull50_spx, off)
        offs.append(dict(offset=off, agg=r["agg"], n=r["n"]))
    o_aggs = np.array([o["agg"] * 100 for o in offs])
    print(f"    agg range {o_aggs.min():.1f}% to {o_aggs.max():.1f}%   "
          f"sd {o_aggs.std(ddof=1):.2f} pp   (offset 0 = E1: "
          f"{offs[0]['agg']*100:.1f}% / {offs[0]['n']} events)")
    results["offsets"] = dict(rows=offs,
                              range_pct=[round(float(o_aggs.min()), 1),
                                         round(float(o_aggs.max()), 1)],
                              sd_pp=round(float(o_aggs.std(ddof=1)), 2))

    # ---- 6. log vs level prices (SPX, 4 main specs, H=63) ----
    print("\n[6] LOG VS LEVEL PRICES (SPX, 4 main specs, H=63)")
    level_spx = np.exp(spx)               # back to level prices
    rows = []
    for spec in ["Hull-50", "SMA-50", "SMA-200", "EMA-50"]:
        r_log = decompose(spx, spec_ma(spx, spec))
        r_lvl = decompose(level_spx, spec_ma(level_spx, spec))
        rows.append(dict(spec=spec, agg_log=r_log["agg"], n_log=r_log["n"],
                         agg_level=r_lvl["agg"], n_level=r_lvl["n"]))
        print(f"    {spec:<9} log {r_log['agg']*100:>7.1f}% ({r_log['n']})   "
              f"level {r_lvl['agg']*100:>7.1f}% ({r_lvl['n']})")
    results["log_vs_level"] = dict(
        rows=rows, qualitatively_identical=all(r["agg_level"] > 0.5 for r in rows))

    # ---- 7. era analysis (SPX, Hull-50, H=63; E1 chain binned by era) ----
    print("\n[7] ERA ANALYSIS (SPX, Hull-50, H=63; full-history chain binned; "
          "span rule)")
    chain = event_chain(dated["SPX"], spx, hull50_spx)
    # invariant: chain aggregate == E1's full decomposition
    cp_all = sum(e["cp"] for e in chain); cw_all = sum(e["cw"] for e in chain)
    full_agg = cw_all / (cp_all + cw_all)
    r_e1 = decompose(spx, hull50_spx)
    assert len(chain) == r_e1["n"] and abs(full_agg - r_e1["agg"]) < 1e-12, \
        "event_chain does not reproduce decompose()"
    rows = []
    for name, a, b in ERAS:
        r = bin_events(chain, a, b)
        d = direction_binned(dated["SPX"], spx, hull50_spx, a, b)
        interp = not (name == "pre-1930" or r["n"] < 10)
        rows.append(dict(era=name, agg=r["agg"], n=r["n"],
                         toward_rate=d["rate"], n_direction=d["total"],
                         direction_z=d["z"], direction_p=d["p"],
                         interpreted=interp))
        agg_s = f"{r['agg']*100:7.1f}%" if r["n"] else "     --"
        print(f"    {name:<10} agg {agg_s}   events {r['n']:>4}   "
              f"toward {d['rate']*100:5.1f}% (N {d['total']:>5}, z {d['z']:+.2f}, "
              f"p {d['p']:.4f})"
              f"{'' if interp else '   (reported, not interpreted)'}")
    mod = rows[-1]
    print(f"    modern-era direction test (1990-2026): toward "
          f"{mod['toward_rate']*100:.1f}%  z {mod['direction_z']:+.2f}  "
          f"p {mod['direction_p']:.4f}")
    results["eras"] = dict(rows=rows,
                           binning_rule="span: event date AND horizon-end date "
                                        "inside era",
                           modern_direction=dict(rate=mod["toward_rate"],
                                                 total=mod["n_direction"],
                                                 z=mod["direction_z"],
                                                 p=mod["direction_p"]))

    # ---- 8. rolling windows (SPX, Hull-50, H=63) ----
    print("\n[8] ROLLING WINDOWS (SPX, Hull-50, H=63; B.11)")
    windows = [ROLLING_CATCHALL] + [
        (f"{y}-{y+10}", f"{y}-01-01", f"{y+10}-01-01") for y in ROLLING_START_YEARS]
    rows = []
    for name, a, b in windows:
        seg = slice_by_date(dated["SPX"], spx, a, b)
        r = decompose(seg, hma(seg, 50)) if len(seg) else dict(n=0, agg=float("nan"),
                                                               median=float("nan"),
                                                               mean=float("nan"),
                                                               sum_cp=float("nan"),
                                                               sum_cw=float("nan"))
        rows.append(dict(window=name, agg=r["agg"], median=r["median"], n=r["n"]))
    n_valid = sum(1 for r in rows if r["n"] > 0 and not np.isnan(r["agg"]))
    n_above = sum(1 for r in rows if r["n"] > 0 and r["agg"] > 0.5)
    for r in rows:
        agg_s = f"{r['agg']*100:7.1f}%" if r["n"] else "     --"
        print(f"    {r['window']:<11} agg {agg_s}   events {r['n']:>4}")
    print(f"    -> {n_above} of {len(rows)} windows above 50%")
    results["rolling"] = dict(rows=rows, n_windows=len(rows),
                              n_above_50=n_above, n_with_events=n_valid)

    # ---- 9. IS/OOS midpoint split (13 instruments, Hull-50, H=63) ----
    print("\n[9] IS/OOS MIDPOINT SPLIT (13 instruments, Hull-50, H=63)")
    rows = []
    for inst in ISOOS_INSTRUMENTS:
        lp = prices[inst]
        m = len(lp) // 2
        r1 = decompose(lp[:m], hma(lp[:m], 50))
        r2 = decompose(lp[m:], hma(lp[m:], 50))
        rows.append(dict(instrument=inst,
                         agg_is=r1["agg"], n_is=r1["n"],
                         agg_oos=r2["agg"], n_oos=r2["n"]))
        print(f"    {inst:<7} IS {r1['agg']*100:>7.1f}% ({r1['n']:>3})   "
              f"OOS {r2['agg']*100:>7.1f}% ({r2['n']:>3})")
    is_mean = float(np.mean([r["agg_is"] for r in rows]) * 100)
    oos_mean = float(np.mean([r["agg_oos"] for r in rows]) * 100)
    both_above = sum(1 for r in rows if r["agg_is"] > 0.5 and r["agg_oos"] > 0.5)
    print(f"    -> {both_above}/13 above 50% in BOTH halves; "
          f"mean IS {is_mean:.1f}%, mean OOS {oos_mean:.1f}%")
    results["is_oos"] = dict(rows=rows, n_both_above_50=both_above,
                             mean_is_pct=round(is_mean, 1),
                             mean_oos_pct=round(oos_mean, 1))

    # ---- decision-rule audit: report every sub-50% region ----
    sub50 = []
    for r in results["horizons"]["rows"]:
        if not np.isnan(r["agg"]) and r["agg"] <= 0.5:
            sub50.append(f"horizons: {r['instrument']} H={r['horizon']} "
                         f"agg {r['agg']*100:.1f}%")
    for r in results["rolling"]["rows"]:
        if r["n"] > 0 and not np.isnan(r["agg"]) and r["agg"] <= 0.5:
            sub50.append(f"rolling: {r['window']} agg {r['agg']*100:.1f}%")
    for r in results["is_oos"]["rows"]:
        if r["agg_is"] <= 0.5:
            sub50.append(f"is_oos: {r['instrument']} IS agg {r['agg_is']*100:.1f}%")
        if r["agg_oos"] <= 0.5:
            sub50.append(f"is_oos: {r['instrument']} OOS agg {r['agg_oos']*100:.1f}%")
    results["sub_50_regions"] = sub50
    print("\n" + "=" * 92)
    print("DECISION-RULE AUDIT -- every sub-50% region (reported, not smoothed):")
    for s in sub50:
        print(f"    {s}")
    if not sub50:
        print("    none")

    result = {
        "experiment": "E7_robustness_battery",
        "design_ref": "DESIGN.md section E7 (amended 2026-06-09)",
        "params": {"eight_specs": [f"{f}-{n}" for f, n in EIGHT_SPECS],
                   "threshold_grid": THRESHOLD_GRID,
                   "horizon_grid": HORIZON_GRID,
                   "filter_matched": FILTER_MATCHED,
                   "n_offsets": N_OFFSETS,
                   "eras": [e[0] for e in ERAS],
                   "rolling_start_years": ROLLING_START_YEARS,
                   "isoos_instruments": ISOOS_INSTRUMENTS},
        "inputs": input_hashes,
        "results": results,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="\n") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"\nWritten: {OUT_PATH}")
    return result


if __name__ == "__main__":
    main()
