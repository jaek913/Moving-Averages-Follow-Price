# Moving Averages Follow Price

Research repository for **"Moving Averages Follow Price: A Mathematical Proof and
Empirical Validation of the Adaptation Property in Trailing Averages"** —
a standalone paper under the Discovery Lattice / Lagging Truth program.

Built under the **Research-to-Publication Standard v1.3**. The contract:

> A number may appear in the paper only if a committed script, run on hashed input
> data, regenerates it on demand. No script, no number. The script is the truth;
> the paper quotes it. Done = `verify.py` exits green.

There is no outside gatekeeper: the paper is posted as a work-in-progress, comments
welcome, and is refutable by anyone because the data dictionary, code, and review
transcript are public.

## The claim (see THESIS.md)

When a price series deviates from a causal trailing moving average, the subsequent
convergence is predominantly the **mechanical adaptation of the average to price**,
not mean reversion of price toward the average. The S_W decomposition quantifies
the mechanical share; the falsifier is a mechanical share below 50% across the
tested instruments.

## Structure (Standard v1.3 layout)

| Path | Contents |
|---|---|
| `THESIS.md`        | Phase 0 — the claim, why it matters, the gap, the falsifier. |
| `DESIGN.md`        | Phase 1 — each experiment's exact operator, decision rules, spec counts, and the data manifest. Amended dated, never overwritten. |
| `data/SOURCES.md`  | Every input series: vendor, exact symbol, date range, bar interval, session, adjustment, timezone, price field, full SHA-256, project-local store location, and replicator tolerances. |
| `data/pull.py`     | Verifies/hashes the local price files against SOURCES.md. Raw data is **not** committed (see below). |
| `analysis/`        | One script per experiment; each reads hashed data and writes its result to `analysis/outputs/` as JSON. |
| `analysis/outputs/`| Committed JSON results — what the paper quotes. |
| `claims.lock`      | Phase 3 — the ledger: one row per load-bearing number → script, input hashes, value, tolerance, CIC flags. |
| `verify.py`        | Phase 3 — the checker. Green = done. Re-hashes inputs, re-runs scripts, checks the ledger against the paper. |
| `paper/`           | Phase 4 — the manuscript and shipping PDF. The plain-English companion lives at LaggingTruth.com (single canonical copy). |
| `verification/`    | Phase 5 — the capped adversarial review transcript and responses. |
| `CORRECTIONS.md`   | Public post-publication corrections log (initialized at publication; errors found in the published record are handled here, in the open). |
| `DECISIONS.md`     | Append-only research notebook: decisions, dead ends, surprises. |
| `requirements.txt` | Pinned Python environment. |

## Reproducing the results

```
# 1. Environment (Python 3.12)
pip install -r requirements.txt

# 2. Obtain the price data (not committed)
#    Export the TradingView daily CSVs listed in data/SOURCES.md and verify
#    each against its SHA-256 fingerprint (data/pull.py does this for you).
#    Place them in one folder.

# 3. Run an analysis (e.g. the core decomposition)
LT_DATA_DIR=/path/to/price/csvs python analysis/decomposition.py
#    Results land in analysis/outputs/ as JSON.

# 4. Verify everything
python verify.py
```

## Why the raw price data is not committed

The price series are daily exports from **TradingView**, which licenses the data from
the exchanges (CME, COMEX, NYMEX, CBOT, HKEX, and the index providers). Those terms
permit a user to export and analyse the data but **not** to redistribute the raw
series. This repository follows standard practice for finance research on licensed
market data: the **code** is public and the **data source is documented precisely
enough to be reproduced** — every file pinned by ticker, observation count, date
range, and full SHA-256 in `data/SOURCES.md`. A within-tolerance mode in `verify.py`
accepts a replicator's own vendor export against the declared per-series tolerance.

## Provenance

This project is a rebuild of previously completed work under the new Standard; see
the dated provenance entry in `DECISIONS.md`. Git timestamps document the rebuild,
not the original formation of the hypotheses.

## License

Three kinds of material, three licenses — full text and file lists in `LICENSE`:
the **manuscript** CC BY-NC-ND 4.0; the **plain-English companion** CC BY-NC 4.0;
the **code** MIT. Raw price data is not in this repository (exchange-licensed).

## Citing

This repository is tagged (v1.0) and archived to Zenodo with DOI
**10.5281/zenodo.20469741** (reserved; registers on publication). Recommended
citation:

> Kim, Jae (2026). "Moving Averages Follow Price: A Mathematical Proof and
> Empirical Validation of the Adaptation Property in Trailing Averages."
> Working paper, v1.0. doi:10.5281/zenodo.20469741.
