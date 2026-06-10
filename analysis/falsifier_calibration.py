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
measure, on the above-threshold event set (Hull-50, 75th-pct expanding
threshold), THREE statistics, averaged over independent paths:

  (i)  b4_toward_rate -- the paper's B.4 next-bar PRICE-direction operator
       (x>0 and next return<0, or x<0 and next return>0). Exactly 50% in
       expectation at beta=0 by independence; rises smoothly with beta.
  (ii) gap_shrink_rate -- P(|x(t+1)| < |x(t)|), a FILTER-INCLUSIVE statistic
       that exceeds 50% even at beta=0 because the trailing average adapts
       every bar. Reported to show the contrast; it is NOT the B.4 operator
       (an earlier revision of this script mislabeled it as the toward rate --
       caught by adversarial review Round 2 and corrected here).
  (iii) the aggregate S_W from the unmodified decompose() at H=63.

Purpose: calibrate the falsifier. The output curve shows aggregate S_W is
monotone decreasing in genuine attraction and crosses below 50% at a finite,
identifiable beta -- the bar is reachable -- and records the B.4 toward rate
at that crossing (~57%), giving the falsifier a direction-test equivalent.

Deterministic: fixed seed. Headline values registered in claims.lock (LB-021).

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


def event_rates(logP, spec=SPEC):
    """Return (b4_toward_rate, gap_shrink_rate) on above-threshold bars.

    b4_toward_rate: the manuscript's B.4 operator -- next-bar PRICE direction
    relative to the MA (toward iff sign(next return) opposes sign(x)).
    gap_shrink_rate: P(|x(t+1)| < |x(t)|) -- includes the filter's own
    adaptation and exceeds 50% even under a random walk. Not the B.4 operator.
    """
    MA = moving_average(logP, spec)
    x = logP - MA
    ax = pd.Series(np.abs(x))
    tau = ax.expanding(min_periods=MIN_HISTORY).quantile(THRESHOLD_PCT / 100).to_numpy()
    b4 = gs = tot = 0
    for t in range(MIN_HISTORY, len(logP) - 1):
        if np.isnan(tau[t]) or np.isnan(x[t]):
            continue
        if ax[t] > tau[t]:
            r = logP[t + 1] - logP[t]
            if (x[t] > 0 and r < 0) or (x[t] < 0 and r > 0):
                b4 += 1
            if abs(x[t + 1]) < abs(x[t]):
                gs += 1
            tot += 1
    if tot == 0:
        return float("nan"), float("nan")
    return b4 / tot, gs / tot


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    for beta in BETAS:
        b4s, gss, sws, nev = [], [], [], []
        for _ in range(N_PATHS):
            lp = gen_attracted(T, beta, rng)
            b4, gs = event_rates(lp)
            b4s.append(b4)
            gss.append(gs)
            d = decompose(lp, moving_average(lp, SPEC))
            if d["n"] > 0:
                sws.append(d["agg"])
                nev.append(d["n"])
        rows.append(dict(beta=beta,
                         b4_toward_rate=float(np.nanmean(b4s)),
                         gap_shrink_rate=float(np.nanmean(gss)),
                         agg_sw=float(np.mean(sws)),
                         mean_events=float(np.mean(nev))))
        print(f"beta={beta:>5.2f}  B4_toward={100*np.nanmean(b4s):5.1f}%  "
              f"gap_shrink={100*np.nanmean(gss):5.1f}%  "
              f"aggS_W={100*np.mean(sws):6.1f}%  n={int(np.mean(nev))}")

    # locate the sub-50% crossing and the B.4 toward rate at that crossing
    cross = cross_b4 = None
    for a, b in zip(rows, rows[1:]):
        if a["agg_sw"] >= 0.5 > b["agg_sw"]:
            f = (a["agg_sw"] - 0.5) / (a["agg_sw"] - b["agg_sw"])
            cross = a["beta"] + f * (b["beta"] - a["beta"])
            cross_b4 = (a["b4_toward_rate"]
                        + f * (b["b4_toward_rate"] - a["b4_toward_rate"]))
            break
    out = dict(experiment="falsifier_calibration", seed=SEED, spec=SPEC,
               sigma_daily=SIGMA, path_length=T, n_paths=N_PATHS,
               rows=rows, sub50_crossing_beta=cross,
               b4_toward_at_crossing=cross_b4,
               b4_toward_at_beta0=rows[0]["b4_toward_rate"])
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "outputs", "falsifier_calibration.json"),
              "w", newline="\n") as fp:
        json.dump(out, fp, indent=2)
        fp.write("\n")
    if cross:
        print(f"\nsub-50% S_W crossing at beta ~ {cross:.3f}; "
              f"B.4 toward rate there ~ {100*cross_b4:.1f}% "
              f"(at beta=0: {100*rows[0]['b4_toward_rate']:.2f}%)")
    else:
        print("\nno sub-50% crossing in tested range")
    print("written: analysis/outputs/falsifier_calibration.json")


if __name__ == "__main__":
    main()
