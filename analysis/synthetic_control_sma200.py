"""
synthetic_control_sma200.py -- A3: the spec-matched SMA-200 synthetic null
(DESIGN.md amendment 2026-06-11, item A3).

"Moving Averages Follow Price" -- Research-to-Publication Standard (review-born
follow-up under the v1.4 gated-fix rule; addresses adversarial-review Finding 4.2,
deferred at Round 1 and disclosed in the paper's Section 5.3: E3's synthetic null
ran under Hull-50 only, so the 11 SMA-200@H=63 cells rested on Corollary 1 rather
than a spec-matched simulated null).

WHAT IT DOES
    Reruns E3's two zero-attraction controls with the decomposition spec set to
    SMA-200, all other operators and seeds identical to E3:

    1. I.I.D. NORMAL -- 20 Gaussian zero-drift random walks (seed 42, length
       25,000, sigma ~20% annual), plus the 200-series large-sample expectation
       run (seed 20260526).
    2. GARCH-CALIBRATED -- GARCH(1,1)-t fits to the same 9 instruments (CL/GC
       excluded for integrated GARCH), 20 mu=0 simulated paths each, D15
       deterministic seeding (StudentsT seeded 42 + instrument index).

    A zero-attraction process should put the SMA-200 aggregate S_W at ~100%; this
    establishes the spec-matched null the paper's Section 5.3 currently lacks.

INPUTS
    GARCH control: the 9 instruments' daily CSVs (project-local store). The
    i.i.d. control needs no external data.

OUTPUT
    analysis/outputs/synthetic_control_sma200.json

HOW TO RUN (PowerShell)
    cd <repo root>
    python analysis\\synthetic_control_sma200.py
    (requires: numpy, pandas, arch)
"""
import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decomposition import (load_prices, moving_average, decompose, sha256_of,
                           INSTRUMENT_FILES, DATA_DIR)
from synthetic_control import (SEED, SIGMA_DAILY, IID_N_SERIES, IID_LENGTH,
                               LARGE_N_SERIES, LARGE_SEED, GARCH_INSTRUMENTS,
                               GARCH_N_SIMS, rw_from_returns)

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "outputs", "synthetic_control_sma200.json")

DECOMP_SPEC = "SMA-200"     # the only operator change vs E3


def aggregate_sw(logP):
    return decompose(logP, moving_average(logP, DECOMP_SPEC))


def run_iid(n_series, length=IID_LENGTH, seed=SEED):
    np.random.seed(seed)
    rows = []
    for i in range(n_series):
        r = np.random.normal(0.0, SIGMA_DAILY, length)
        res = aggregate_sw(rw_from_returns(r))
        rows.append(dict(sim=i + 1, agg=float(res["agg"]), n_events=int(res["n"])))
    return rows


def run_garch(data_dir):
    from arch.univariate import ConstantMean, GARCH, StudentsT
    import warnings
    warnings.filterwarnings("ignore")
    out = []
    for i, inst in enumerate(GARCH_INSTRUMENTS):
        path = os.path.join(data_dir, INSTRUMENT_FILES[inst])
        logP = load_prices(path)
        r = np.diff(logP)
        am = ConstantMean(r * 100.0)
        am.volatility = GARCH(p=1, q=1)
        am.distribution = StudentsT(seed=SEED + i)
        fit = am.fit(disp="off")
        a, b = fit.params["alpha[1]"], fit.params["beta[1]"]
        persistence = float(a + b)
        if persistence >= 1.0:
            out.append(dict(instrument=inst, excluded=True, persistence=persistence,
                            garch_mean_agg=float("nan"), garch_std=float("nan"),
                            n_sims=0))
            continue
        psim = fit.params.copy()
        psim["mu"] = 0.0
        aggs = []
        for _ in range(GARCH_N_SIMS):
            sim = fit.model.simulate(psim, len(r))
            sr = sim["data"].to_numpy() / 100.0
            res = aggregate_sw(rw_from_returns(sr))
            aggs.append(res["agg"] * 100.0)
        aggs = np.array(aggs)
        out.append(dict(instrument=inst, excluded=False, persistence=persistence,
                        garch_mean_agg=float(aggs.mean()),
                        garch_std=float(aggs.std(ddof=1)), n_sims=GARCH_N_SIMS))
    return out


def main():
    print("=" * 78)
    print("A3 -- SPEC-MATCHED SMA-200 SYNTHETIC NULL "
          "(DESIGN.md amendment 2026-06-11)")
    print(f"identical to E3 except decomposition spec: {DECOMP_SPEC}; seed {SEED}")
    print("=" * 78)

    print("\n[1] I.I.D. NORMAL CONTROL (zero drift)")
    iid = run_iid(IID_N_SERIES)
    iid_aggs = np.array([r["agg"] * 100 for r in iid])
    print(f"    per-sim aggregate S_W: {', '.join(f'{a:.1f}' for a in iid_aggs)}")
    print(f"    mean = {iid_aggs.mean():.2f}%   sd = {iid_aggs.std(ddof=1):.2f}")

    print("\n    Large-sample expectation:")
    big = run_iid(LARGE_N_SERIES, seed=LARGE_SEED)
    big_aggs = np.array([r["agg"] * 100 for r in big])
    se = float(big_aggs.std(ddof=1) / np.sqrt(len(big_aggs)))
    print(f"    {len(big_aggs)} series -> mean = {big_aggs.mean():.2f}% (SE {se:.2f}).")

    print("\n[2] GARCH-CALIBRATED CONTROL (mu=0, D15 seeding)")
    input_hashes = {inst: {"file": INSTRUMENT_FILES[inst],
                           "sha256": sha256_of(os.path.join(DATA_DIR,
                                                            INSTRUMENT_FILES[inst]))}
                    for inst in GARCH_INSTRUMENTS}
    garch = run_garch(DATA_DIR)
    incl = []
    print(f"    {'Instrument':<11}{'persist.':>9}{'mean agg%':>12}{'sd%':>8}")
    print("    " + "-" * 42)
    for g in garch:
        if g["excluded"]:
            print(f"    {g['instrument']:<11}{g['persistence']:>9.3f}"
                  f"{'EXCLUDED (IGARCH)':>22}")
        else:
            print(f"    {g['instrument']:<11}{g['persistence']:>9.3f}"
                  f"{g['garch_mean_agg']:>12.1f}{g['garch_std']:>8.1f}")
            incl.append(g["garch_mean_agg"])
    garch_mean = float(np.mean(incl)) if incl else float("nan")
    if incl:
        print("    " + "-" * 42)
        print(f"    GARCH control mean across {len(incl)}: {garch_mean:.1f}%")

    summary = {
        "decomp_spec": DECOMP_SPEC,
        "iid_20sim_mean_pct": round(float(iid_aggs.mean()), 2),
        "iid_20sim_sd_pct": round(float(iid_aggs.std(ddof=1)), 2),
        "large_sample_n": int(len(big_aggs)),
        "large_sample_mean_pct": round(float(big_aggs.mean()), 2),
        "large_sample_se_pct": round(se, 2),
        "garch_instruments_included": int(len(incl)),
        "garch_mean_agg_pct": round(garch_mean, 1),
    }

    print("\n" + "=" * 78)
    print(f"SUMMARY: iid 20-sim mean {summary['iid_20sim_mean_pct']}%; large-sample "
          f"{summary['large_sample_mean_pct']}% (SE {summary['large_sample_se_pct']}); "
          f"GARCH mean {summary['garch_mean_agg_pct']}%")

    result = {
        "experiment": "A3_synthetic_control_sma200",
        "design_ref": "DESIGN.md amendment 2026-06-11 (A3)",
        "params": {"seed": SEED, "sigma_daily": SIGMA_DAILY,
                   "iid_n_series": IID_N_SERIES, "iid_length": IID_LENGTH,
                   "large_n_series": LARGE_N_SERIES, "large_seed": LARGE_SEED,
                   "decomp_spec": DECOMP_SPEC,
                   "garch_instruments": GARCH_INSTRUMENTS,
                   "garch_n_sims": GARCH_N_SIMS},
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
