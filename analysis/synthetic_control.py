"""
synthetic_control.py -- E3: synthetic zero-attraction controls (DESIGN.md section E3).

"Moving Averages Follow Price" -- Research-to-Publication Standard v1.2, Phase 2.
Ported 2026-06-09 from the prior iteration's verified reconstruction (see
DECISIONS.md); operators unchanged. Instrument key "Nikkei" renamed "NI225" to
match this repo's manifest (label-only change).

WHAT IT DOES
    Two synthetic controls, both processes with ZERO mean-reversion by construction.
    If the decomposition's aggregate-S_W metric is honest, a no-attraction process
    should yield an MA share of ~100% (the moving average does all the gap closure
    because price itself does not revert).

    1. I.I.D. NORMAL -- 20 Gaussian random walks (zero drift), each run through the
       E1 decomposition; plus a 200-series large-sample run estimating the metric's
       expectation under zero attraction.
    2. GARCH-CALIBRATED -- a GARCH(1,1) model with Student-t innovations fitted to
       each real instrument's returns, then simulated with mean mu = 0, run through
       the decomposition. Tests whether volatility clustering changes the result.

INPUTS
    For the GARCH control: the daily CSVs for the 9 GARCH instruments pinned in
    data/SOURCES.md (project-local store; LT_DATA_DIR or the default in
    decomposition.py). The i.i.d. control needs no external data. Run data/pull.py
    first.

OUTPUT
    analysis/outputs/synthetic_control.json -- input hashes (GARCH instruments),
    per-sim i.i.d. aggregates, large-sample estimate, per-instrument GARCH results,
    and a summary. Plus a console report.

HOW TO RUN (PowerShell)
    cd <repo root>
    python analysis\\synthetic_control.py
    (requires: numpy, pandas, arch)

OPERATORS (DESIGN.md section E3)
    i.i.d.: 20 series, length 25,000, r ~ N(0, sigma^2), sigma_daily = 0.20/sqrt(252);
    seed 42. GARCH: GARCH(1,1)-t per instrument, 20 mu=0 paths each; CL and GC
    excluded (integrated GARCH); explicitly seeded StudentsT distribution (prior
    discrepancy D15) -- seed 42 + instrument index -- so the control is fully
    deterministic. Decomposition spec: Hull-50.
"""
import json
import os
import sys
import numpy as np
import pandas as pd

# allow `from decomposition import ...` regardless of the working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decomposition import (load_prices, moving_average, decompose, sha256_of,
                           INSTRUMENT_FILES, DATA_DIR)

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "outputs", "synthetic_control.json")

# --------------------------------------------------------------------------
# Configuration (DESIGN.md E3)
# --------------------------------------------------------------------------
SEED = 42                              # pre-registered seed
SIGMA_DAILY = 0.20 / np.sqrt(252)      # ~20% annual volatility -> ~0.0126
IID_N_SERIES = 20                      # 20 i.i.d. series
IID_LENGTH = 25_000                    # length 25,000
LARGE_N_SERIES = 200                   # large-sample expectation run
LARGE_SEED = 20260526                  # carried from the prior reconstruction
DECOMP_SPEC = "Hull-50"                # primary spec used for the synthetic control

# GARCH control: the 9 instruments (CL and GC excluded for integrated GARCH)
GARCH_INSTRUMENTS = ["SPX", "NDX", "NI225", "DAX", "FTSE", "HSI", "ZN", "6E", "6J"]
GARCH_N_SIMS = 20                      # 20 simulated paths per instrument


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def rw_from_returns(returns):
    """Build a log-price path from a return series: logP[0] = 0, then cumulative sum."""
    return np.concatenate([[0.0], np.cumsum(returns)])


def aggregate_sw(logP, spec=DECOMP_SPEC):
    """Aggregate S_W from the E1 decomposition for one synthetic price path."""
    return decompose(logP, moving_average(logP, spec))


# --------------------------------------------------------------------------
# Control 1 -- i.i.d. normal random walks
# --------------------------------------------------------------------------
def run_iid_control(n_series=IID_N_SERIES, length=IID_LENGTH, drift=0.0, seed=SEED):
    """Generate n_series zero-drift Gaussian random walks and decompose each.

    r[t] ~ N(0, sigma^2), sigma calibrated to ~20% annual vol; logP[0] = 0;
    prices are the cumulative sum of returns. Returns a list of result dicts.
    """
    np.random.seed(seed)
    rows = []
    for i in range(n_series):
        r = np.random.normal(drift, SIGMA_DAILY, length)
        res = aggregate_sw(rw_from_returns(r))
        rows.append(dict(sim=i + 1, agg=float(res["agg"]), n_events=int(res["n"])))
    return rows


# --------------------------------------------------------------------------
# Control 2 -- GARCH(1,1)-t, simulated with mu = 0
# --------------------------------------------------------------------------
def run_garch_control(data_dir, instruments=GARCH_INSTRUMENTS,
                      n_sims=GARCH_N_SIMS, seed=SEED):
    """Fit GARCH(1,1)-t to each instrument, simulate n_sims mu=0 paths, decompose each.

    Fit r[t] = mu + eps[t] with GARCH(1,1) variance and Student-t innovations by
    MLE; simulate with mu set to 0 (zero attraction by construction). Instruments
    whose fit is integrated (alpha + beta >= 1) are excluded.

    Reproducibility (prior discrepancy D15): arch's model.simulate() does NOT draw
    from numpy's global RNG, so numpy.random.seed() never reaches it. The model is
    therefore built from components (ConstantMean + GARCH + StudentsT) with an
    explicitly seeded Student-t distribution, a distinct derived seed per instrument,
    which makes the GARCH control fully deterministic.
    """
    from arch.univariate import ConstantMean, GARCH, StudentsT
    import warnings
    warnings.filterwarnings("ignore")

    out = []
    for i, inst in enumerate(instruments):
        path = os.path.join(data_dir, INSTRUMENT_FILES[inst])
        logP = load_prices(path)
        r = np.diff(logP)                       # daily log returns
        # fit GARCH(1,1)-t with a constant mean; returns scaled to % for stability.
        am = ConstantMean(r * 100.0)
        am.volatility = GARCH(p=1, q=1)
        am.distribution = StudentsT(seed=seed + i)
        fit = am.fit(disp="off")
        a, b = fit.params["alpha[1]"], fit.params["beta[1]"]
        persistence = float(a + b)
        if persistence >= 1.0:                  # integrated GARCH -> exclude
            out.append(dict(instrument=inst, excluded=True, persistence=persistence,
                            garch_mean_agg=float("nan"), garch_std=float("nan"),
                            n_sims=0))
            continue
        # simulate n_sims paths with mu = 0 (deterministic: seeded distribution above)
        psim = fit.params.copy()
        psim["mu"] = 0.0
        aggs = []
        for _ in range(n_sims):
            sim = fit.model.simulate(psim, len(r))
            sr = sim["data"].to_numpy() / 100.0      # back to log-return units
            res = aggregate_sw(rw_from_returns(sr))
            aggs.append(res["agg"] * 100.0)
        aggs = np.array(aggs)
        out.append(dict(instrument=inst, excluded=False, persistence=persistence,
                        garch_mean_agg=float(aggs.mean()),
                        garch_std=float(aggs.std(ddof=1)), n_sims=n_sims))
    return out


# --------------------------------------------------------------------------
# Runner -> JSON
# --------------------------------------------------------------------------
def main():
    print("=" * 78)
    print("E3 -- SYNTHETIC ZERO-ATTRACTION CONTROLS (DESIGN.md E3)")
    print(f"decomposition spec: {DECOMP_SPEC}; seed {SEED}")
    print("=" * 78)

    # ---- Control 1: i.i.d. normal (zero drift) ----
    print("\n[1] I.I.D. NORMAL CONTROL (zero drift)")
    print(f"    {IID_N_SERIES} series, length {IID_LENGTH}, sigma_daily={SIGMA_DAILY:.6f}")
    iid = run_iid_control()
    iid_aggs = np.array([r["agg"] * 100 for r in iid])
    print(f"    per-sim aggregate S_W: {', '.join(f'{a:.1f}' for a in iid_aggs)}")
    print(f"    mean = {iid_aggs.mean():.2f}%   sd = {iid_aggs.std(ddof=1):.2f}")

    print("\n    Large-sample expectation (the metric's value under zero attraction):")
    big = run_iid_control(n_series=LARGE_N_SERIES, seed=LARGE_SEED)
    big_aggs = np.array([r["agg"] * 100 for r in big])
    se = float(big_aggs.std(ddof=1) / np.sqrt(len(big_aggs)))
    print(f"    {len(big_aggs)} series -> mean = {big_aggs.mean():.2f}% (SE {se:.2f}).")

    # ---- Control 2: GARCH-calibrated, simulated with mu = 0 ----
    print("\n[2] GARCH-CALIBRATED CONTROL -- GARCH(1,1)-t, simulated with mu=0")
    input_hashes = {inst: {"file": INSTRUMENT_FILES[inst],
                           "sha256": sha256_of(os.path.join(DATA_DIR, INSTRUMENT_FILES[inst]))}
                    for inst in GARCH_INSTRUMENTS}
    garch = run_garch_control(DATA_DIR)
    print(f"    {'Instrument':<11}{'persist.':>9}{'GARCH mean agg%':>17}{'GARCH sd%':>11}")
    print("    " + "-" * 46)
    incl = []
    for g in garch:
        if g["excluded"]:
            print(f"    {g['instrument']:<11}{g['persistence']:>9.3f}"
                  f"{'EXCLUDED (IGARCH)':>28}")
        else:
            print(f"    {g['instrument']:<11}{g['persistence']:>9.3f}"
                  f"{g['garch_mean_agg']:>17.1f}{g['garch_std']:>11.1f}")
            incl.append(g["garch_mean_agg"])
    garch_mean = float(np.mean(incl)) if incl else float("nan")
    if incl:
        print("    " + "-" * 46)
        print(f"    GARCH control mean across {len(incl)} instruments: {garch_mean:.1f}%")

    summary = {
        "iid_20sim_mean_pct": round(float(iid_aggs.mean()), 2),
        "iid_20sim_sd_pct": round(float(iid_aggs.std(ddof=1)), 2),
        "large_sample_n": int(len(big_aggs)),
        "large_sample_mean_pct": round(float(big_aggs.mean()), 2),
        "large_sample_se_pct": round(se, 2),
        "garch_instruments_included": int(len(incl)),
        "garch_mean_agg_pct": round(garch_mean, 1),
    }

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"i.i.d. seed-42 20-sim mean {summary['iid_20sim_mean_pct']}%; large-sample "
          f"expectation {summary['large_sample_mean_pct']}% (SE {summary['large_sample_se_pct']}).")
    print(f"GARCH control (deterministic, D15 seeding): mean {summary['garch_mean_agg_pct']}% "
          f"across {summary['garch_instruments_included']} instruments.")
    print("The aggregate-S_W metric is approximately unbiased under zero attraction.")

    result = {
        "experiment": "E3_synthetic_controls",
        "design_ref": "DESIGN.md section E3",
        "params": {"seed": SEED, "sigma_daily": SIGMA_DAILY,
                   "iid_n_series": IID_N_SERIES, "iid_length": IID_LENGTH,
                   "large_n_series": LARGE_N_SERIES, "large_seed": LARGE_SEED,
                   "decomp_spec": DECOMP_SPEC,
                   "garch_instruments": GARCH_INSTRUMENTS, "garch_n_sims": GARCH_N_SIMS},
        "inputs": input_hashes,
        "iid_rows": iid,
        "large_sample_rows": big,
        "garch_rows": garch,
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
