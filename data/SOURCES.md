# Data Sources — Moving Averages Follow Price

Every input series, recorded so an independent party can obtain identical data and
verify it byte-for-byte. Raw files are **not** committed (exchange-licensed; see
the licensing note below). `pull.py` in this folder verifies a local copy of the
data against this manifest.

**Project-local store (git-ignored, this machine):**
`C:\Users\jaek9\Documents\LaggingTruth\Moving-Averages-Follow-Price\`
Backup: J: drive (Crucial X10 SSD).

All series are **TradingView CSV exports**: daily (1D) bars for the core and
extension layers, plus hourly (60), 5-minute (5), and monthly (1M) bars for the
Schelling test (E5). Hashes below were computed 2026-06-09 from the author's
original export files; the daily layer matches the prior iteration's fingerprints
(first-16 prefixes) exactly, and the E5 layer adopts the exact files named in the
original replication log (DESIGN.md §4, 2026-06-09 amendment).

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

## Schelling layers (E5) — hourly (12), 5-minute (8), monthly (2)

Used only by the Schelling Point test (E5). File identities pinned from the
original replication log; see the DESIGN.md amendment of 2026-06-09. min_history
by timeframe: daily 252, hourly 500, 5-minute 2,000, monthly 60 (B.7). The
Schelling daily layer = the 11 core instruments with NDX replaced by NQ
(`NQ.1D` below; verified to reproduce the workbook's NQ daily rows exactly),
plus ES and NKD from the extension table.

| Key | TradingView ticker | Export file | Obs | Start | End | SHA-256 (full) |
|---|---|---|---|---|---|---|
| NQ.1D    | CME_MINI:NQ1! | `CME_MINI_NQ1!, 1D_de2b2.csv`  |  6,753 | 1999-06-30 | 2026-03-13 | `105b8be21760373023f21aa58777933d4299fcfa6a8bdd591e260fb562538375` |
| NQ.60    | CME_MINI:NQ1! | `CME_MINI_NQ1!, 60_985ba.csv`  | 24,757 | 2022-01-02 | 2026-03-13 | `cb78020d2e0af9dd6d08c8009e375f51fc87d4966680ce61042f51213862c2c7` |
| NI225.60 | TVC:NI225     | `TVC_NI225, 60_b5054.csv`      | 20,848 | 2014-01-05 | 2026-03-13 | `0d5756d747cdcbdd7f81565e28bbfe767b28d9d3d5feb6cfd9cfecb0262211b9` |
| DAX.60   | XETR:DAX      | `XETR_DLY_DAX, 60_82c16.csv`   | 20,964 | 2017-01-02 | 2026-03-13 | `d5f30c75a50c611e4c6e9d86585b8c0b7577a7a45fb5fb260bd91fcdb4ce9745` |
| FTSE.60  | IG:FTSE       | `IG_FTSE, 60_6e958.csv`        | 14,458 | 2023-10-29 | 2026-03-13 | `80e3bc00085f1d4cf197b87f550d6fac38238b37bafbad496221e360930f44bf` |
| HSI.60   | HKEX:HSI1!    | `HKEX_DLY_HSI1!, 60_7c166.csv` | 17,486 | 2022-03-11 | 2026-03-13 | `f3ee58c0f215c592947a2e6e471bfa87a2a5acabe9f7eab8c3a7f0607b1c732e` |
| CL.60    | NYMEX:CL1!    | `NYMEX_CL1!, 60_72c46.csv`     | 24,815 | 2022-01-02 | 2026-03-13 | `76c86cdd31cde67275a79e83f5115c9c3abd28fe2ade7317d903701e2e64d123` |
| GC.60    | COMEX:GC1!    | `COMEX_GC1!, 60_26eca.csv`     | 23,682 | 2022-03-11 | 2026-03-13 | `ea5c1db35ae672c21babff92906bb111a11337420e120ea2a11d62567cc345e0` |
| ZN.60    | CBOT:ZN1!     | `CBOT_ZN1!, 60_81641.csv`      | 23,636 | 2022-03-11 | 2026-03-13 | `09d2f935b27a4467bb468e75a98cf076adce3022cd1ad1e4f75dfb235c11c56d` |
| 6E.60    | CME:6E1!      | `CME_6E1!, 60_df31a.csv`       | 23,715 | 2022-03-13 | 2026-03-13 | `bd832acaff17c155d64fa963b3eb95ffac6ad6e3175f353dacb75030f8c5f2d9` |
| 6J.60    | CME:6J1!      | `CME_6J1!, 60_5c795.csv`       | 23,715 | 2022-03-13 | 2026-03-13 | `0c129e5897ddf7e44e1d416a211063c672003912b98abbf0b21f295a5a98acbd` |
| ES.60    | CME_MINI:ES1! | `CME_MINI_ES1!, 60_127a6.csv`  | 24,757 | 2022-01-02 | 2026-03-13 | `af9636e77793376e4eeae541b5c3d440619f0f89d6473d5fa3df34f5f8716b87` |
| NKD.60   | CME:NKD1!     | `CME_NKD1!, 60_ffee5.csv`      | 23,577 | 2022-03-13 | 2026-03-13 | `eb2be2bbfaf556329630e47396e413181ad6d003867c45596ef3177d247d0bb3` |
| ES.5     | CME_MINI:ES1! | `CME_MINI_ES1!, 5_28d89.csv`   | 21,116 | 2025-11-23 | 2026-03-13 | `4c42d1c46421ed8696f8998ab855fe1ac6cb4f9a2f20d24a90bb8f027b689e12` |
| NQ.5     | CME_MINI:NQ1! | `CME_MINI_NQ1!, 5_c2781.csv`   | 21,117 | 2025-11-23 | 2026-03-13 | `68a8c0e43f6182e65d56ac9c08dc65a3cb186c478bff5c5fa619b5c1cb82bed7` |
| GC.5     | COMEX:GC1!    | `COMEX_GC1!, 5_f87e8.csv`      | 21,176 | 2025-11-23 | 2026-03-13 | `0348a5ba6186b9b90b47050bbff9031fd67c593ad0852669230da1722d820e39` |
| CL.5     | NYMEX:CL1!    | `NYMEX_CL1!, 5_a29b4.csv`      | 21,180 | 2025-11-23 | 2026-03-13 | `49babb3e90a39e54c26f66fd9bdd77672f88a1a13c79ef7c52b2962064956c69` |
| ZN.5     | CBOT:ZN1!     | `CBOT_ZN1!, 5_bdc1e.csv`       | 20,877 | 2025-11-23 | 2026-03-13 | `371db6204f513861aaa2b19d398494bce6ae6ebc583e456281d6d19387073d0c` |
| 6E.5     | CME:6E1!      | `CME_6E1!, 5_d72d6.csv`        | 20,059 | 2025-11-30 | 2026-03-13 | `182f84d3ff659ce269be2da6af8005e2b164ff3afabc3c5d35c510d427b4300a` |
| 6J.5     | CME:6J1!      | `CME_6J1!, 5_c0f96.csv`        | 20,059 | 2025-11-30 | 2026-03-13 | `eb9fa9fe87e55b6b1142f9d86208e5c7db447cc90d569f70771978205a403044` |
| NKD.5    | CME:NKD1!     | `CME_NKD1!, 5_f1b66.csv`       | 20,757 | 2025-11-16 | 2026-03-13 | `52ccdc7ab16bd231131be0c73f318248320f767415add2f282561472910f6411` |
| SPX.1M   | SP:SPX        | `SP_SPX, 1M_9ba20.csv`         |  1,668 | 1871-02-01 | 2026-03-02 | `895f28d799cda2b1c8971a62964beb95186c3db69f7cebe2f848272f94370206` |
| GC.1M    | COMEX:GC1!    | `COMEX_GC1!, 1M_958cd.csv`     |    615 | 1975-01-01 | 2026-03-02 | `998151626467226d5578a9a1e827f5175d4a5854576122f6210cc1b443d1ef1c` |

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
- **Schelling intraday/monthly layers (E5):** pinned 2026-06-09 from the original
  replication log and added to this manifest (22 files; table above), then
  **verified by reproduction against the original Schelling workbook**
  (`Schelling_Point_Test.xlsx`): sampled combinations on every timeframe
  reproduce the workbook's per-combination N and toward rates (exactly, or
  within 1–6 events — threshold-tie boundary effects). One correction from that
  verification: the log's 6E 5-minute entry (`5_20b27`, a different export
  batch) does not reproduce the workbook; `CME_6E1!, 5_d72d6.csv` reproduces it
  exactly (N = 5,718, toward 46.73 at SMA-20) and is adopted. Full scope
  retained: daily 13 + hourly 12 + 5-minute 8 + monthly 2; 137 expected
  combinations. See DESIGN.md §4 amendments.

*Populated 2026-06-09 (Phase 2 data layer). Hashes computed from the author's
original exports in `C:\Users\jaek9\Documents\LaggingTruth\Data\` and verified
against the prior iteration's fingerprint table before the files were copied into
the project-local store.*
