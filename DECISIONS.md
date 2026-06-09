# DECISIONS — Moving Averages Follow Price

Append-only research notebook. Dead ends, surprises, decisions and reasons. Newest at the bottom. Never edit or delete an entry; correct by appending.

---

## 2026-06-09 — Project kickoff: rebuild under the Research-to-Publication Standard v1.2

**Decision.** "Moving Averages Follow Price" is rebuilt from scratch as a standalone paper under the new Standard (ClickUp doc 2kydc08j-754), as the pilot project for the new process. The old numbered series ("Paper 1" of 10/11) and its Pre-Print Review Protocol pipeline are superseded for this project.

**Provenance — this is a port, not an original pre-registration.** The science is complete and public-facing in the prior iteration. THESIS.md (Phase 0) and DESIGN.md (Phase 1) are ported from:

- v5 manuscript: `lagging-truth-paper-01/paper/Paper1_MA_Adaptation_Core_v5.md` — MD5 `ce836c756e93086252a5ad144147ae46`, 595 lines, version dated 2026-05-27. Source of the claim, gap, falsifier, operators (Appendix B), and all empirical targets.
- Old repo analysis layer: six reconstructed scripts (`decomposition.py`, `direction_test.py`, `pe_volatility.py`, `quarterly_reversion.py`, `schelling_point.py`, `synthetic_control.py`), already verified to reproduce the manuscript's figures during the prior protocol's Stages 1.5–1.6.
- Old data manifest: `lagging-truth-paper-01/data/SOURCES.md` (13 TradingView instruments, fingerprinted to Appendix B.1).

The git timestamps in this repo therefore document **when the port happened**, not when the hypotheses were formed. Honest framing per the Standard's re-design rule: nothing here is confirmatory-by-pre-registration; the empirical targets were known before this repo existed. What the rebuild adds is the Standard's integrity machinery — hashed inputs, claims.lock, verify.py, and the capped adversarial review — applied end to end.

**Known facts carried in (so they are not re-discovered as surprises):**
- EMA-50 must be the normalized `ewm(adjust=True)` form (prior discrepancy D12); the recursive form diverges up to 30 pp.
- NDX is the **cash** NASDAQ-100 index (`NASDAQ_DLY_NDX, 1D_e6961.csv`), not the NQ future (prior discrepancy D11).
- Canary already run (2026-06-09, pre-scaffold): SPX/Hull-50 through the ported decomposition operators gives 260 events / 89.9% aggregate S_W / 60.8% median / 48.1% mean — exact reproduction. SPX input `SP_SPX, 1D_5871b.csv`, SHA-256 `c75e8fb61149f5ba606ebe5a3881db40a1015ff49e322a590cf6e7a7d537cbe7`.

**Subtitle decision.** Adopted the recommended subtitle: "A Proof and Empirical Decomposition of Moving-Average Convergence: Adaptation versus Mean Reversion."

**Commit-order rule honored.** THESIS.md + DESIGN.md land (and are committed) before the first analysis commit in this repo.
