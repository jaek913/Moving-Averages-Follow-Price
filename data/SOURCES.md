# Data Sources — Moving Averages Follow Price

Every input series, recorded so an independent party can obtain identical data and
verify it byte-for-byte. Raw files are **not** committed (exchange-licensed; see
the licensing note below). `pull.py` in this folder verifies a local copy of the
data against this manifest.

**Project-local store (git-ignored, this machine):**
`C:\Users\jaek9\Documents\LaggingTruth\Moving-Averages-Follow-Price\`
Backup: J: drive (Crucial X10 SSD).

All series are **TradingView CSV exports, daily (1D) bars**. Hashes below were
computed 2026-06-09 from the author's original export files and match the prior
iteration's fingerprints (first-16 prefixes) exactly.

---

## Licensing note — why the raw CSVs are not committed

TradingView price data is licensed from the exchanges (CME, COMEX, NYMEX, CBOT,
HKEX, and the index providers). TradingView's terms permit a user to export and
analyse the data; they do **not** permit redistribution of the raw exported series.
This repository follows standard practice for finance research on licensed market
data: the **code** is public and the **data source is documented precisely enough
to be reproduced** by anyone with a TradingView account.

---

## Core instruments (11) — decomposition (E1), direction test (E2), PE-volatility (E4)

| Inst | TradingView ticker | Export file | Obs | Start | End | SHA-256 (full) |
|---|---|---|---|---|---|---|
| SPX   | SP:SPX        | `SP_SPX, 1D_5871b.csv`         | 25,187 | 1871-02-01 | 2026-03-12 | `c75e8fb61149f5ba606ebe5a3881db40a1015ff49e322a590cf6e7a7d537cbe7` |
| NDX   | NASDAQ:NDX    | `NASDAQ_DLY_NDX, 1D_e6961.csv` | 10,359 | 1985-01-31 | 2026-03-13 | `0e93da6e7e3a97cbc377c5b8ad9930ae3261a28d22410322ee5c6e9ec250c1b5` |
| NI225 | TVC:NI225     | `TVC_NI225, 1D_8be07.csv`      | 19,040 | 1949-05-16 | 2026-03-13 | `271da7a404086ff9c939daf8c8ff18cf3eb4d45c60214a3e5e53a42f1ee70228` |
| DAX   | XETR:DAX      | `XETR_DLY_DAX, 1D_cd703.csv`   | 14,143 | 1970-01-02 | 2026-03-13 | `4531616311c17b8cbd5781ba20717ac5a93c31d348282474fff9c39f7c144491` |
| FTSE  | IG:FTSE       | `IG_FTSE, 1D_c9679.csv`        |  8,615 | 1995-01-03 | 2026-03-13 | `ae76f4a65e6c65e96ea141fe4d23e8348a7033d9e8348a46efd681c5dbf31e1c` |
| HSI   | HKEX:HSI      | `HKEX_DLY_HSI1!, 1D_57a14.csv` |  9,585 | 1987-04-21 | 2026-03-16 | `840dbd3fce9da09b06d5e4aa459a8070ed352735230bd171bbcc2546e69ef99c` |
| CL    | NYMEX:CL1!    | `NYMEX_CL1!, 1D_de4b1.csv`     | 10,798 | 1983-03-30 | 2026-03-13 | `f32fb49cd7653c01cbcd91e43a58615811be04f4ed84c22d4b061711c96494f4` |
| GC    | COMEX:GC1!    | `COMEX_GC1!, 1D_1e2f0.csv`     | 12,878 | 1975-01-02 | 2026-03-13 | `cd71339445b1c5107c808b8dad76b77383aadada26b0b240a086d323430e67d0` |
| ZN    | CBOT:ZN1!     | `CBOT_ZN1!, 1D_3436b.csv`      | 11,058 | 1982-05-03 | 2026-03-13 | `d2d88f9c7614e0c9995952a885f1a297c4fc6eb1a3dfcbef6e593b45fcd44840` |
| 6E    | CME:6E1!      | `CME_6E1!, 1D_9dd8b.csv`       |  6,451 | 2000-09-12 | 2026-03-13 | `4422e3a4631493125d31eaa3906e3bb74351c2b9b90ede76bd3dd53651b06c5f` |
| 6J    | CME:6J1!      | `CME_6J1!, 1D_01e58.csv`       |  6,373 | 2000-09-13 | 2026-03-13 | `f342d871ee4af468f323633e7f857725da67efc82259b3e1d28bb2384b21006c` |

## Extension instruments (2) — IS/OOS and Schelling extensions only

| Inst | TradingView ticker | Export file | Obs | Start | End | SHA-256 (full) |
|---|---|---|---|---|---|---|
| ES  | CME_MINI:ES1! | `CME_MINI_ES1!, 1D_40b30.csv` | 7,210 | 1997-09-09 | 2026-03-13 | `b81fc7a91bd0ee202291b8bfc9411f812f7f99042f167fd87819026fb2d67bab` |
| NKD | CME:NKD1!     | `CME_NKD1!, 1D_92650.csv`     | 5,574 | 2004-02-17 | 2026-03-13 | `c8468adf2dac6bbf9ec385bfefb69414a3e0e26a639722bccfaface33875afd0` |

---

## Data-variability schema (applies to every series above)

- **Vendor:** TradingView (chart CSV export).
- **Bar interval:** 1D (daily).
- **Session:** exchange default as served by TradingView — ETH for the futures
  symbols (CL, GC, ZN, 6E, 6J, ES, NKD, HSI front-month), exchange cash session
  for the indices (SPX, NDX, NI225, DAX, FTSE).
- **Adjustment / roll:** futures are TradingView's default front-month splice
  (`1!` continuous, no back-adjustment). Indices are as-published levels; no
  split/dividend adjustment applies to index levels.
- **Timezone:** exchange-local session dates as exported by TradingView.
- **Price field:** `close` column. Analysis operates on ln(close).
- **Schema:** column layouts vary by export vintage (5/7/11-column). Loaders read
  columns **by name** (`time`, `close`) and parse both ISO (YYYY-MM-DD) and US
  (M/D/YYYY) date formats. SPX is monthly-frequency in its early history
  (pre-daily era), daily thereafter; it is treated as one bar series throughout,
  as in the prior iteration.

**What a replicator's own pull may differ on, and the tolerance that absorbs it:**
a fresh TradingView export made today will have a **later end date** (extra rows)
and may reflect vendor revisions in the early history of the long index series.
Exact SHA-256 match is expected only for the author's archived files. For a fresh
pull, the within-tolerance mode (`verify.py`, Phase 3) accepts: same ticker and
bar interval, start date matching to the day, observation count >= the listed
count, and headline statistics within the per-claim tolerances in `claims.lock`.
Roll-method differences on the `1!` futures splices are the largest known source
of replicator variance; the decomposition is robust to them (trailing averages
adapt to roll gaps mechanically — see DESIGN.md §0).

---

## Provenance notes

- **NDX is the cash NASDAQ-100 index**, not the NQ E-mini future (prior-iteration
  discrepancy D11, established by reconstruction). The Schelling test alone uses
  NQ futures on all its timeframes (the cash index lacks intraday history).
- **FTSE:** a second export (`IG_FTSE, 1D_3a15f.csv`, 7-column) matches the same
  fingerprint window (8,615 obs, same range) and is an equivalent alternate;
  `c9679` (11-column) is canonical here for schema consistency.
- **Synthetic controls (E3)** are generated, not collected — seed 42; no external
  data source (see DESIGN.md §E3).
- **Schelling intraday/monthly layers (E5):** NOT yet in this manifest — open
  design decision (DESIGN.md §E5): re-export and hash, or re-scope to the daily
  52 combinations. This manifest covers the daily layer only.

*Populated 2026-06-09 (Phase 2 data layer). Hashes computed from the author's
original exports in `C:\Users\jaek9\Documents\LaggingTruth\Data\` and verified
against the prior iteration's fingerprint table before the files were copied into
the project-local store.*
