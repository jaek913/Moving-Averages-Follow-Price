"""
pe_volatility_blockperm.py -- A2: serial-dependence-corrected inference for E4
(DESIGN.md amendment 2026-06-11, item A2).

"Moving Averages Follow Price" -- Research-to-Publication Standard (review-born
follow-up under the v1.4 gated-fix rule; addresses adversarial-review Finding 3.1,
deferred at Round 1 and disclosed in the paper as a limitation).

WHAT IT DOES
    Recomputes the E4 displacement-volatility battery's significance under serial
    dependence, two ways, on the SAME non-overlapping 21-bar sample as E4:

    1. EFFECTIVE-N CORRECTION (all 33 Spearman tests: 11 full + 11 IS + 11 OOS).
       Pyper-Peterman / Quenouille effective sample size from the cross-products of
       the two rank series' autocorrelations:
           n_eff = n / (1 + 2 * sum_{k=1..K} ((n-k)/n) * rho_PE(k) * rho_FV(k)),
       K = min(n//4, 50), n_eff clipped to [5, n]. Two-sided p from the t
       approximation with df = n_eff - 2.

    2. CIRCULAR BLOCK PERMUTATION (the 5 long-history instruments of E4).
       The PE rank-z vector is permuted in contiguous circular blocks of length L
       SAMPLES against the fixed FwdVol rank-z vector, preserving within-block
       serial structure. Ladder L in {3, 6, 12, 24} samples = {63, 126, 252, 504}
       bars (the review's ">= 63 bars" satisfied by every rung). 5,000 permutations
       per rung, deterministic derived seeds. The reported corrected p per
       instrument is the MAXIMUM (most conservative) across the ladder.

    The Bonferroni frame is unchanged from E4 (38 tests, threshold 0.05/38); the
    corrected battery replaces the original anti-conservative p-values. The
    cross-sectional sign test (11 instruments) does not involve serial dependence
    and is reported unchanged.

INPUTS
    Same 11 instruments as E4 (project-local store; run data/pull.py first).

OUTPUT
    analysis/outputs/pe_volatility_blockperm.json

HOW TO RUN (PowerShell)
    cd <repo root>
    python analysis\\pe_volatility_blockperm.py
    (requires: numpy, pandas, scipy)
"""
import json
import os
import sys
import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decomposition import (load_prices, sha256_of, INSTRUMENT_FILES,
                           INSTRUMENT_ORDER, DATA_DIR)
from pe_volatility import (pe_and_fwdvol, sampled_pairs, PERM_INSTRUMENTS,
                           BONFERRONI_N, BONFERRONI_THRESH, N_PERM)

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "outputs", "pe_volatility_blockperm.json")

SEED = 42                          # base seed (pre-registered, matches E4)
BLOCK_LADDER = [3, 6, 12, 24]      # block lengths in SAMPLES (x21 bars each)
MAX_LAG_CAP = 50                   # autocorrelation lag cap for effective-n


def rank_z(v):
    r = stats.rankdata(v)
    return (r - r.mean()) / r.std()


def autocorr(z, k):
    if k >= len(z) - 1:
        return 0.0
    a, b = z[:-k], z[k:]
    sa, sb = a.std(), b.std()
    if sa == 0 or sb == 0:
        return 0.0
    return float(np.mean((a - a.mean()) * (b - b.mean())) / (sa * sb))


def effective_n(z1, z2):
    """Pyper-Peterman effective sample size for the correlation of two series."""
    n = len(z1)
    K = min(n // 4, MAX_LAG_CAP)
    s = 0.0
    for k in range(1, K + 1):
        s += ((n - k) / n) * autocorr(z1, k) * autocorr(z2, k)
    n_eff = n / (1.0 + 2.0 * s)
    return float(np.clip(n_eff, 5.0, n))


def corrected_corr(pe_v, fwd_v):
    """Spearman rho with the effective-n corrected two-sided p (t approximation)."""
    if len(pe_v) < 30:
        return dict(rho=float("nan"), n=len(pe_v), n_eff=float("nan"),
                    p_naive=float("nan"), p_eff=float("nan"))
    z1, z2 = rank_z(pe_v), rank_z(fwd_v)
    rho = float(np.mean(z1 * z2))
    n = len(pe_v)
    n_eff = effective_n(z1, z2)

    def t_p(r, m):
        if m <= 2 or abs(r) >= 1:
            return float("nan")
        t = r * np.sqrt((m - 2) / (1 - r * r))
        return float(2.0 * stats.t.sf(abs(t), df=m - 2))

    return dict(rho=rho, n=int(n), n_eff=round(n_eff, 1),
                p_naive=t_p(rho, n), p_eff=t_p(rho, n_eff))


def block_permutation(pe_v, fwd_v, L, n_perm, seed):
    """Circular block permutation p-value at block length L (in samples)."""
    z1, z2 = rank_z(pe_v), rank_z(fwd_v)
    n = len(z1)
    real_rho = float(np.mean(z1 * z2))
    n_blocks = int(np.ceil(n / L))
    rng = np.random.default_rng(seed)
    exceed = 0
    base = np.arange(n)
    for _ in range(n_perm):
        shifted = (base + rng.integers(n)) % n          # circular shift
        blocks = [shifted[i * L:(i + 1) * L] for i in range(n_blocks)]
        order = rng.permutation(n_blocks)
        idx = np.concatenate([blocks[j] for j in order])[:n]
        if float(np.mean(z1[idx] * z2)) > real_rho:
            exceed += 1
    p_perm = exceed / n_perm
    return dict(L_samples=L, L_bars=L * 21, exceed=int(exceed), n_perm=n_perm,
                p_report=(p_perm if exceed > 0 else 1.0 / n_perm),
                rho=real_rho, n=int(n))


def main():
    prices, input_hashes = {}, {}
    for inst, fn in INSTRUMENT_FILES.items():
        path = os.path.join(DATA_DIR, fn)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{inst}: {path} not found. Set LT_DATA_DIR or see data/SOURCES.md.")
        input_hashes[inst] = {"file": fn, "sha256": sha256_of(path)}
        prices[inst] = load_prices(path)

    print("=" * 96)
    print("A2 -- E4 INFERENCE UNDER SERIAL DEPENDENCE (DESIGN.md amendment 2026-06-11)")
    print(f"effective-n (Pyper-Peterman, K<=min(n//4,{MAX_LAG_CAP})) on all 33 tests; "
          f"circular block permutation ladder {BLOCK_LADDER} samples on "
          f"{len(PERM_INSTRUMENTS)} instruments")
    print("=" * 96)

    # ---- 1. effective-n corrected battery (full + IS + OOS) ----
    rows = []
    print(f"\n{'Instrument':<11}{'rho':>8}{'n':>7}{'n_eff':>9}"
          f"{'p_naive':>11}{'p_eff':>11}   (full sample)")
    print("-" * 96)
    for inst in INSTRUMENT_ORDER:
        PE, fwd = pe_and_fwdvol(prices[inst])
        pe_v, fwd_v = sampled_pairs(PE, fwd)
        m = len(pe_v) // 2
        full = corrected_corr(pe_v, fwd_v)
        is_h = corrected_corr(pe_v[:m], fwd_v[:m])
        oos = corrected_corr(pe_v[m:], fwd_v[m:])
        rows.append(dict(instrument=inst, full=full, is_half=is_h, oos_half=oos))
        print(f"{inst:<11}{full['rho']:>+8.3f}{full['n']:>7d}{full['n_eff']:>9.1f}"
              f"{full['p_naive']:>11.2e}{full['p_eff']:>11.2e}")

    # ---- 2. block permutation ladder ----
    print(f"\nBlock permutation ({N_PERM} perms/rung, seed base {SEED}):")
    print(f"  {'Instrument':<11}{'L(smp)':>8}{'L(bars)':>9}{'exceed':>8}{'p':>11}")
    print("  " + "-" * 50)
    block_rows = []
    for ii, inst in enumerate(PERM_INSTRUMENTS):
        PE, fwd = pe_and_fwdvol(prices[inst])
        pe_v, fwd_v = sampled_pairs(PE, fwd)
        rungs = []
        for L in BLOCK_LADDER:
            seed = SEED * 100000 + ii * 100 + L      # deterministic, documented
            r = block_permutation(pe_v, fwd_v, L, N_PERM, seed)
            rungs.append(r)
            ptxt = f"<{1.0/N_PERM:.4f}" if r["exceed"] == 0 else f"{r['p_report']:.4f}"
            print(f"  {inst:<11}{L:>8d}{r['L_bars']:>9d}{r['exceed']:>8d}{ptxt:>11}")
        p_cons = max(r["p_report"] for r in rungs)
        block_rows.append(dict(instrument=inst, rungs=rungs,
                               p_conservative=p_cons, rho=rungs[0]["rho"],
                               n=rungs[0]["n"]))
        print(f"  {inst:<11}{'':>8}{'':>9}{'':>8}{'-> max':>11}  "
              f"p_conservative = {p_cons:.4f}")

    # ---- Bonferroni over the corrected battery (same 38-test frame as E4) ----
    p33 = ([r["full"]["p_eff"] for r in rows]
           + [r["is_half"]["p_eff"] for r in rows]
           + [r["oos_half"]["p_eff"] for r in rows])
    p38 = p33 + [b["p_conservative"] for b in block_rows]
    n_below = int(np.sum(np.array(p38) < BONFERRONI_THRESH))
    n_below_05 = int(np.sum(np.array(p38) < 0.05))

    rho_full = np.array([r["full"]["rho"] for r in rows])
    n_pos = int((rho_full > 0).sum())
    sign_p = float(2.0 * stats.binom.cdf(min(n_pos, 11 - n_pos), 11, 0.5))

    print("\n" + "=" * 96)
    print(f"Corrected Bonferroni ({BONFERRONI_N} tests, threshold "
          f"{BONFERRONI_THRESH:.5f}): {n_below} of {BONFERRONI_N} survive")
    print(f"Uncorrected 0.05 level: {n_below_05} of {BONFERRONI_N} below 0.05")
    print(f"Sign test (cross-sectional, unaffected by serial dependence): "
          f"{n_pos}/11 positive, two-sided p = {sign_p:.5f}")
    print(f"Mean full-sample rho: {rho_full.mean():+.3f}")

    summary = {
        "n_survive_bonferroni_corrected": n_below,
        "n_below_05_corrected": n_below_05,
        "bonferroni_n": BONFERRONI_N,
        "bonferroni_threshold": BONFERRONI_THRESH,
        "rho_full_mean": round(float(rho_full.mean()), 3),
        "n_positive_of_11": n_pos,
        "sign_test_p": sign_p,
        "median_n_eff_full": round(float(np.median([r["full"]["n_eff"]
                                                    for r in rows])), 1),
        "block_p_conservative": {b["instrument"]: b["p_conservative"]
                                 for b in block_rows},
    }

    result = {
        "experiment": "A2_pe_volatility_blockperm",
        "design_ref": "DESIGN.md amendment 2026-06-11 (A2)",
        "params": {"seed_base": SEED, "block_ladder_samples": BLOCK_LADDER,
                   "n_perm": N_PERM, "max_lag_cap": MAX_LAG_CAP,
                   "perm_instruments": PERM_INSTRUMENTS,
                   "bonferroni_n": BONFERRONI_N},
        "inputs": input_hashes,
        "rows": rows,
        "block_rows": block_rows,
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
