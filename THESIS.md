# THESIS — Moving Averages Follow Price

*Dated: 2026-06-09. Phase 0 of the Research-to-Publication Standard (v1.2).*
*This project is a rebuild of an existing, completed body of work under the new Standard. The thesis below is ported from the v5 manuscript (`Paper1_MA_Adaptation_Core_v5.md`, MD5 `ce836c756e93086252a5ad144147ae46`, dated May 27, 2026); see DECISIONS.md entry 2026-06-09 for the provenance note. The git timestamp of this file documents the port, not an original pre-registration — the science predates this repo.*

## The claim

When a price series deviates from any causal trailing moving average, the subsequent convergence between price and average is predominantly the **mechanical adaptation of the average to price**, not mean reversion of price toward the average.

The core of the claim is algebraic, then empirical:

1. **Algebraic.** A trailing average is computed from past data. After a permanent displacement, each new bar replaces an old-level observation with a new-level one, so the average must converge to price regardless of what price does next. For any weighted moving average satisfying standard non-negativity conditions, 100% of the gap closure after a permanent step is attributable to filter movement and 0% to series movement; under a random walk the aggregate filter share equals 1.
2. **Empirical.** The S_W decomposition splits observed price–MA gap closure into a filter share (C_W, the average moving) and a price share (C_P, price moving back). On real financial data — 44 instrument-filter combinations, 11 instruments, six asset classes, up to 155 years of daily data — the aggregate filter share S_W exceeds 50% on all 44 combinations and exceeds 100% on 33 of 44 (price moved further away while the average converged).

## Why it matters

The moving average is the most widely used analytical tool in financial markets; hundreds of billions in systematically managed assets follow MA-based signals, and price-MA convergence is routinely read as evidence of mean reversion and used in trading strategies, risk models, and valuation frameworks. If the convergence is predominantly the filter's own construction, that inference is unsound: observing convergence, standing alone, is no evidence of any force attracting price to the average. The implications extend beyond finance to any domain where a trailing average is compared to the quantity it tracks.

## The gap

The pieces have existed for ~90 years without being assembled. Slutsky (1937) and Yule (1927) showed moving averages create apparent structure in random data; the macroeconometric literature (Cogley–Nason 1995, Hamilton 2018, Phillips–Jin 2021) developed this critique for **two-sided** filters like Hodrick–Prescott; signal processing (Oppenheim–Willsky, Ehlers 2001) treats trailing-filter step response as a design problem. But no prior work, to our knowledge, has formally **decomposed price–trailing-MA convergence into the respective contributions of price movement and average adaptation**, quantified the mechanical share, and tested it across instruments. The S_W decomposition is that contribution.

## The falsifier

The S_W decomposition attributes the **majority of gap closure to price reversion** — i.e., the mechanical (filter) share comes out **below 50%** — across the tested instruments. Subsidiary falsifiers carried by the supporting results: a systematic next-bar tendency of price to move toward its MA that survives drift adjustment across instruments; synthetic zero-attraction controls showing the aggregate S_W metric is materially biased upward (which would make the elevated real-data shares a metric artifact); or a detectable Schelling-point effect at popular MA windows that the mechanical account cannot absorb.

## Scope and honesty notes carried from the prior iteration

- The claim is scoped to the data examined ("on the data we examine," "predominantly consistent with") — confident humility, not universality.
- Quarterly mean reversion on the S&P 500 (r = −0.28 at 126 days) is real, documented, and operates at a different timescale through a different mechanism; it qualifies rather than contradicts the thesis.
- The one forward-looking finding is volatility prediction: large displacement predicts elevated forward realized volatility (mean Spearman rho +0.54, significant after Bonferroni across 38 tests).
