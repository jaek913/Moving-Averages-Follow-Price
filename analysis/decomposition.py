"""
decomposition.py -- E1: the core gap-closure decomposition (DESIGN.md section E1).

"Moving Averages Follow Price" -- Research-to-Publication Standard v1.2, Phase 2.
Ported 2026-06-09 from the prior iteration's verified reconstruction (see
DECISIONS.md); operators unchanged.

WHAT IT DOES
    For each instrument x MA-specification combination, computes the moving average
    of log prices, identifies displacement events where price sits far from the MA,
    and measures over a forward horizon how much of the gap closure came from the MA
    moving (C_W) versus price moving (C_P). Reports each combination's aggregate,
    median, and mean S_W and event count.

INPUTS
    The 13-instrument TradingView daily CSVs pinned in data/SOURCES.md. Raw files
    are NOT committed (exchange-licensed); they live in the project-local store.
    Set the directory via LT_DATA_DIR, or the default below. Run data/pull.py
    first -- do not run this on an unverified data layer.

OUTPUT
    analysis/outputs/decomposition.json -- parameters, the SHA-256 of every input
    actually read, all 44 combination rows, and the summary statistics the paper
    quotes. Plus a console table.

HOW TO RUN (PowerShell)
    cd <repo root>
    python analysis\\decomposition.py
    (requires: numpy, pandas; see requirements.txt)

OPERATORS (DESIGN.md sections 1 and E1)
    H = 63, expanding 75th-percentile threshold (no look-ahead), min_history = 252,
    non-overlapping events. MA specs: Hull-50, SMA-50, SMA-200, EMA-50.
    EMA is the normalized adjust=True form (load-bearing; prior discrepancy D12).
    NDX is the cash NASDAQ-100 index (prior discrepancy D11).
"""
import hashlib
import json
import os
import math
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
DATA_DIR = os.environ.get(
    "LT_DATA_DIR",
    r"C:\Users\jaek9\Documents\LaggingTruth\Moving-Averages-Follow-Price",
)
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "outputs", "decomposition.json")

# instrument -> export filename (full provenance: data/SOURCES.md)
INSTRUMENT_FILES = {
    "SPX":    "SP_SPX, 1D_5871b.csv",
    "NDX":    "NASDAQ_DLY_NDX, 1D_e6961.csv",   # cash NASDAQ-100 index (D11)
    "NI225":  "TVC_NI225, 1D_8be07.csv",
    "DAX":    "XETR_DLY_DAX, 1D_cd703.csv",
    "FTSE":   "IG_FTSE, 1D_c9679.csv",
    "HSI":    "HKEX_DLY_HSI1!, 1D_57a14.csv",
    "CL":     "NYMEX_CL1!, 1D_de4b1.csv",
    "GC":     "COMEX_GC1!, 1D_1e2f0.csv",
    "ZN":     "CBOT_ZN1!, 1D_3436b.csv",
    "6E":     "CME_6E1!, 1D_9dd8b.csv",
    "6J":     "CME_6J1!, 1D_01e58.csv",
}
INSTRUMENT_ORDER = list(INSTRUMENT_FILES.keys())

H = 63                  # forward horizon, trading days
THRESHOLD_PCT = 75      # expanding percentile for "substantial deviation"
MIN_HISTORY = 252       # bars before events may be selected (~1 trading year)

MA_SPECS = ["Hull-50", "SMA-50", "SMA-200", "EMA-50"]


# --------------------------------------------------------------------------
# Data loading -- schema-tolerant (columns read by NAME; see data/SOURCES.md)
# --------------------------------------------------------------------------
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_prices(path):
    """Load a TradingView CSV; return a numpy array of log close prices.

    Reads columns by NAME (export schema varies: 5/7/11-column) and parses
    both ISO (YYYY-MM-DD) and US (M/D/YYYY) date formats.
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if "time" not in df.columns or "close" not in df.columns:
        raise ValueError(f"{path}: expected 'time' and 'close' columns, got {list(df.columns)}")
    dt = pd.to_datetime(df["time"], format="mixed", errors="coerce")
    close = pd.to_numeric(df["close"], errors="coerce")
    out = pd.DataFrame({"date": dt, "close": close}).dropna()
    out = out[out["close"] > 0]                       # log needs positive prices
    out = out.sort_values("date").reset_index(drop=True)
    return np.log(out["close"].to_numpy())


# --------------------------------------------------------------------------
# Moving averages (DESIGN.md section 1)
# --------------------------------------------------------------------------
def sma(p, N):
    return pd.Series(p).rolling(N).mean().to_numpy()

def ema(p, N):
    """EMA of span N (alpha = 2/(N+1)), normalized 'adjust=True' form:

        EMA(t) = sum_{k=0..t} (1-alpha)^k * p[t-k]  /  sum_{k=0..t} (1-alpha)^k

    This normalized weighted-average form (pandas ewm(adjust=True)) is
    load-bearing: the recursive adjust=False form diverges by up to 30 pp
    (prior discrepancy D12).
    """
    return pd.Series(p).ewm(span=N, adjust=True).mean().to_numpy()

def wma(p, M):
    """Linearly weighted MA: weights (M-k) for k=0..M-1, k=0 the most recent bar."""
    w = np.arange(M, 0, -1, dtype=float)
    w /= w.sum()
    p = np.asarray(p, float)
    out = np.full(len(p), np.nan)
    for t in range(M - 1, len(p)):
        win = p[t - M + 1 : t + 1][::-1]              # win[0] = p[t]
        if not np.isnan(win).any():
            out[t] = float(np.dot(w, win))
    return out

def hma(p, N):
    """Hull MA of window N: WMA_sqrt(N) of (2*WMA_{N/2} - WMA_N)."""
    half = N // 2
    sq = int(math.isqrt(N))
    inner = 2 * wma(p, half) - wma(p, N)
    return wma(inner, sq)

def moving_average(p, spec):
    if spec == "Hull-50":  return hma(p, 50)
    if spec == "SMA-50":   return sma(p, 50)
    if spec == "SMA-200":  return sma(p, 200)
    if spec == "EMA-50":   return ema(p, 50)
    raise ValueError(f"unknown MA spec: {spec}")


# --------------------------------------------------------------------------
# Decomposition (DESIGN.md section E1)
# --------------------------------------------------------------------------
def decompose(logP, MA, horizon=H, pct=THRESHOLD_PCT, min_hist=MIN_HISTORY):
    """Return summary stats for the gap-closure decomposition.

      x[t]   = logP[t] - MA[t]
      tau[t] = expanding pct-percentile of |x| using data through t (no look-ahead)
      event when |x[t]| > tau[t] AND >= H bars since the last event (non-overlapping)
      C_P = -sign(x)*dP ; C_W = +sign(x)*dW ; S_W = C_W/(C_P+C_W)
      aggregate S_W = sum(C_W) / sum(C_P + C_W)
    """
    x = logP - MA
    abs_x = pd.Series(np.abs(x))
    tau = abs_x.expanding(min_periods=min_hist).quantile(pct / 100.0).to_numpy()

    T = len(logP)
    CP, CW, SW = [], [], []
    last_event = -horizon
    for t in range(min_hist, T - horizon - 1):
        if np.isnan(tau[t]) or np.isnan(x[t]) or np.isnan(MA[t]):
            continue
        if abs_x[t] > tau[t] and (t - last_event) >= horizon:
            if np.isnan(MA[t + horizon]):
                continue
            dP = logP[t + horizon] - logP[t]
            dW = MA[t + horizon] - MA[t]
            sgn = np.sign(x[t])
            c_p = -sgn * dP
            c_w = sgn * dW
            CP.append(c_p)
            CW.append(c_w)
            if (c_p + c_w) != 0:
                SW.append(c_w / (c_p + c_w))
            last_event = t

    CP = np.array(CP); CW = np.array(CW); SW = np.array(SW)
    n = len(CP)
    if n == 0:
        return dict(n=0, agg=float("nan"), median=float("nan"), mean=float("nan"),
                    sum_cp=float("nan"), sum_cw=float("nan"))
    sum_cp, sum_cw = float(CP.sum()), float(CW.sum())
    agg = sum_cw / (sum_cw + sum_cp) if (sum_cw + sum_cp) != 0 else float("nan")
    return dict(n=n, agg=float(agg),
                median=float(np.median(SW)) if len(SW) else float("nan"),
                mean=float(np.mean(SW)) if len(SW) else float("nan"),
                sum_cp=sum_cp, sum_cw=sum_cw)


# --------------------------------------------------------------------------
# Runner -- all 44 instrument-filter combinations -> JSON
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
        for spec in MA_SPECS:
            MA = moving_average(logP, spec)
            r = decompose(logP, MA)
            rows.append(dict(instrument=inst, ma_spec=spec, **r))

    agg_pct = [r["agg"] * 100 for r in rows]
    summary = {
        "combinations": len(rows),
        "agg_sw_min_pct": round(min(agg_pct), 1),
        "agg_sw_max_pct": round(max(agg_pct), 1),
        "exceed_50pct": int(sum(a > 50 for a in agg_pct)),
        "exceed_100pct": int(sum(a > 100 for a in agg_pct)),
    }

    print("=" * 86)
    print("E1 -- CORE DECOMPOSITION (DESIGN.md E1)")
    print(f"H={H}, threshold={THRESHOLD_PCT}th pctile, min_history={MIN_HISTORY}, "
          f"{len(INSTRUMENT_ORDER)} instruments x {len(MA_SPECS)} specs")
    print("=" * 86)
    print(f"{'Instrument':<11}{'MA Spec':<10}{'AggS_W%':>9}{'MedianS_W%':>12}"
          f"{'MeanS_W%':>10}{'Events':>8}")
    print("-" * 86)
    for r in rows:
        print(f"{r['instrument']:<11}{r['ma_spec']:<10}"
              f"{r['agg']*100:>9.1f}{r['median']*100:>12.1f}"
              f"{r['mean']*100:>10.1f}{r['n']:>8d}")
    print("-" * 86)
    print(f"Combinations: {summary['combinations']}")
    print(f"Aggregate S_W range: {summary['agg_sw_min_pct']}% to {summary['agg_sw_max_pct']}%")
    print(f"Exceed  50%: {summary['exceed_50pct']}/44")
    print(f"Exceed 100%: {summary['exceed_100pct']}/44")

    result = {
        "experiment": "E1_core_decomposition",
        "design_ref": "DESIGN.md section E1",
        "params": {"H": H, "threshold_pct": THRESHOLD_PCT, "min_history": MIN_HISTORY,
                   "ma_specs": MA_SPECS, "instruments": INSTRUMENT_ORDER},
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
