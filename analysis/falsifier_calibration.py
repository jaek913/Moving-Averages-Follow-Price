"""
falsifier_calibration.py -- Phase 5 (adversarial review, Finding 4.1 response).

The reviewer's load-bearing finding asks: what genuine attraction would drive
the aggregate S_W metric below its 50% falsifier at H=63? If the answer were
"nothing realistic," the bar would be rhetorical. This script answers it
empirically on the paper's own decompose() operator.

Construction. Build synthetic log-price paths with an EXPLICIT, controllable
daily attraction toward a trailing mean:

    r[t] = -beta * (logP[t-1] - MA_50(t-1)) + sigma * z[t],   z ~ N(0,1)

beta = 0 is a driftless random walk (the paper's null; aggregate S_W ~ 100%).
beta > 0 injects genuine mean-reversion of known strength. For each beta we
measure (i) the realized next-bar toward-rate on the direction-test event set
and (ii) the aggregate S_W from the unmodified decompose() (Hull-50, H=63,
75th-pct expanding threshold), averaged over independent paths.

Purpose: calibrate the falsifier. The output curve shows S_W is monotone
decreasing in genuine attraction and crosses below 50% at a finite, identifiable
beta -- i.e. the bar is reachable -- while also showing the toward-rate is a
weak discriminator (measurement-pinned), which is why the paper leans on
aggregate S_W rather than the toward-rate for the headline claim.

Deterministic: fixed seed. Not a load-bearing claim in claims.lock (it
characterizes the metric, it is not a result about markets); recorded in
verification/ and cited in the Finding 4.1 response.

Run:  python analysis/falsifier_calibration.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decomposition import moving_average, decompose, THRESHOLD_PCT, MIN_HISTORY

SEED = 20260610
SIGMA = 0.0126          # ~SPX daily log-return sd
SPEC = "Hull-50"
T = 8000
N_PATHS = 8
BETAS = [0.0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.20]


def gen_attracted(T, beta, rng, sigma=SIGMA, N=50):
    logP = np.zeros(T)
    for t in range(1, T):
        ma = logP[max(0, t - N):t].mean() if t > 1 else logP[t - 1]
        logP[t] = logP[t - 1] - beta * (logP[t - 1] - ma) + sigma * rng.standard_normal()
    return logP


def toward_rate(logP, spec=SPEC):
    MA = moving_average(logP, spec)
    x = logP - MA
    ax = pd.Series(np.abs(x))
    tau = ax.expanding(min_periods=MIN_HISTORY).quantile(THRESHOLD_PCT / 100).to_numpy()
    tow = tot = 0
    for t in range(MIN_HISTORY, len(logP) - 1):
        if np.isnan(tau[t]) or np.isnan(x[t]):
            continue
        if ax[t] > tau[t]:
            tow += 1 if abs(x[t + 1]) < abs(x[t]) else 0
            tot += 1
    return (tow / tot if tot else float("nan"))


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    for beta in BETAS:
        trs, sws, nev = [], [], []
        for _ in range(N_PATHS):
            lp = gen_attracted(T, beta, rng)
            trs.append(toward_rate(lp))
            d = decompose(lp, moving_average(lp, SPEC))
            if d["n"] > 0:
                sws.append(d["agg"])
                nev.append(d["n"])
        rows.append(dict(beta=beta,
                         toward_rate=float(np.nanmean(trs)),
                         agg_sw=float(np.mean(sws)),
                         mean_events=float(np.mean(nev))))
        print(f"beta={beta:>5.2f}  toward={100*np.nanmean(trs):5.1f}%  "
              f"aggS_W={100*np.mean(sws):6.1f}%  n={int(np.mean(nev))}")

    # locate the sub-50% crossing
    cross = None
    for a, b in zip(rows, rows[1:]):
        if a["agg_sw"] >= 0.5 > b["agg_sw"]:
            f = (a["agg_sw"] - 0.5) / (a["agg_sw"] - b["agg_sw"])
            cross = a["beta"] + f * (b["beta"] - a["beta"])
            break
    out = dict(experiment="falsifier_calibration", seed=SEED, spec=SPEC,
               sigma_daily=SIGMA, path_length=T, n_paths=N_PATHS,
               rows=rows, sub50_crossing_beta=cross)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "outputs", "falsifier_calibration.json"),
              "w", newline="\n") as fp:
        json.dump(out, fp, indent=2)
        fp.write("\n")
    print(f"\nsub-50% S_W crossing at beta ~ {cross:.3f}"
          if cross else "\nno sub-50% crossing in tested range")
    print("written: analysis/outputs/falsifier_calibration.json")


if __name__ == "__main__":
    main()
