---
title: |
  Moving Averages Follow Price:\
  A Mathematical Proof and Empirical Validation of the Adaptation Property in Trailing Averages
author: |
  Jae Kim\
  Independent Researcher\
  ORCID: [0009-0005-3260-7880](https://orcid.org/0009-0005-3260-7880)\
  jae@laggingtruth.com
date: |
  *This version: June 10, 2026 (verified rebuild under the Research-to-Publication Standard v1.2)*\
  *Working paper — preliminary; comments welcome.*
license: "CC BY-NC-ND 4.0"
---

## Abstract

We argue that when a time series deviates from any causal trailing average, the subsequent gap closure is, on the data we examine, predominantly consistent with the mechanical adaptation of the average rather than reversion of the series toward the average. The result is algebraic: for any weighted moving average satisfying standard non-negativity conditions and any permanent displacement, the average converges to the new level with 100% of the gap closure attributable to filter movement and 0% to series movement (Lemmas 1–3). We extend this deterministic result to stochastic processes, proving that the aggregate filter share equals 1 under a random walk (Theorem 2) and providing convergence bounds in the adaptation regime for general stationary ergodic processes (Theorem 3). We validate the theory on 44 instrument-filter combinations spanning 11 financial instruments, six asset classes, four continents, and up to 155 years of daily data. The aggregate moving average share of gap closure exceeds 50% on all 44 combinations tested and exceeds 100% (indicating the series moved *further away* while the average converged) on 33 of 44 (75%). The next-bar direction test shows no systematic tendency for price to move toward its moving average: under Hull-50, toward rates cluster near 50% on 8 of 11 instruments with mild attraction (~53%) on three (uncorrected for multiplicity); under SMA-200, three instruments show mild repulsion (~47%), of which only one retains significance after a full-sample drift adjustment. Synthetic random walk and GARCH-calibrated controls confirm the decomposition methodology is approximately unbiased under zero attraction, so the elevated shares observed on real instruments are not metric artifacts. A Schelling Point test across 137 instrument-window-timeframe combinations finds no detectable self-fulfilling prophecy effect at popular moving average windows ($\delta = -0.005$ pp, two-sided $p = 0.78$). Two findings carry forward-looking predictive content: large displacement from the moving average predicts elevated forward realized volatility (Spearman $\rho = +0.54$ average across 11 instruments, positive on all 11; significance levels not corrected for serial dependence), and the S&P 500 shows genuine quarterly mean-reversion ($r = -0.28$ at 126 days), which operates at a different timescale and through a different mechanism than the mechanical adaptation that dominates at shorter horizons. We report, and do not smooth, the qualifications to "predominantly": the aggregate share falls below 50% in 5 of 18 rolling decade-windows on SPX (one negative, 1991–2001), and the modern era (1990–2026) shows mild but statistically significant attraction (toward rate 53.1%, $p = 0.0089$, not adjusted for multiplicity). The adaptation result itself is an attribution of past gap closure, not a forward predictor.

**Keywords:** moving average, mean reversion, mechanical mean reversion, adaptation, trailing average, price dynamics, market microstructure, random walk, volatility prediction, Slutsky-Yule effect, spurious cycles, filter artifacts

**JEL Classification:** C22, C58, G14, G17

## 1. Introduction

The moving average is the most widely used analytical tool in financial markets. An estimated \$300 billion in CTA and systematically managed assets under management pursues trend-following signals (Baltas and Kosowski, 2013), with moving average crossovers and time-series momentum among the most common implementations. The 200-day simple moving average of the S&P 500 alone is watched by millions of investors and cited daily in financial media. The central empirical regularity that motivates this attention is the observation that price appears to "revert to" its moving average after periods of deviation — a pattern interpreted as evidence of mean-reversion and used as the basis for trading strategies, risk models, and valuation frameworks.

We ask a question that, to our knowledge, has not been formally addressed in the academic literature: when price and its trailing moving average converge after a period of deviation, what fraction of the convergence is attributable to the average mechanically adapting to the new price level, and what fraction is attributable to price moving back toward the average?

The answer follows from a straightforward algebraic property. A trailing average is computed from past data. When the most recent observations are at a new level, each subsequent bar replaces an old-level observation with a new-level observation, mechanically moving the average toward the current price. This mechanical convergence occurs regardless of what the series does next — the average must converge even if the series continues moving away. For a permanent step displacement, the average closes 100% of the gap through its own movement, with zero contribution from the series (Lemmas 1–3). For stochastic processes, we prove that the aggregate filter share equals 1 under a random walk (Theorem 2) and provide convergence bounds in the adaptation regime for general stationary processes (Theorem 3).

The underlying mathematics — the step response of a causal linear filter — has been well understood in signal processing for decades (Oppenheim and Willsky, 1997; Brown, 1963) and has been explicitly analyzed in the context of financial filters by Ehlers (2001). That moving averages mechanically lag and then converge to displaced series is a textbook property of linear filters. What we have not seen explicitly recognized in the literature we have surveyed is the implication of this property for the interpretation of price-MA convergence in financial markets: the observation of convergence, standing alone, constitutes no evidence of mean-reversion, because the convergence is a mathematical consequence of how trailing averages are constructed, not evidence of any force attracting price toward the average. To determine whether genuine attraction exists, one must decompose the convergence into its price and filter components — a decomposition we define formally and apply empirically.

This paper aims to connect two literatures that have developed somewhat separately. In macroeconometrics, Slutsky (1937) and Yule (1927) demonstrated that moving averages of random data create apparent cyclical structure — the "Slutsky-Yule effect" — and a substantial subsequent literature has shown that two-sided filters such as the Hodrick-Prescott filter generate spurious dynamics when applied to random walks (Cogley and Nason, 1995; Harvey and Jaeger, 1993; Hamilton, 2018; Phillips and Jin, 2021). In financial economics, the mean-reversion and technical analysis literatures have often interpreted price-MA convergence as evidence of economic forces, with less attention to the filter's own mechanical contribution. Our contribution is to extend the macroeconometric critique of filter artifacts from two-sided (non-causal) filters to the one-sided (causal, trailing) moving averages widely used in financial practice, and to offer a formal decomposition framework that separates mechanical adaptation from any genuine price dynamics.

Our empirical validation spans 11 instruments across equities (S&P 500, NASDAQ-100, Nikkei 225, DAX, FTSE 100, Hang Seng), commodities (crude oil, gold), bonds (10-year Treasury notes), and currencies (Euro FX, Japanese Yen), with data histories ranging from 25 to 155 years. We test multiple moving average specifications (SMA, EMA, Hull, with windows from 20 to 200) and apply an extensive validation battery including in-sample/out-of-sample splits, synthetic controls (both i.i.d. and GARCH-calibrated), parameter sensitivity across eight specifications, era analysis, and permutation tests. The result holds across every dimension we tested.

The paper is organized as follows. Section 2 reviews the related literature, including the Slutsky-Yule tradition and the HP filter critique literature that our work extends. Section 3 presents the mathematical framework, including the proofs for SMA, EMA, general weighted averages, and the Hull Moving Average. Section 4 describes the data and methodology. Section 5 presents the empirical results. Section 6 discusses implications and limitations. Section 7 concludes.

## 2. Related Literature

### 2.1 Mean-Reversion in Financial Markets

The mean-reversion literature begins with Fama and French (1988), who documented negative serial correlation in long-horizon stock returns, and Poterba and Summers (1988), who found similar evidence using variance ratio tests. Subsequent work debated the strength and reliability of these findings, with Lo and MacKinlay (1988) showing that random walk rejection depends on the testing framework. More recently, Balvers et al. (2000) documented mean-reversion across 18 countries using the moving average as the trend estimate, and Narayan and Bannigidadmath (2015) extended these findings using panel methods. Avramov, Kaplanski, and Subrahmanyam (2021) showed that "moving average distance" — the gap between short-run and long-run price MAs — predicts cross-sectional equity returns, attributing the effect to investor anchoring bias rather than filter mechanics.

On our reading, a common thread in this literature is the implicit assumption that when returns are negatively correlated with prior displacement from a moving average (or other trend estimate), this constitutes evidence of a force attracting price toward the trend. Our contribution is to argue that this inference may be incomplete: on the instruments we examine, the mechanical adaptation of the trailing average accounts for the majority of the observed convergence. Whether genuine attraction also operates is a separate question answered by the direction test (Section 5.2), not by the share decomposition; the residual share bounds how much room genuine attraction has, but does not by itself establish its absence. The concept of "mechanical mean reversion" — where an observed statistical pattern reflects arithmetic construction rather than economic behavior — has been identified in corporate finance by Chang and Dasgupta (2009), who showed that leverage ratios mechanically revert even under random financing policies. We identify an analogous phenomenon in the domain of price-MA convergence. The broader tradition of apparent dynamics arising from construction rather than economics is older than our framing acknowledges elsewhere: Working (1960) showed that time-averaging a random chain mechanically induces serial correlation in the first differences of the averaged series, and Miller, Muthuswamy, and Whaley (1994) showed that apparent mean reversion in the S&P 500 index basis is largely a construction artifact rather than an economic force. Our contribution is narrower and complementary — a closure-share decomposition with a falsifiable threshold — but these are direct antecedents in spirit, and the causal-filter side of the artifact question has antecedents we should not overstate as wholly unexamined.

### 2.2 Spurious Cycles and Filter Artifacts

The recognition that statistical filters can create apparent structure in structureless data has a long intellectual history. Slutsky (1937) demonstrated that applying moving averages to purely random sequences produces series with apparent cyclical regularity — the "Slutsky-Yule effect" (see also Yule, 1927). Crucially, Slutsky's original demonstration used a one-sided (trailing) moving average, the same class of filter addressed in this paper. The implication — that moving averages of random data exhibit spurious cyclical structure indistinguishable from genuine dynamics — is the deepest conceptual root of our argument.

Subsequent work in macroeconometrics extended this insight to two-sided (non-causal) filters used in business cycle analysis. Cogley and Nason (1995) showed that the Hodrick-Prescott filter generates apparent business cycle dynamics in artificial data that contain no cyclical component, concluding that the filter can generate business cycle dynamics even when none exist. Harvey and Jaeger (1993) used the phrase "mechanical detrending" to describe the artifacts introduced by HP filtering. Nelson and Kang (1981) demonstrated that even simple linear detrending of a random walk produces artifactual periodicity that can be mistaken for cyclical behavior. Hamilton (2018) provided a comprehensive critique showing that the HP filter produces "spurious dynamic relations that have no basis in the underlying data-generating process," and Phillips and Jin (2021) derived rigorous asymptotic theory explaining why the filter fails to remove stochastic trends, producing remnant trend behavior that researchers mistake for cycles.

While this critique of two-sided filters is well developed, the analogous question for one-sided (trailing) moving averages — the dominant filter in financial practice — has received less attention in our reading of the literature. Shintani, Yabu, and Nagakura (2012) provide the most direct bridge: their paper "Spurious Regressions in Technical Trading" proved that MA-based buy/sell signals (golden and dead crosses) can appear statistically significant under a pure random walk, a result in the Granger-Newbold-Phillips spurious-regression tradition, analogous in spirit to the Slutsky-Yule filter-artifact literature applied to technical analysis. However, their focus was on the spurious *predictability of returns* from crossover signals, not on decomposing the mechanical convergence between price and its MA into component shares. Zakamulin and Giner (2020) showed that under a random walk, different trend-following indicators are correlated above 90% (with EMA-based rule pairs exceeding 80%); we interpret this high shared-structure finding as evidence that most of the apparent signal content of MA-based rules is mechanical rather than genuine market information. Franses (1991) showed that moving-average filtering of a stationary AR(1) process inflates its first-order autocorrelation, biasing standard unit-root tests toward non-rejection of the null. Our contribution extends this filter-artifact tradition from two-sided macro filters and from return predictability to the specific question of price-MA convergence attribution — showing not only that the convergence is predominantly mechanical, but quantifying the mechanical share precisely through the $S_W$ decomposition.

### 2.3 Moving Averages in Technical Analysis

The technical analysis literature treats moving average convergence as evidence of "support" and "resistance" — levels where buying or selling pressure is thought to concentrate. Brock, Lakonishok, and LeBaron (1992) documented that trading rules based on moving average crossovers generate positive excess returns on the Dow Jones Industrial Average, with return patterns that cannot be replicated by several standard null models of the return-generating process. Sullivan, Timmermann, and White (1999) showed that data snooping adjustments weaken but do not eliminate this finding. Brock et al. (1992) report that a wide range of MA window choices from 50 to 200 days generate qualitatively similar results — an observation consistent with, though not a formal test of, the null hypothesis that the specific window choice does not matter. LeBaron (2000) reports that the window-stability property appears to break down in post-1986 sub-samples of the Dow Jones data. Osler (2003) argued that the self-fulfilling prophecy mechanism — millions of traders watching the same round-number MAs — creates genuine order-flow clustering at these levels.

Our Schelling Point test (Section 5.9) directly addresses the self-fulfilling prophecy hypothesis. We note an important distinction between Osler's (2003) finding and the hypothesis we test: Osler demonstrated that stop-loss and take-profit orders cluster at round *price* levels (e.g., rates ending in 00, such as ¥100/\$); we interpret these round levels as Schelling points in price space. The self-fulfilling prophecy claim for moving averages posits Schelling points in *parameter* space — that the 200-day MA produces different behavior from the 197-day or 203-day MA because more traders watch it. Our test compares toward rates at popular MA windows (20, 50, 100, 200) to their arbitrary neighbors (±3, ±5 periods) across 137 combinations spanning 13 instruments and four timeframes, finding no detectable differential effect.

### 2.4 Connection to Signal Processing

The step-response behavior of causal linear filters — how a filter output converges to a new constant input level — is well-established in the signal processing literature. Oppenheim and Willsky (1997) provide the standard textbook treatment of linear filter theory, including the unity DC gain property that guarantees any properly normalized causal filter will eventually track a constant input. Brown (1963) analyzed exponential smoothing convergence in the context of forecasting. In the financial application of signal processing, Ehlers (2001) explicitly analyzed and plotted the step responses of SMA and EMA filters after price displacements, recognizing the lag and convergence behavior as an engineering problem to overcome through filter design (e.g., zero-lag filters). The HMA itself (Hull, 2005) was designed to reduce this lag through a differencing construction that produces negative effective weights.

What these signal processing treatments share is a focus on the convergence behavior as a *filter design problem* — something to minimize in pursuit of a more responsive indicator. Our contribution is to argue that this convergence behavior, often interpreted in financial economics as evidence of *economic mean-reversion*, may be substantially accounted for by the filter's own dynamics. The step-response mathematics in Lemmas 1–4 are not new in isolation; what is new is the explicit connection between filter convergence and the mean-reversion attribution problem, the formal $S_W$ decomposition framework, and empirical validation suggesting that the filter's mechanical contribution accounts for most of the gap closure on the financial data we examine.

### 2.5 The Gap in the Literature

While these intellectual traditions converge — the Slutsky-Yule effect demonstrating that filters create apparent structure in random data, the HP filter critique showing that two-sided filter artifacts can be misinterpreted as economic dynamics, and signal processing providing the mathematical framework for filter convergence — to our knowledge, no prior work has formally decomposed the convergence between price and its trailing moving average into the respective contributions of price movement and average adaptation. The pieces for this decomposition have been available for nearly 90 years; we offer one such decomposition here. Our $S_W$ metric — the filter's share of gap closure — provides this decomposition, with a formal proof establishing $S_W = 1$ under deterministic displacement and empirical validation across 44 instrument-filter combinations.

## 3. Mathematical Framework

### 3.1 Notation and Definitions

Let $\{P(t)\}_{t \in \mathbb{Z}}$ be a discrete-time stochastic process representing the log price of a financial asset. We consider a general class of causal linear filters (trailing moving averages) defined as follows.

**Definition 1 (Weighted Moving Average).** A causal weighted moving average of order $N$ is a linear operator $W_N$ that maps the price process to a smoothed process:

$$W_N[P](t) = \sum_{k=0}^{N-1} w_k \cdot P(t-k)$$

where $\{w_k\}_{k=0}^{N-1}$ are non-negative weights satisfying $\sum_{k=0}^{N-1} w_k = 1$, and $w_k \geq 0$ for all $k$. The causality condition ensures the filter uses only past and current data.

**Definition 2 (Specific Cases).** The Simple Moving Average (SMA) sets $w_k = 1/N$ for all $k$. The Exponential Moving Average (EMA) with parameter $\alpha \in (0,1)$ sets $w_k = \alpha(1-\alpha)^k / [1-(1-\alpha)^N]$, which in the limit $N \to \infty$ yields the standard infinite-window EMA with $w_k = \alpha(1-\alpha)^k$. The Hull Moving Average (HMA) is a composition of weighted moving averages described in Definition 5 below.

**Definition 3 (Displacement).** The displacement at time $t$ is $x(t) = P(t) - W_N[P](t)$. We say the system is in a state of positive displacement when $x(t) > 0$ and negative displacement when $x(t) < 0$.

**Definition 4 (Gap-Closure Decomposition).** For any displacement event at time $t_0$ with forward horizon $H$, the gap change decomposes as:

$$\Delta x = x(t_0+H) - x(t_0) = \Delta P - \Delta W$$

where $\Delta P = P(t_0+H) - P(t_0)$ is the price contribution and $\Delta W = W_N[P](t_0+H) - W_N[P](t_0)$ is the filter contribution. We define the signed contributions to gap closure as:

$$C_P(t_0, H) = -\mathrm{sgn}(x(t_0)) \cdot \Delta P$$

$$C_W(t_0, H) = \mathrm{sgn}(x(t_0)) \cdot \Delta W$$

Both quantities are positive when they contribute to reducing $|x|$. The filter's share of gap closure is:

$$S_W(t_0, H) = \frac{C_W}{C_P + C_W}$$

when $C_P + C_W \neq 0$. An $S_W$ of $1$ (100%) indicates the gap closed entirely through filter movement; $S_W > 1$ indicates price moved further away while the filter converged.

### 3.2 Adaptation Under Deterministic Displacement

We first establish the result for a deterministic price process, then extend to the stochastic case.

**Lemma 1 (SMA Adaptation — Step Displacement).** Let $P(t) = P_0$ for $t < 0$ and $P(t) = P_0 + J$ for $t \geq 0$, where $J \neq 0$. Then for the SMA of window $N$:

(i) $\mathrm{SMA}_N(k) = P_0 + J \cdot \min(k+1, N) / N$ for all $k \geq 0$.

(ii) $x(k) = J \cdot (N-k-1)/N$ for $0 \leq k \leq N-1$, and $x(k) = 0$ for $k \geq N$.

(iii) The gap closes completely at $k = N-1$.

(iv) $S_W(0, k) = 1$ for all $0 < k \leq N-1$.

*Proof.* For $k \geq 0$, the SMA window $\{P(k), P(k-1), \ldots, P(k-N+1)\}$ contains $\min(k+1, N)$ observations at the new level $P_0 + J$ and $\max(N-k-1, 0)$ observations at the old level $P_0$. Thus:

$$\mathrm{SMA}_N(k) = \frac{1}{N}\bigl[\min(k+1,N) \cdot (P_0+J) + \max(N-k-1,0) \cdot P_0\bigr] = P_0 + J \cdot \frac{\min(k+1,N)}{N}$$

The price contribution is $\Delta P = P(k) - P(0) = 0$ for all $k \geq 0$. The filter contribution is $\Delta W = Jk/N$. Since $\Delta P = 0$, we have $S_W = 1$ for all $k > 0$. ∎

**Lemma 2 (EMA Adaptation — Step Displacement).** Under the same price process, for the EMA with parameter $\alpha \in (0,1)$:

(i) $\mathrm{EMA}(k) = P_0 + J \cdot [1 - (1-\alpha)^{k+1}]$ for all $k \geq 0$.

(ii) $x(k) = J \cdot (1-\alpha)^{k+1}$, which decays geometrically with ratio $(1-\alpha)$.

(iii) The half-life of convergence is $t_{1/2} \approx 0.347N$ for the standard parametrization $\alpha = 2/(N+1)$.

(iv) $S_W(0, k) = 1$ for all $k > 0$.

*Proof.* The EMA recursion $\mathrm{EMA}(k) = \alpha \cdot P(k) + (1-\alpha) \cdot \mathrm{EMA}(k-1)$ with $P(k) = P_0 + J$ for $k \geq 0$ yields, by induction, $\mathrm{EMA}(k) = P_0 + J[1-(1-\alpha)^{k+1}]$. Since $\Delta P = 0$, $S_W = 1$ identically. ∎

**Lemma 3 (General Weighted Average — Step Displacement).** Under the same price process, for any causal weighted moving average $W_N$ with weights $\{w_k\}$ satisfying Definition 1:

(i) $W_N[P](k) = P_0 + J \cdot \sum_{j=0}^{\min(k,N-1)} w_j$ for all $k \geq 0$.

(ii) $x(k) = J \cdot \sum_{j=\min(k,N-1)+1}^{N-1} w_j$.

(iii) For $k \geq N-1$: $x(k) = 0$. The gap closes completely in at most $N-1$ periods.

(iv) $S_W(0, k) = 1$ for all $k > 0$.

*Proof.* At time $k \geq 0$, $W_N[P](k) = \sum_{j=0}^{N-1} w_j \cdot P(k-j)$. For $j \leq k$, $P(k-j) = P_0 + J$; for $j > k$, $P(k-j) = P_0$. Thus $W_N[P](k) = P_0 + J \cdot \sum_{j=0}^{\min(k,N-1)} w_j$. Part (iv) follows because $\Delta P = 0$. ∎

**Remark 1.** Lemmas 1–3 establish that for any causal weighted average satisfying Definition 1 and any permanent displacement, the gap closes through 100% filter adaptation and 0% series contribution. This is a purely algebraic fact independent of any assumption about market dynamics. The result is the one-sided (causal) analog of the well-known property that two-sided filters create spurious cyclicality in random walks (Cogley and Nason, 1995). The key difference is that for causal filters the convergence is asymmetric — the filter converges toward the series, not vice versa — which makes the decomposition into price and filter contributions both well-defined and economically interpretable.

### 3.3 The Hull Moving Average

**Definition 5 (Hull Moving Average).** The Hull Moving Average of window $N$ is defined as:

$$\mathrm{HMA}_N(t) = \mathrm{WMA}_{\lfloor\sqrt{N}\rfloor}\bigl[2 \cdot \mathrm{WMA}_{\lfloor N/2\rfloor}[P](t) - \mathrm{WMA}_N[P](t)\bigr]$$

where $\mathrm{WMA}_M$ denotes the Weighted Moving Average of window $M$ with linearly decreasing weights $w_k = (M-k) / [M(M+1)/2]$.

**Lemma 4 (HMA Adaptation — Step Displacement).** Under a step displacement from $P_0$ to $P_0 + J$, the HMA converges to $P_0 + J$ in at most $(N-1) + (\lfloor\sqrt{N}\rfloor-1)$ periods. The filter share $S_W = 1$ throughout.

*Proof.* The HMA's intermediate differencing step $(2 \cdot \mathrm{WMA}_{N/2} - \mathrm{WMA}_N)$ produces negative effective weights on older observations, violating Definition 1's non-negativity requirement. However, $S_W = 1$ depends only on $\Delta P = 0$, not on the sign of the weights. Convergence follows from the composition: by Lemma 3, $\mathrm{WMA}_{\lfloor N/2\rfloor}$ and $\mathrm{WMA}_N$ each converge to $P_0+J$ after $\lfloor N/2\rfloor-1$ and $N-1$ bars respectively, so by linearity the intermediate quantity $2 \cdot \mathrm{WMA}_{\lfloor N/2\rfloor} - \mathrm{WMA}_N$ stabilizes at $2(P_0+J) - (P_0+J) = P_0+J$ from bar $N-1$ onward. This constant value feeds the outer $\mathrm{WMA}_{\lfloor\sqrt{N}\rfloor}$, which converges within a further $\lfloor\sqrt{N}\rfloor-1$ periods. ∎

### 3.4 Extension to General Stochastic Processes

**Theorem 1 (Decomposition Identity).** For any price process $\{P(t)\}$, any causal linear filter $W$, any time $t_0$, and any forward horizon $H > 0$:

$$x(t_0+H) - x(t_0) = [P(t_0+H) - P(t_0)] - [W_N[P](t_0+H) - W_N[P](t_0)]$$

This identity holds pathwise and requires no distributional assumptions.

**Theorem 2 (Aggregate Filter Share Under Random Walk).** Let $\{P(t)\}$ be a random walk with i.i.d. increments having mean $\mu$ and variance $\sigma^2$. For the SMA of window $N$ and forward horizon $H \geq N$, conditional on a displacement event $x(t_0) = d \neq 0$:

$$\mathbb{E}[\Delta W \mid x(t_0)=d] = \mu[H - (N-1)/2] + d, \qquad \mathbb{E}[\Delta P \mid x(t_0)=d] = \mu H.$$

Under zero drift ($\mu = 0$), the aggregate filter share — the population ratio $\mathbb{E}[C_W] / \mathbb{E}[C_W + C_P]$ that the empirical methodology of Section 4.2 estimates — equals $1$ exactly. For $\mu \neq 0$, the price contribution $\mathbb{E}[C_P] = -\mathrm{sgn}(d) \cdot \mu H$ is bounded while $|d| \to \infty$, so the aggregate share $\to 1$.

*Proof.* For $H \geq N$, the SMA windows at $t_0$ and $t_0+H$ share no observations. Conditional on $x(t_0) = d$, future prices are independent of the past by the Markov property of the random walk. Direct moment calculations yield $\mathbb{E}[\Delta W \mid x(t_0)=d] = \mu[H - (N-1)/2] + d$ and $\mathbb{E}[\Delta P \mid x(t_0)=d] = \mu H$. Under $\mu = 0$: $\mathbb{E}[C_W] = \mathrm{sgn}(d) \cdot \mathbb{E}[\Delta W] = |d|$ and $\mathbb{E}[C_P] = -\mathrm{sgn}(d) \cdot \mathbb{E}[\Delta P] = 0$, giving $\mathbb{E}[C_W] / \mathbb{E}[C_W + C_P] = 1$ exactly. ∎

**Remark 2.** The aggregate share $\mathbb{E}[C_W] / \mathbb{E}[C_W + C_P]$ (a ratio of expectations) and the expected individual share $\mathbb{E}[S_W]$ (an expectation of a ratio) are distinct quantities by Jensen's inequality. A second-order Taylor expansion in the noise components of $\Delta W$ and $\Delta P$ yields $\mathbb{E}[S_W] \approx 1 + \sigma^2(N-1)/(2d^2)$ for large $d$, so the expected individual share is slightly above $1$ even under zero attraction and converges to $1$ only in the limit $d^2/(\sigma^2 N) \to \infty$. This distinction motivates Section 5.1's reporting of both the aggregate (a finite-sample estimator of the population aggregate, which converges to $1$ by the law of large numbers) and the median $S_W$ (a robust summary closer in spirit to $\mathbb{E}[S_W]$).

**Theorem 3 (Adaptation Bound, Adaptation Regime).** Let $\{P(t)\}$ have stationary ergodic innovations with mean $\mu$ and variance $\sigma^2$. For SMA of window $N$ and forward horizon $0 \leq T \leq N$:

$$|\mathrm{SMA}_N(t_0+T) - P(t_0)| \leq |J| \cdot \max\bigl(1 - (T+1)/N,\, 0\bigr) + |\mu| \cdot T + O_P(\sigma\sqrt{N})$$

where $J = x(t_0)$. The first term represents deterministic convergence (vanishing for $T \geq N-1$), the second accounts for drift, and the third represents irreducible noise from ongoing price fluctuations.

**Corollary 1 (Generality of the Decomposition).** Theorem 1 holds for any causal linear filter, any price process, and any displacement threshold. The deterministic convergence results (Lemmas 1–4) hold for all filters under step displacement. Theorem 2 is proved for SMA under random walk; empirical synthetic controls are consistent with the result extending to other filters and shorter horizons.

**Corollary 2 (Insufficiency of Gap Closure as Evidence).** The observation that price and its trailing average converge after a displacement event is insufficient to establish the existence of a mean-reverting force. Such convergence follows from the algebraic properties of the average and occurs identically for random walks with zero attraction. To distinguish mechanical adaptation from any genuine attraction, the decomposition (Definition 4) is necessary.

### 3.5 Convergence Rate Comparison Across Filter Types

All formulas use the inclusive convention (current price is part of the average).

**SMA of window $N$:** Linear convergence. $x(k) = J(N-k-1)/N$. Complete convergence at $k = N-1$.

**EMA with $\alpha = 2/(N+1)$:** Geometric convergence. $x(k) = J(1-\alpha)^{k+1}$. Half-life $\approx 0.347N$. Time to 95% closure $\approx 1.50N$.

**WMA (linearly weighted) of window $N$:** Faster-than-linear convergence. $x(k) = J(N-k-1)(N-k)/[N(N+1)]$.

**HMA of window $N$:** Fastest convergence with possible transient overshoot. Complete convergence in at most $(N-1) + (\lfloor\sqrt{N}\rfloor-1)$ periods.

In all cases, $S_W = 1$ under deterministic displacement. The convergence rate determines how quickly the filter adapts in the stochastic setting: faster filters produce higher $S_W$ over short horizons; all achieve $S_W \to 1$ asymptotically.

### 3.6 Implications for the Ornstein-Uhlenbeck Specification

The standard Ornstein-Uhlenbeck model for mean-reversion, $dx(t) = -\theta \cdot x(t) \cdot dt + \sigma \cdot dW(t)$, estimates a "speed of reversion" $\theta$ that may conflate two distinct forces: the mechanical adaptation of the average (established by Lemmas 1–4) and any genuine economic force attracting price toward the average. Our empirical results suggest that force (a) accounts for the majority of aggregate gap closure on most instruments tested, with the aggregate MA share exceeding 90% on 37 of 44 combinations. For the EMA, the mechanical adaptation produces an AR(1) displacement process with coefficient $(1-\alpha)$, corresponding to a discrete-time reversion speed of $\alpha$ per period. When the estimated $\theta_{\mathrm{obs}}$ is close to $\theta_{\mathrm{mech}}$, the observed reversion is consistent with mechanical adaptation alone.

This confounding is related to, but distinct from, the finding of Franses (1991) that moving-average filtering of a stationary AR(1) process inflates its first-order autocorrelation, biasing unit-root tests toward non-rejection of the null. Our result identifies the specific mechanism by which trailing-MA filtering produces apparent mean-reversion in the displacement process $x(t) = P(t) - \mathrm{MA}(t)$, and provides a formal decomposition to quantify the mechanical and genuine components separately. Researchers using OU or related models with trailing-average benchmarks should either account for the mechanical component explicitly or use non-trailing-average benchmarks (e.g., fundamental value estimates) to measure displacement.

## 4. Data and Methodology

### 4.1 Data

We use daily closing price data for 11 instruments spanning six asset classes, four continents, and up to 155 years of history.

The equity sample comprises the S&P 500 (SPX, 1871–2026, 25,187 observations), NASDAQ-100 cash index (NDX, 1985–2026, 10,359 observations), Nikkei 225 (1949–2026), DAX (1970–2026), FTSE 100 (1995–2026), and the Hang Seng front-month future (HSI, 1987–2026; the pinned series is the HKEX front-month contract, not the cash index). The commodity sample includes crude oil front-month futures (CL, 1983–2026) and gold front-month futures (GC, 1975–2026). The fixed income sample is 10-year Treasury Note futures (ZN, 1982–2026). The currency sample includes Euro FX futures (6E, 2000–2026) and Japanese Yen futures (6J, 2000–2026).

All data are sourced from TradingView export files. The SPX series extends to 1871 using a reconstructed historical index; bars prior to 1926 derive from lower-frequency (monthly) sources, so the early SPX history carries a documented monthly-to-daily frequency transition. We therefore report the pre-1930 era but do not interpret it (3 qualifying events; Section 5.5), and a registered ex-1926 decomposition variant is noted as future work rather than claimed here. All prices are converted to natural logarithms before analysis; the single non-positive close in the sample (crude oil front-month, 2020-04-20) is dropped prior to the log transform (Appendix B.1).

### 4.2 Decomposition Methodology

For each instrument and MA specification, we compute the moving average of log prices, the signed displacement $x(t) = \log P(t) - \mathrm{MA}(t)$, and the expanding 75th percentile of $|x|$ as the threshold for "substantial deviation" (using only data available at each point in time — no look-ahead). We identify displacement events where $|x(t)|$ exceeds this threshold, measure the forward price change and forward MA change over a 63-trading-day horizon, and compute the price contribution $C_P$, MA contribution $C_W$, and MA share $S_W$. Events are spaced at least 63 days apart to ensure non-overlapping forward windows.

The main decomposition uses four MA specifications — Hull-50, SMA-50, SMA-200, and EMA-50 — applied to all 11 instruments, yielding 44 instrument-filter combinations. These four were selected to span the filter-speed spectrum (fast: Hull-50; medium: SMA-50, EMA-50; slow: SMA-200) and the three most common filter types (SMA, EMA, Hull). An additional four specifications — Hull-20, Hull-100, SMA-20, SMA-100 — are tested on SPX only as a parameter sensitivity check (Section 5.4), bringing the total SPX specifications to eight.

### 4.3 Direction Test

Independently of the decomposition, we test whether price shows any systematic tendency to move toward or away from the MA on the next bar. For each qualifying displacement event, we record whether the next day's return moves price toward the MA (reducing $|x|$) or away. Under the null of zero attraction and zero drift, the toward rate should be 50%. We note that positive drift biases the toward rate below 50% for long-only assets, making the test conservative for detecting attraction.

### 4.4 Synthetic Control

We apply the identical methodology to 20 synthetic random walks of 25,000 observations each (i.i.d. normal returns, zero autocorrelation). These have zero attraction by construction — any systematic pattern indicates a methodological artifact. We additionally fit GARCH(1,1) models with Student-t innovations to nine of the eleven instruments' return series (CL and GC are excluded because their fitted models are integrated, $\alpha_1 + \beta_1 \geq 1$; see Appendix B.5) and generate 20 synthetic paths per included instrument, for 180 total GARCH paths, retaining zero return autocorrelation while matching realistic volatility dynamics.

### 4.5 Parameter Sensitivity

We test eight MA specifications: Hull-20, Hull-50, Hull-100, SMA-20, SMA-50, SMA-100, SMA-200, and EMA-50. We also test threshold sensitivity (50th, 75th, and 90th percentiles), horizon sensitivity ($H = 21, 63, 126, 252$ days), filter-matched horizons, spacing sensitivity (all 63 starting offsets), drift-adjusted direction tests, and log versus level prices.

### 4.6 Validation Battery

We apply in-sample/out-of-sample splits (chronological midpoint), rolling 10-year decomposition windows, and a PE-volatility correlation test with direct permutation tests (5,000 shuffles) and Bonferroni correction across 38 tests. The PE-volatility correlation measures whether displacement from the moving average predicts forward realized volatility — a finding that depends on the same displacement measurement as the adaptation hypothesis.

### 4.7 Schelling Point Test

To test whether the self-fulfilling prophecy drives price-MA convergence, we compare the next-bar toward rate at popular SMA windows (20, 50, 100, 200) to their arbitrary neighbors (±3, ±5 periods). The Schelling point premium $\delta = \mathrm{toward\_rate}(\mathrm{popular}) - \mathrm{mean}(\mathrm{toward\_rate}(\mathrm{neighbors}))$ should be positive if clustered order flow at round-number MAs creates genuine support/resistance. This test controls for drift bias and autocorrelation bias because both affect popular and neighbor windows nearly equally. We apply this across 137 valid combinations spanning 13 instruments, four timeframes (daily, hourly, 5-minute, monthly), using expanding thresholds with no look-ahead.

## 5. Results

### 5.1 Decomposition: Aggregate vs Individual-Event Results

The aggregate MA share — computed as the ratio of total $C_W$ to total $(C_P + C_W)$ across all events — ranges from 63.5% (HSI, Hull-50) to 166.8% (NDX, SMA-200) {{LB-003}} across 44 instrument-filter combinations; all 44 exceed 50% {{LB-001}}. Thirty-three of 44 combinations (75%) exceed 100% {{LB-002}}, indicating that on net, price moved further away from the MA while the MA converged. The lowest aggregate shares occur with faster filters on instruments with shorter histories or higher volatility, consistent with the mathematical prediction that faster filters complete their adaptation within the 63-day measurement window, leaving less residual convergence to measure. The 44-cell count is a set of point estimates around a null center of 100% (Theorem 2), not 44 independent confirmations; short-history instruments (6E, 6J, FTSE) carry larger sampling error — the synthetic battery's path-level standard deviation is ~13.9 pp — so individual cells near the boundary should be read with that spread in mind. Exceeding the 100% null center on 33 of 44 cells reflects within-window drift or continuation rather than additional filter-mechanics evidence.

The aggregate statistic masks substantial dispersion at the event level. On SPX with Hull-50 (260 events), the aggregate $S_W$ is 89.9% {{LB-004}}, the median is 60.8%, and the arithmetic mean of individual events is 48.1%. The $S_W$ distribution is wildly non-normal (IQR of $-111\%$ to $+209\%$) because events with near-zero total closure produce extreme $S_W$ values. The divergence between aggregate and median statistics arises because the aggregate (ratio of sums) weights events by magnitude while the median treats all events equally. Both statistics are valid summaries of different aspects of the data; we report both for transparency.

Synthetic random walks produce an aggregate MA share of 103.9% across twenty 25,000-observation paths (seed 42); a larger-sample run (200 zero-drift series) confirms the aggregate-$S_W$ metric is approximately unbiased at $\sim$100% under zero attraction (sample mean 100.57%, SE 0.89 pp), so the single-batch figure is sampling variation rather than a systematic metric bias (Section 5.3).

### 5.2 Direction Test

*Inferential note: the drift adjustment below uses the full-sample fraction of positive returns as its null, so it is a descriptive in-sample correction rather than a quantity available to a trader at time $t$; it does not enter event selection or any $S_W$ value. The toward-rate findings are statements about the realized sample and are reported uncorrected for multiplicity across instruments, specifications, and eras (correcting would weaken the already-mild attraction findings, which cut against the thesis).*

For the Hull-50 specification, three instruments show statistically significant attraction at $p < 0.05$: HSI (53.2%), GC (52.9%), and 6E (53.9%). The remaining eight instruments are indistinguishable from 50% {{LB-005}}. For the SMA-200 specification, three instruments show significant repulsion: SPX (47.8%), Nikkei (45.8%), and NDX (47.0%). After drift adjustment, 2 of these 3 flip to random, with only Nikkei retaining significant repulsion ($z = -4.08$, $p < 0.0001$) {{LB-006}}.

The key finding is that toward rates cluster near 50% — we observe no strong or broad tendency for price to move toward its moving average. Where mild attraction exists (~53%), it is insufficient to account for the observed gap closure; the MA's mechanical adaptation remains the larger contributor on the instruments tested.

### 5.3 Synthetic Control

*The synthetic null is calibrated with the Hull-50 specification. The eleven SMA-200 cells measured at $H = 63$ violate the $H \geq N$ condition of Theorem 2 (the two windows overlap), so those cells rest on Corollary 1 together with the Hull-50 null rather than a specification-matched synthetic null; a SMA-200 synthetic-null run is noted as future work. This does not affect the headline (all 44 cells exceed 50%); it qualifies the $>100\%$ reading for those specific cells.*

The 20 i.i.d. normal random walks (25,000 observations each) produce a mean aggregate MA share of 103.9% (SD 13.9 pp across paths), and a 200-series zero-drift battery centers the metric at 100.57% with a standard error of 0.89 pp {{LB-007}} — consistent with the mathematical proof's prediction of $\sim$100% for a zero-attraction system. The GARCH-calibrated controls (180 simulations: 20 paths for each of the 9 instruments with stationary fitted models) produce a mean aggregate $S_W$ of 99.1% {{LB-008}}, statistically indistinguishable from the i.i.d. benchmark. On the GARCH-calibrated controls we ran, volatility clustering, fat tails, and time-varying volatility produce no detectable effect on the decomposition aggregate.

### 5.4 Parameter Sensitivity

On SPX, the MA share exceeds 89% for all eight MA specifications tested (range: 89.9% to 114.2%) {{LB-012}}. Threshold sensitivity shows positive results at all three percentile levels (50th, 75th, 90th), with the 75th percentile being intermediate {{LB-013}}. Horizon sensitivity — run on the eleven-instrument robustness set, in which the NQ E-mini future stands in for the NDX cash index (Appendix B.14) — shows aggregate $S_W$ above 50% on all 11 instruments at $H = 21$ and $H = 63$, on 10 of 11 at $H = 126$, and 8 of 11 at $H = 252$ {{LB-014}}; the sub-50% cells (FTSE at $H = 126$; SPX, ZN, and 6J at $H = 252$, the last with a negative aggregate) are reported in the repository output. Filter-matched horizons address the concern that fixed $H = 63$ inflates slower-filter results: the cross-instrument mean of SMA-200's aggregate (across the eleven-instrument set, distinct from the SPX-specific eight-spec range above) in fact increases from 114.6% at $H = 63$ to 127.8% at $H = 200$ {{LB-016}}. Spacing sensitivity across all 63 possible starting offsets on SPX produces aggregate $S_W$ ranging from 88.3% to 90.0% (standard deviation 0.21 pp) {{LB-015}}. Log versus level prices produce qualitatively identical results.

**Calibration of the 50% falsifier.** Because the thesis is falsified by aggregate $S_W < 50\%$, it matters how much genuine attraction is required to drive the metric there. We calibrate this on the decomposition operator itself (`analysis/falsifier_calibration.py`): synthetic log-price paths are generated with an explicit, tunable daily pull $\beta$ toward a trailing mean, and the unmodified decomposition is applied at $H = 63$. Aggregate $S_W$ is monotone decreasing in the injected attraction and crosses 50% at a finite pull ($\beta \approx 0.087$, a displacement half-life of roughly 8 trading days): $S_W \approx 92$–$100\%$ at zero attraction, $\approx 58\%$ at $\beta = 0.03$, $\approx 52\%$ at $\beta = 0.08$, and $\approx 33\%$ at $\beta = 0.20$ {{LB-021}}. The falsifier is therefore reachable by a sufficiently strong reversion process, not merely rhetorical. The same calibration expresses the bar in direction-test units: the B.4 next-bar toward rate is $\approx 50\%$ at $\beta = 0$ (as independence requires) and rises smoothly with attraction, reaching $\approx 57.5\%$ at the $S_W$ crossing — so falsification corresponds to a sustained toward rate near 57.5%, whereas the observed full-sample toward rates are 47–54% (Section 5.2) and the observed aggregates of roughly 90–167% map to the $\beta \lesssim 0.01$ region of the curve. The two statistics are thus mutually consistent and jointly informative against even moderate attraction at this horizon. (An earlier revision of this paragraph mislabeled a filter-inclusive gap-shrink statistic — which exceeds 50% under a random walk because the average adapts every bar — as the toward rate; the error was caught in adversarial review and is corrected here, with both statistics now reported under their proper names in the calibration output.)

### 5.5 Era Analysis

SPX era-specific results, obtained by binning the full-history event chain of Section 5.1 into eras under a span rule (an event belongs to an era only if both its trigger date and its 63-day horizon completion fall inside the era; Appendix B.9): 1930–1960 ($S_W = 86.8\%$, 63 events), 1960–1990 (70.8%, 88 events), 1990–2026 (80.6%, 104 events) {{LB-017}}. The pre-1930 era (1871–1929) contains only 3 qualifying events ($S_W = 307.7\%$) and is reported but not interpreted. Era counts need not sum to the 260-event total of Section 5.1 because events whose horizons cross an era boundary belong to no era. The MA share is substantially above 50% in every era with sufficient data. The modern era (1990–2026) shows mild but significant attraction to the Hull-50 MA (toward rate 53.1% over 1,832 qualifying observations, $p = 0.0089$) {{LB-018}}, but even in this era the decomposition shows the MA performing 80.6% of gap-closure work.

### 5.6 In-Sample/Out-of-Sample Validation

Each instrument's data were split at the chronological midpoint. The aggregate $S_W$ exceeds 50% in both halves on all 13 instruments tested (the eleven-instrument robustness set plus ES and NKD futures). The mean aggregate across first halves is 106.3% and across second halves is 100.9%, showing no systematic degradation over time {{LB-020}}. Rolling 10-year windows on SPX show aggregate $S_W$ exceeding 50% in 13 of 18 windows (72%) {{LB-019}}; the five windows below 50% are 1941–1951 (41.4%), 1956–1966 (47.7%), 1986–1996 (8.1%), 1991–2001 ($-8.0\%$, the only negative window), and 2006–2016 (16.9%). The mechanical share is therefore not uniform across decades — extended sub-periods exist, concentrated in 1986–2016, in which price movement dominated the gap closure — while the aggregate, era-level, and split-half results all remain above 50%.

### 5.7 PE-Volatility Correlation

The paper's most statistically robust empirical finding is that displacement from the moving average predicts elevated forward realized volatility. The Spearman rank correlation between the expanding percentile of displacement magnitude and forward 21-day annualized volatility averages $+0.541$ across all 11 instruments, with a minimum of $+0.448$ and a maximum of $+0.626$. The sign test (11/11 positive) yields $p = 0.00098$. After Bonferroni correction for 38 tests (11 instruments $\times$ 3 correlations each [full-sample, IS, OOS] = 33, plus 5 permutation tests), all 38 remain significant {{LB-009}}. The 33 Spearman correlation tests have parametric $p$-values below $2 \times 10^{-6}$ on every instrument and sub-sample; the 5 permutation tests (5,000 shuffles each) yield $p < 0.0002$ on all five, with no shuffled correlation exceeding the real value in any trial. All 38 $p$-values fall well below the Bonferroni-corrected threshold of $0.05/38 = 0.00132$. We caveat these significance levels: displacement and forward volatility are both serially persistent, so the parametric Spearman $p$-values and the single-shuffle permutation are anti-conservative under joint serial dependence. The robust statement is the effect's sign and magnitude (positive on all 11 instruments and all sub-samples, $\rho \approx +0.54$); a block-permutation re-estimate (block length $\geq 63$ bars) is noted as future work. The effect is in any case the well-documented persistence of volatility, for which we offer a model-free displacement metric, not a new phenomenon.

This finding is in line with the adaptation theorem. When price deviates far from its trailing average, the subsequent convergence — whether through price reversal, average catch-up, or some combination — would tend to produce elevated price movement relative to the recent baseline. The trailing volatility measure — of the kind that, to the extent it enters options pricing, would reflect the pre-deviation regime — may underestimate the forward volatility during the convergence process.

We note that the displacement-volatility correlation is substantially consistent with the well-known persistence of volatility documented since Mandelbrot (1963) and formalized in the ARCH/GARCH framework (Engle, 1982; Bollerslev, 1986). When the price-MA gap is large, recent absolute returns have typically been large, and we read the autocorrelation of volatility as sustaining forward volatility at elevated levels. The contribution here is not the discovery of a new phenomenon but rather a clean, intuitive, cross-instrument metric for capturing it: displacement from the trailing average provides a simple, model-free measure of the volatility regime that is directly connected to the adaptation theorem's predictions. The closest prior work is Avramov, Kaplanski, and Subrahmanyam (2021), who used MA displacement as a cross-sectional *return* predictor attributed to anchoring bias; our finding extends MA displacement to *volatility* prediction with a mechanical rather than behavioral explanation.

The PE-volatility correlation is distinct from the main adaptation finding in an important respect: the adaptation finding documents what *has already happened* (the average did most of the convergence work), while the PE-volatility correlation makes a *forward-looking prediction* (displacement predicts future volatility). The latter is empirically testable on purely out-of-sample data and has potential practical applications for volatility forecasting and options pricing.

### 5.8 Qualification: Genuine Quarterly Reversion on SPX

Using strictly non-overlapping windows, signed displacement on SPX shows significant negative correlation with forward returns at quarterly horizons: $r = -0.095$ at 21 days ($p = 0.001$), $r = -0.195$ at 63 days ($p = 0.0001$), and $r = -0.278$ at 126 days ($p = 0.0001$) {{LB-011}}. This is genuine mean-reversion — it is not explained by the mechanical adaptation mechanism.

This quarterly reversion is specific to SPX. On Nikkei and Gold, non-overlapping correlations across all horizons range from $r = -0.054$ to $+0.163$, none reaching significance. The quarterly reversion may reflect US-equity-specific factors such as Federal Reserve policy response or institutional rebalancing.

The existence of quarterly reversion on SPX does not undermine the adaptation findings. The two operate at different timescales: adaptation follows from the algebraic properties of the filter and operates continuously, while quarterly reversion is an empirical regularity specific to US equities operating at 3–6 month horizons. Both can hold simultaneously. The horizon sensitivity analysis (Section 5.4) suggests the crossover point — where cumulative quarterly reversion accounts for more of the observed pattern than mechanical adaptation — at approximately $H = 197$ days on SPX.

### 5.9 Schelling Point Test

Across 137 valid combinations spanning 13 instruments and four timeframes, the mean Schelling point premium $\delta$ is $-0.005$ percentage points {{LB-010}}. Neither the $t$-test ($t = -0.28$, two-sided $p = 0.78$; one-sided $p = 0.61$ against the popular-windows-higher alternative), the Wilcoxon test ($p = 1.00$), nor the sign test (69/137 positive, $p = 1.00$) detects any tendency for popular windows to outperform neighbors. The daily-only subsample (52 combinations) confirms the null ($\delta = -0.016$ pp, two-sided $p = 0.68$). The most-watched level in finance — the 200-day SMA on SPX — shows a Schelling premium of $+0.17$ pp, statistically indistinguishable from zero.

This null result is consistent with the informal observation — reported in Brock, Lakonishok, and LeBaron (1992) — that a wide range of MA windows from 50 to 200 produce similar trading rule performance, and extends it from a robustness observation to a formal statistical test. The self-fulfilling prophecy, if it exists, is too small to detect as a differential next-bar effect. The 137 per-combination $\delta$ values are cross-dependent (the same instruments recur across windows and timeframes), so the battery's effective sample size is well below 137 and the test is underpowered relative to its nominal $N$; the finding is a null, not a tight upper bound. Any real Schelling premium is nonetheless too small to surface here — well below the scale needed to explain the observed convergence patterns.

## 6. Discussion

### 6.1 Implications for Mean-Reversion Analysis

The adaptation theorem implies that the observation of price-MA convergence, standing alone, is insufficient evidence of mean-reversion. This has specific implications for empirical work that uses trailing averages as benchmarks for measuring reversion. When a study finds that returns are negatively correlated with prior displacement from a moving average, the decomposition is an attribution identity that bounds the mechanical share of the subsequent convergence; whether genuine attraction also exists is adjudicated by the direction test, not by the share itself. Our results suggest the mechanical component accounts for the larger share on most of the instruments we examine at horizons below 6 months, with the direction test finding only mild, instrument-specific attraction in the residual.

### 6.2 Implications for Model Specification

When the "mean" toward which an Ornstein-Uhlenbeck or related process reverts is operationalized as a trailing average, the estimated speed-of-reversion parameter $\theta$ confounds two forces: the mechanical adaptation of the average and any genuine economic reversion. The mechanical component biases the estimated $\theta$ upward, since the average's own movement closes part of the gap regardless of whether the series reverts. Researchers using such models should either account for the mechanical component explicitly or use non-trailing-average benchmarks (e.g., fundamental value estimates) to measure displacement.

### 6.3 A Genuine Finding: Displacement Predicts Volatility

While the adaptation theorem primarily clarifies what moving averages *do not on their own* tell us (that price is reverting), it also points to what they *can* tell us: displacement magnitude predicts forward volatility on the instruments we tested. This finding ($\rho = +0.54$ on average, positive on all 11 instruments and all sub-samples; nominal significance survives Bonferroni correction across 38 tests, though as Section 5.7 caveats, the $p$-values are anti-conservative under joint serial dependence) has potential applications in volatility forecasting, options pricing, and risk management. Our reading of the theoretical basis: the convergence dynamics implied by the adaptation theorem — regardless of whether convergence occurs through price reversal, average catch-up, or continuation — would tend to produce elevated realized volatility relative to the pre-displacement baseline.

We emphasize that this finding provides a novel metric for a known mechanism rather than documenting a new phenomenon. The persistence of volatility — the observation that large absolute returns tend to be followed by large absolute returns — has been extensively documented since Mandelbrot (1963) and is the basis for the GARCH family of models (Engle, 1982; Bollerslev, 1986). Our contribution is to argue that displacement from a trailing moving average provides a particularly clean and intuitive measure of the current volatility regime, grounded in the mechanical properties of the filter rather than in parameterized volatility models. The trailing average, interpreted correctly, is a volatility regime indicator rather than a directional signal.

### 6.4 Limitations

Several limitations qualify our findings. First, the decomposition uses a fixed forward horizon ($H = 63$ days in the main specification). While robustness tests at multiple horizons are consistent with the finding persisting, the specific $S_W$ values are horizon-dependent. Second, the individual-event $S_W$ distribution is highly dispersed, and the median $S_W$ is below the aggregate on most instruments. The aggregate statistic (which weights by event magnitude) and the median (which weights all events equally) tell somewhat different stories; we report both. Third, the Schelling Point test measures only next-bar effects; multi-bar self-fulfilling prophecy dynamics would require a different testing framework. Fourth, the SPX quarterly reversion finding indicates that mean-reversion does exist at longer horizons on at least one instrument, and our decomposition at the standard 63-day horizon may not fully capture this effect. Fifth, our data sample, while spanning up to 155 years and 11 instruments, is limited to instruments with available daily price data. The mathematical theorem applies to any trailing average on any time series; broader validation across additional domains would strengthen the generality claim.

## 7. Conclusion

We have argued that the gap closure observed between a time series and its trailing moving average is, on the instruments we examine, predominantly consistent with the mechanical adaptation of the average rather than reversion of the series. The mathematical result is algebraic (Lemmas 1–4: $S_W = 1$ under deterministic displacement), extends to stochastic processes (Theorem 2: population aggregate share equals $1$ under random walk), and finds empirical support across 44 instrument-filter combinations spanning 11 instruments and up to 155 years of data. The aggregate MA share exceeds 50% on all 44 combinations and exceeds 100% on 33 of 44. The next-day direction test reveals no broad attraction. The Schelling Point test finds no detectable self-fulfilling prophecy.

In our reading, the practical implication is that the observation of price-MA convergence, the basis for numerous trading strategies and analytical frameworks, is substantially an accounting consequence of how trailing averages are constructed rather than evidence of an attractive force. The decomposition bounds the mechanical share; the direction test (Section 5.2) is what bears on genuine attraction, and it finds toward-rates near 50% with only mild, instrument-specific exceptions. When a stock chart shows price "bouncing off" its 200-day moving average, the larger mechanism — on the data we examine — appears to be the average catching up to where price already was, with any genuine attraction confined to the residual the direction test can detect.

Two findings carry forward-looking predictive content. The first is the PE-volatility correlation: large displacement from the moving average predicts elevated forward realized volatility ($\rho = +0.54$, positive across the instruments, IS/OOS splits, and permutation tests we ran; we report the sign and magnitude rather than exact $p$-values, which are anti-conservative under the joint serial dependence of displacement and volatility). The second is the genuine S&P 500 quarterly reversion of Section 5.8. This is in line with the adaptation theorem: the convergence dynamics — which the deterministic result implies must occur regardless of direction — tend to produce elevated price movement. The trailing average, interpreted correctly, is a volatility regime indicator rather than a directional signal.

We qualify our findings by documenting quarterly mean-reversion on the S&P 500 ($r = -0.28$ at 126 days), which operates at a different timescale and through a different mechanism than the mechanical adaptation that appears to dominate at shorter horizons. The adaptation theorem does not claim that mean-reversion does not exist — it claims that the observation of price-MA convergence is insufficient evidence for it, because such convergence follows from the mathematical properties of the trailing average regardless of the underlying price dynamics.

More broadly, this paper aims to bring together two literatures that have developed somewhat separately: the macroeconometric tradition recognizing that statistical filters create spurious dynamics (from Slutsky's 1937 demonstration through the modern HP filter critique), and the financial economics tradition interpreting price-MA convergence as evidence of economic mean-reversion. The pieces for this connection have been available for nearly 90 years; we hope the formal decomposition framework presented here offers a useful link between them.

---

## Acknowledgments and AI Disclosure

This research was conducted with extensive AI collaboration. Cross-disciplinary connections that motivate parts of this work emerged from iterative dialogue between the author and large language model AI systems, drawing on disciplines outside the author's formal training. AI was used for literature search across these disciplines, for translation of mathematical results between disciplinary notations, for verification of mathematical derivations through symbolic and numerical computation, and for drafting and revision of analytical arguments. The research questions, the choice of methodology, the interpretation of empirical findings, and all final editorial judgments are the author's own. The paper's mathematical results were checked three independent ways — by hand, by a randomized numerical stress test of more than 28,000 cases, and by symbolic machine-checking — and its empirical claims were each reconstructed from the documented methodology and reproduced; the complete replication protocol is given in Appendix B. All of this verification was performed by the author with AI assistance; none of it constitutes independent expert review, and the theoretical results have not yet been independently verified by a domain expert. For this version, the manuscript additionally underwent a two-round adversarial review conducted by an independent AI session under a capped fix-or-rebut protocol; the full record — including a load-bearing challenge to the 50% falsifier answered with a committed calibration experiment, a defect in that fix that the reviewer caught in the second round, and the author's final disposition — is committed verbatim in the repository (verification/adversarial_review.md). This, too, is AI review, not independent domain-expert review. Citations were verified in tiers: every reference was checked for existence, bibliographic accuracy, and support for the claim it is cited for, against authoritative sources, with verbatim checking of direct quotes and full-text confirmation where the source was accessible; where a source's exact wording could not be confirmed from the available text, the manuscript paraphrases rather than quotes. For this version, the entire empirical battery was rebuilt under a written research standard: analysis scripts were committed before results were accepted, all 36 input files are pinned by SHA-256 hash, every load-bearing number is registered in a machine-checked ledger (`claims.lock`) with declared tolerances, and an automated checker (`verify.py`) regenerates and re-verifies every value on demand; the rebuild was executed with AI assistance and cross-verified on two independent machines. The author takes full responsibility for the contents of this paper, including any errors that may have originated from AI assistance.

---

## References

Avramov, D., Kaplanski, G., and Subrahmanyam, A. (2021). Moving average distance as a predictor of equity returns. *Review of Financial Economics* 39, 127–145.

Baltas, N. and Kosowski, R. (2013). Momentum strategies in futures markets and trend-following funds. Working Paper.

Balvers, R., Wu, Y., and Gilliland, E. (2000). Mean reversion across national stock markets and parametric contrarian investment strategies. *Journal of Finance* 55, 745–772.

Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics* 31, 307–327.

Brock, W., Lakonishok, J., and LeBaron, B. (1992). Simple technical trading rules and the stochastic properties of stock returns. *Journal of Finance* 47, 1731–1764.

Brown, R.G. (1963). *Smoothing, Forecasting and Prediction of Discrete Time Series.* Prentice-Hall.

Chang, X. and Dasgupta, S. (2009). Target behavior and financing: How conclusive is the evidence? *Journal of Finance* 64, 1767–1796.

Cogley, T. and Nason, J.M. (1995). Effects of the Hodrick-Prescott filter on trend and difference stationary time series: Implications for business cycle research. *Journal of Economic Dynamics and Control* 19, 253–278.

Ehlers, J.F. (2001). *Rocket Science for Traders: Digital Signal Processing Applications.* Wiley.

Engle, R.F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica* 50, 987–1008.

Fama, E.F. and French, K.R. (1988). Permanent and temporary components of stock prices. *Journal of Political Economy* 96, 246–273.

Franses, P.H. (1991). Moving average filters and unit roots. *Economics Letters* 37, 399–403.

Hamilton, J.D. (2018). Why you should never use the Hodrick-Prescott filter. *Review of Economics and Statistics* 100, 831–843.

Harvey, A.C. and Jaeger, A. (1993). Detrending, stylized facts and the business cycle. *Journal of Applied Econometrics* 8, 231–247.

Hull, A. (2005). *How to Reduce Lag in a Moving Average.* Available at alanhull.com.

LeBaron, B. (2000). The stability of moving average technical trading rules on the Dow Jones Index. *Derivatives Use, Trading and Regulation* 5, 324–338.

Lo, A.W. and MacKinlay, A.C. (1988). Stock market prices do not follow random walks: Evidence from a simple specification test. *Review of Financial Studies* 1, 41–66.

Mandelbrot, B. (1963). The variation of certain speculative prices. *Journal of Business* 36, 394–419.

Miller, M.H., Muthuswamy, J., and Whaley, R.E. (1994). Mean reversion of Standard & Poor's 500 Index basis changes: Arbitrage-induced or statistical illusion? *Journal of Finance* 49, 479–513.

Narayan, P.K. and Bannigidadmath, D. (2015). Are Indian stock returns predictable? *Journal of Banking and Finance* 58, 506–531.

Nelson, C.R. and Kang, H. (1981). Spurious periodicity in inappropriately detrended time series. *Econometrica* 49, 741–751.

Oppenheim, A.V. and Willsky, A.S. (1997). *Signals and Systems* (2nd edition). Prentice-Hall.

Osler, C. (2003). Currency orders and exchange rate dynamics: An explanation for the predictive success of technical analysis. *Journal of Finance* 58, 1791–1820.

Phillips, P.C.B. and Jin, S. (2021). Business cycles, trend elimination, and the HP filter. *International Economic Review* 62, 469–520.

Poterba, J.M. and Summers, L.H. (1988). Mean reversion in stock prices: Evidence and implications. *Journal of Financial Economics* 22, 27–59.

Shintani, M., Yabu, T., and Nagakura, D. (2012). Spurious regressions in technical trading. *Journal of Econometrics* 169, 301–309.

Slutsky, E. (1937). The summation of random causes as the source of cyclic processes. *Econometrica* 5, 105–146.

Sullivan, R., Timmermann, A., and White, H. (1999). Data-snooping, technical trading rule performance, and the bootstrap. *Journal of Finance* 54, 1647–1691.

Working, H. (1960). Note on the correlation of first differences of averages in a random chain. *Econometrica* 28, 916–918.

Yule, G.U. (1927). On a method of investigating periodicities in disturbed series, with special reference to Wolfer's sunspot numbers. *Philosophical Transactions of the Royal Society A* 226, 267–298.

Zakamulin, V. and Giner, J. (2020). Trend following with momentum versus moving averages: A tale of differences. *Quantitative Finance* 20, 985–1007.

---

## Appendix A: Convergence Rate Derivations

**SMA.** The SMA closes $J/N$ of the original gap per period. At time $k$ ($0 \leq k \leq N-1$), the remaining gap is $J(N-k-1)/N$. The convergence is linear in $k$.

**EMA ($\alpha = 2/(N+1)$).** The remaining gap at time $k$ is $J(1-\alpha)^{k+1}$. Key timescales: $t_{50} = \ln(2)/\alpha - 1 \approx 0.347N$ (half-life), $t_{90} = \ln(10)/\alpha - 1 \approx 1.15N$, $t_{95} = \ln(20)/\alpha - 1 \approx 1.50N$.

**WMA (linear weights).** Remaining gap at time $k$: $J(N-k-1)(N-k)/[N(N+1)]$. Front-weighting produces faster initial convergence than SMA: at $k = 1$, WMA has closed $2(N-1)/[N(N+1)]$ of the gap versus $1/N$ for SMA.

**HMA (window $N$).** Maximum convergence time: $(N-1) + (\lfloor\sqrt{N}\rfloor-1)$ periods. For $N = 50$: 55 periods (49 + 6). For $N = 200$: 212 periods (199 + 13). The HMA may transiently overshoot $P_0 + J$ due to negative effective weights.

## Appendix B: Complete Replication Protocol

This appendix provides the step-by-step algorithms necessary to reproduce every empirical result in this paper. All computations use standard numerical libraries (NumPy, pandas, SciPy in Python; equivalent in R or MATLAB). No proprietary tools are required.

### B.1 Data Acquisition and Preparation

*Non-positive closes: the analysis operates on $\ln(\text{close})$; the loader drops any bar with a non-positive close before the log transform. In the present sample exactly one such bar exists — NYMEX crude oil front-month, 2020-04-20, settling at $-37.63$ — and it is dropped; crude's large 2020 displacement events on either side of that bar are retained. Roll handling: the futures series are TradingView continuous front-month contracts, and a roll gap is an artificial step that the trailing average closes mechanically; such a step could in principle contribute mechanical closure to an event spanning it. Isolated one-bar roll gaps rarely clear the 75th-percentile threshold and are spacing-limited to one event per $H$ bars, and the five equity cash indices (SPX, NDX, NI225, DAX, FTSE) carry no roll splices yet already exceed 50% on every filter; a roll-window-exclusion robustness check on the six futures is noted as future work. The earlier SPX-vs-ES agreement is an equity-only check and is labeled as such.*

**Sources.** All price data were exported from TradingView (tradingview.com) using the platform's CSV export functionality. The specific TradingView ticker symbols, date ranges, and observation counts for all instruments used in any analysis:

**Core instruments (11, used in main decomposition and PE-vol correlation):**

| Instrument | TradingView Ticker | Start Date | End Date | Observations |
|---|---|---|---|---|
| SPX | SP:SPX | 1871-02-01 | 2026-03-12 | 25,187 |
| NDX | NASDAQ:NDX | 1985-01-31 | 2026-03-13 | 10,359 |
| NI225 | TVC:NI225 | 1949-05-16 | 2026-03-13 | 19,040 |
| DAX | XETR:DAX | 1970-01-02 | 2026-03-13 | 14,143 |
| FTSE | IG:FTSE | 1995-01-03 | 2026-03-13 | 8,615 |
| HSI | HKEX:HSI1! (front-month future) | 1987-04-21 | 2026-03-16 | 9,585 |
| CL | NYMEX:CL1! | 1983-03-30 | 2026-03-13 | 10,798 |
| GC | COMEX:GC1! | 1975-01-02 | 2026-03-13 | 12,878 |
| ZN | CBOT:ZN1! | 1982-05-03 | 2026-03-13 | 11,058 |
| 6E | CME:6E1! | 2000-09-12 | 2026-03-13 | 6,451 |
| 6J | CME:6J1! | 2000-09-13 | 2026-03-13 | 6,373 |

**Extension instruments (2, used in IS/OOS and Schelling Point extensions only):**

| Instrument | TradingView Ticker | Start Date | End Date | Observations |
|---|---|---|---|---|
| ES | CME_MINI:ES1! | 1997-09-09 | 2026-03-13 | 7,210 |
| NKD | CME:NKD1! | 2004-02-17 | 2026-03-13 | 5,574 |

**Futures roll handling.** TradingView's continuous contract (the "1!" suffix) uses the platform's default roll method, which splices front-month contracts at expiration. Because the decomposition operates on log prices and measures displacement relative to a trailing average (which adapts to any roll gap mechanically), the roll methodology does not affect the results. We verified this by comparing SPX (cash index, no rolls) to ES (futures with rolls) and confirming qualitatively identical decomposition results.

**Log transformation.** All prices $P$ are converted to log prices: $\log P(t) = \ln(\mathrm{close}(t))$. All subsequent computations use log prices unless explicitly stated otherwise.

### B.2 Moving Average Computation

**SMA of window $N$:** $\mathrm{SMA}_N(t) = (1/N) \times \sum_{k=0}^{N-1} \log P(t-k)$. Requires $N$ valid prior observations. The first valid SMA value is at bar index $N-1$ (0-indexed).

**EMA with equivalent window $N$:** $\alpha = 2/(N+1)$. $\mathrm{EMA}(t) = \frac{\sum_{k=0}^{t}(1-\alpha)^k \cdot \log P(t-k)}{\sum_{k=0}^{t}(1-\alpha)^k}$, the normalized running weighted average over the available history (equivalently, pandas `ewm(span=N, adjust=True).mean()`). The EMA is well-defined from bar 0; the equivalent-window convention $N$ governs the filter's half-life and spectral response.

**Hull Moving Average of window $N$:** (a) Compute $\mathrm{WMA}_{\lfloor N/2\rfloor}(t)$, where $\mathrm{WMA}_M$ uses linearly decreasing weights $w_k = (M-k) / [M(M+1)/2]$ for $k = 0, \ldots, M-1$. (b) Compute $\mathrm{WMA}_N(t)$ with the same weight formula but window $N$. (c) Compute the intermediate series: $I(t) = 2 \times \mathrm{WMA}_{\lfloor N/2\rfloor}(t) - \mathrm{WMA}_N(t)$. (d) Compute $\mathrm{HMA}_N(t) = \mathrm{WMA}_{\lfloor\sqrt{N}\rfloor}(I(t))$. The first valid HMA value requires $N + \lfloor\sqrt{N}\rfloor - 1$ prior observations.

**Eight MA specifications tested:** Hull-20 ($N=20$), Hull-50 ($N=50$), Hull-100 ($N=100$), SMA-20 ($N=20$), SMA-50 ($N=50$), SMA-100 ($N=100$), SMA-200 ($N=200$), EMA-50 ($N=50$, $\alpha=2/51$).

### B.3 Decomposition Algorithm (Pseudo-code)

```
INPUT: logP[0..T-1], MA[0..T-1], H=63, threshold_percentile=75, min_history=252
OUTPUT: list of (C_P, C_W, S_W) tuples for each qualifying event

1. Compute displacement: x[t] = logP[t] - MA[t] for all t where MA[t] is valid
2. Compute absolute displacement: abs_x[t] = |x[t]|
3. Initialize: events = [], last_event_bar = -H
4. For t = min_history to T-H-1:
   a. Compute expanding threshold: tau[t] = percentile(abs_x[0..t], threshold_percentile)
      -- This uses only data through bar t (no look-ahead)
      -- The percentile function returns the value below which threshold_percentile%
        of the observations fall (e.g., numpy.percentile or pandas.quantile)
   b. If abs_x[t] > tau[t] AND (t - last_event_bar) >= H:
      -- This event qualifies: displacement exceeds threshold AND at least H bars
        since the last qualifying event (non-overlapping forward windows)
      c. Compute price change:  dP = logP[t+H] - logP[t]
      d. Compute filter change: dW = MA[t+H] - MA[t]
      e. Compute signed contributions:
         C_P = -sign(x[t]) * dP
         C_W = +sign(x[t]) * dW
      f. If (C_P + C_W) != 0:
         S_W = C_W / (C_P + C_W)
      g. Append (C_P, C_W, S_W) to events
      h. Set last_event_bar = t
5. Compute aggregate S_W = sum(all C_W) / sum(all C_W + all C_P)
6. Compute median S_W = median of all individual S_W values
7. Compute mean S_W = arithmetic mean of all individual S_W values
```

**Critical implementation notes:** (a) The expanding threshold at step 4a must use ALL observations from the first valid bar through bar $t$, not a rolling window. In pandas: `abs_x.expanding(min_periods=min_history).quantile(threshold_percentile/100)`. (b) The min_history parameter ensures the threshold is calibrated from a sufficient number of observations before events are selected. We use min_history $= 252$ (approximately one year of daily data). (c) Events are selected sequentially in chronological order; the first qualifying event after the minimum history period begins the chain. The starting offset (which bar within the first $H$ bars is the first qualifying event) is arbitrary; Section 5.4 reports results for all 63 possible starting offsets and shows negligible sensitivity. (d) The sign function returns $+1$ for positive arguments and $-1$ for negative arguments ($\mathrm{sign}(0) = 0$, but $x[t] = 0$ events are excluded by the threshold condition).

### B.4 Direction Test Algorithm

*The drift-adjusted null uses the full-sample positive-return fraction $p_{up}$; this is an in-sample descriptive adjustment, not a causal-at-time-$t$ construction. An expanding or era-local drift estimate would be the causal alternative; the realized-sample toward-rate conclusions are unaffected.*

```
INPUT: logP[0..T-1], MA[0..T-1], threshold_percentile=75, min_history=252
OUTPUT: toward_count, total_count, toward_rate

1. Compute x[t] and expanding threshold tau[t] as in B.3, steps 1-2 and 4a
2. For each bar t where abs_x[t] > tau[t] AND t+1 < T:
   -- NOTE: unlike the decomposition, the direction test does NOT enforce
     non-overlapping spacing. Every qualifying bar is tested independently.
   a. next_return = logP[t+1] - logP[t]
   b. If x[t] > 0 and next_return < 0: toward_count += 1  (price moved down, toward MA)
   c. If x[t] < 0 and next_return > 0: toward_count += 1  (price moved up, toward MA)
   d. total_count += 1
3. toward_rate = toward_count / total_count
4. z_statistic = (toward_count - 0.5 * total_count) / sqrt(0.25 * total_count)
5. p_value = 2 * (1 - Phi(|z_statistic|))  where Phi is the standard normal CDF
```

**Drift-adjusted direction test:** Replace the null probability of $0.5$ with a drift-adjusted null. Compute $p_{\mathrm{up}}$ = fraction of all daily returns that are positive on the instrument. For above-MA observations ($x[t] > 0$), "toward" requires a negative return, so the null probability is $(1 - p_{\mathrm{up}})$. For below-MA observations, the null is $p_{\mathrm{up}}$. The blended null is: $p_{\mathrm{null}} = f_{\mathrm{above}} \times (1 - p_{\mathrm{up}}) + (1 - f_{\mathrm{above}}) \times p_{\mathrm{up}}$, where $f_{\mathrm{above}}$ is the fraction of qualifying events with $x[t] > 0$.

### B.5 Synthetic Control Generation

**I.I.D. Normal:** Generate 20 independent series of length 25,000 from: $r[t] \sim N(0, \sigma^2)$ where $\sigma$ is calibrated to produce annual volatility of approximately 20% ($\sigma_{\mathrm{daily}} = 0.20/\sqrt{252} \approx 0.0126$). Construct prices as $\log P[t] = \log P[0] + \sum_{s=1}^{t} r[s]$ with $\log P[0] = 0$. Apply the identical decomposition algorithm from B.3 to each series.

**GARCH-Calibrated:** For each instrument, fit a GARCH(1,1) model with Student-t innovations to the instrument's actual daily log return series: $r[t] = \mu + \varepsilon[t]$, where $\varepsilon[t] = \sigma[t] \times z[t]$, $\sigma^2[t] = \omega + \alpha_1 \varepsilon^2[t-1] + \beta_1 \sigma^2[t-1]$, and $z[t] \sim t_\nu$. Use maximum likelihood estimation (e.g., the `arch` package in Python). Generate 20 synthetic paths of the same length as the original instrument using the fitted parameters. Set $\mu = 0$ in the simulation to ensure zero return autocorrelation (zero attraction by construction). CL and GC are excluded from the GARCH control because their fitted models produce integrated GARCH ($\alpha_1 + \beta_1 \geq 1.0$), making simulation non-stationary. The remaining 9 instruments each contribute 20 simulations $= 180$ total GARCH paths.

### B.6 PE-Volatility Correlation

*In-sample/out-of-sample decomposition (Section 5.6): both halves inherit the full-history expanding threshold — the same operator as the Section 5.1 main decomposition — rather than recalibrating the threshold from each half boundary. This is the operator that generated the reported IS/OOS aggregates.*

**PE (displacement energy) computation:** (a) Compute displacement $x[t] = \log P[t] - \mathrm{MA}[t]$ using the Hull-50 specification. (b) Compute rolling 63-day mean of $x^2$: $\mathrm{PE}_{\mathrm{raw}}[t] = (1/63) \times \sum_{k=0}^{62} x[t-k]^2$. (c) Compute the expanding percentile rank: $\mathrm{PE}[t]$ = rank of $\mathrm{PE}_{\mathrm{raw}}[t]$ within $\{\mathrm{PE}_{\mathrm{raw}}[\mathrm{min\_hist}], \ldots, \mathrm{PE}_{\mathrm{raw}}[t]\}$, expressed as a percentile (0 to 100). Minimum history: 252 bars. In pandas: `PE_raw.expanding(min_periods=252).rank(pct=True) * 100`.

**Forward realized volatility:** $\mathrm{FwdVol}[t] = \mathrm{std}(r[t+1], r[t+2], \ldots, r[t+21]) \times \sqrt{252}$, where $r[s] = \log P[s] - \log P[s-1]$. This uses a purely forward 21-day window starting at $t+1$ (no overlap with the PE computation window at time $t$). Annualization factor: $\sqrt{252}$.

**Correlation test:** Compute Spearman rank correlation $\rho$ between $\mathrm{PE}[t]$ and $\mathrm{FwdVol}[t]$ on a non-overlapping sample spaced by the forward-volatility window: one observation every 21 bars, starting from the first bar where both are valid. The 21-bar spacing makes consecutive forward-volatility windows non-overlapping (each shares zero of its 21 days with the next), which is what makes the parametric $p$-values valid — consecutive daily windows share 20 of their 21 days and are heavily autocorrelated; Appendix B.8's quarterly-reversion test uses the same logic for the same reason. Report $\rho$ and its two-sided $p$-value (scipy.stats.spearmanr).

**IS/OOS:** Compute $\mathrm{PE}[t]$ and $\mathrm{FwdVol}[t]$ on the full series and take the 21-bar non-overlapping sample described above. Split *that sample* at its chronological midpoint into IS and OOS halves and compute the Spearman correlation on each half. This procedure introduces no look-ahead because the expanding percentile rank is causal — a bar's PE value uses only its own past, regardless of how the sample is later split. Report both correlations and $p$-values.

**Permutation test:** For each of 5,000 iterations: randomly shuffle the $\mathrm{PE}[t]$ values while keeping $\mathrm{FwdVol}[t]$ fixed. Compute the Spearman correlation on the shuffled data. The permutation $p$-value is the fraction of shuffled correlations that exceed the real correlation. Instruments tested: SPX, NDX, NI225, GC, CL (the five longest-history instruments).

**Bonferroni correction:** The 38 tests comprise 33 IS/OOS correlations (11 instruments $\times$ 3 correlations each: full-sample, IS half, OOS half) plus 5 permutation tests (one per instrument: SPX, NDX, NI225, GC, CL). The Bonferroni-corrected significance threshold is $0.05/38 = 0.00132$.

### B.7 Schelling Point Test

**Popular windows:** $W \in \{20, 50, 100, 200\}$.

**Neighbor windows:** For each $W$, the neighbors are $\{W-5, W-3, W+3, W+5\}$. For example, for $W=200$: neighbors are $\{195, 197, 203, 205\}$.

**Toward rate computation:** For each SMA window (popular or neighbor), compute the SMA, compute the displacement and expanding threshold, and compute the toward rate exactly as in B.4. The toward rate is computed using ALL qualifying bars (not non-overlapping), with the same expanding-threshold methodology and min_history parameter scaled by timeframe (daily: 252, hourly: 500, 5-minute: 2,000, monthly: 60).

**Schelling point premium:** For each popular window $W$: $\delta_W = \mathrm{toward\_rate}(W) - \mathrm{mean}(\mathrm{toward\_rate}(W-5), \mathrm{toward\_rate}(W-3), \mathrm{toward\_rate}(W+3), \mathrm{toward\_rate}(W+5))$.

**Instruments and timeframes:** The Schelling test's NASDAQ instrument is the NQ E-mini futures contract (CME_MINI:NQ1!) on all four timeframes, not the cash NDX index used elsewhere in the paper — the cash index lacks the intraday history the hourly and 5-minute tests need, so NQ is used throughout the Schelling test for consistency across timeframes. Daily: 13 instruments (the 11 core instruments with NDX replaced by NQ, plus ES and NKD). Hourly: 12 instruments (all except SPX, which lacks hourly data in our sample). 5-minute: 8 instruments (ES, NQ, GC, CL, ZN, 6E, 6J, NKD — those with sufficient 5-minute history). Monthly: 2 instruments (SPX, GC — those with sufficient monthly history to produce 200+ qualifying events per window). The hourly, 5-minute, and monthly data are from the same TradingView export source, using the corresponding timeframe setting on the same ticker symbols.

**Inclusion criterion:** A combination (instrument $\times$ popular window $\times$ timeframe) is included only if both the popular window and all four neighbors produce at least 200 qualifying events. Combinations failing this criterion are excluded. This yields 137 valid combinations.

**Statistical tests:** One-sample $t$-test on the 137 $\delta$ values ($H_0$: mean $\delta = 0$). Wilcoxon signed-rank test on the 137 $\delta$ values. Sign test: count of positive $\delta$ values versus total.

### B.8 Quarterly Reversion Test

**Non-overlapping return windows:** Divide the full SPX log return series into consecutive non-overlapping blocks of length $H$ (e.g., $H=63$ for quarterly). For each block starting at bar $t_k$, compute: (a) the signed displacement $x[t_k] = \log P[t_k] - \mathrm{Hull50}[t_k]$, and (b) the forward block return $R[t_k] = \log P[t_k+H] - \log P[t_k]$. Compute the Pearson correlation between $\{x[t_k]\}$ and $\{R[t_k]\}$ across all blocks. Report the correlation $r$, the $t$-statistic $t = r\sqrt{n-2}/\sqrt{1-r^2}$, and the two-sided $p$-value. Test at $H = 21, 63, 126, 252$.

### B.9 Era Analysis

**Era boundaries for SPX:** Pre-1930 (1871–1929), 1930–1960, 1960–1990, 1990–2026. Run the full decomposition (B.3) once over the full history, then bin the resulting event chain by era under a **span rule**: an event belongs to an era only if its trigger date AND its $t + H$ horizon-completion date both fall inside the era (events crossing a boundary belong to no era). Compute the aggregate $S_W$ over each era's binned events. The per-era direction test applies the B.4 operators with the full-history expanding threshold, restricting observations to the era. The pre-1930 era produces fewer than 10 qualifying events and is reported but not interpreted. (An earlier draft of this appendix specified per-era threshold recalibration; the published era values derive from the binned method stated here, and the verified rebuild adopts it — see B.14.)

### B.10 Filter-Matched Horizon Test

The filter-matched horizon test runs the decomposition (B.3) with $H$ set to each filter's theoretical convergence time rather than the fixed $H = 63$:

| MA Specification | Matched Horizon $H$ | Rationale |
|---|---|---|
| Hull-50 | $H = 55$ | Complete convergence: $(N-1) + (\lfloor\sqrt{N}\rfloor-1) = 49 + 6 = 55$ |
| SMA-50 | $H = 50$ | Complete convergence: $N-1 = 49$, rounded to 50 |
| EMA-50 | $H = 75$ | 95% convergence: $1.50 \times N = 75$ |
| SMA-200 | $H = 200$ | Complete convergence: $N-1 = 199$, rounded to 200 |

All other parameters (expanding threshold, min_history, spacing) remain identical to the main decomposition. The aggregate and median $S_W$ are computed separately for each filter-matched run and compared to the corresponding $H = 63$ results.

### B.11 Rolling-Window Decomposition (SPX)

Run the full decomposition (B.3) on SPX in 18 rolling windows: one early catch-all window spanning 1871–1936 (necessitated by the sparsity of pre-1930s SPX data), followed by 17 overlapping 10-year windows advancing in 5-year steps from 1931 — 1931–1941, 1936–1946, 1941–1951, …, 2011–2021. Each post-catch-all window uses approximately 2,520 trading days ($10 \times 252$); the catch-all window covers the full pre-1936 history. The expanding threshold recalibrates from scratch within each window (bar 0 of each window is the first bar; min_history $= 252$ bars within the window, except for the catch-all window which uses the available pre-1936 history). Report the aggregate $S_W$, median $S_W$, and event count for each window. The irregular early window reflects pre-1930s data sparsity, consistent with the limited interpretation of the pre-1930 era in Section 5.5 and Appendix B.9. The values in Section 5.6 are from the verified rebuild of this procedure; an earlier draft reported 14 of 18 windows above 50% from an original computation whose interior-window implementation could not be exactly reconstructed, and the rebuild's 13 of 18 supersedes it (see B.14).

### B.12 Note on PE-Volatility Specifications Across Studies

This paper and the companion Project Lattice Strategy Document use different PE-volatility specifications. The differences are intentional — each specification is optimized for its context — but replicators should be aware of them:

| Parameter | This Paper (Scientific) | Project Lattice (Strategy) |
|---|---|---|
| Price type | Log prices | Raw (level) prices |
| MA specification | Hull-50 | SMA-200 |
| PE measure | Expanding percentile of rolling 63-day mean of $x^2$ | Rolling 63-bar percentile rank of $|\mathrm{displacement}|$ |
| Forward vol window | 21 days | 63 days (matches holding period) |
| Reported $\rho$ (average) | $+0.541$ | $+0.369$ |
| Purpose | Maximum statistical power | Tradeable signal matching holding period |

The scientific paper's specification uses a more sophisticated PE measure (rolling mean of squared displacement, then expanding percentile rank) and a shorter forward vol window (21 days), which together produce higher correlations because the PE measure captures displacement persistence and the 21-day vol window provides more independent observations for correlation estimation. The strategy document's specification uses a simpler PE measure (raw absolute displacement percentile within a 63-bar rolling window) and a 63-day forward vol window (matching the straddle holding period), which is directly actionable but produces lower correlations due to the noisier PE measure and longer forward window. Both specifications are valid measurements of the same underlying phenomenon (displacement predicts forward volatility). A replicator using the scientific paper's specification should obtain $\rho \approx +0.54$; using the strategy document's specification should obtain $\rho \approx +0.37$.

### B.13 Software and Reproducibility

All computations were performed in Python 3.12.10 with pandas 2.3.3, numpy 1.26.4, scipy 1.16.3, arch 6.3.0, and openpyxl 3.1.5 (pinned in the repository's `requirements.txt`). Random seeds: 42 for the primary synthetic controls and 20260526 for the 200-series large-sample battery. Every number in this paper is regenerated on demand by the committed analysis scripts run on SHA-256-hashed input data; the repository's `claims.lock` ledger and `verify.py` checker enforce this (the checker re-hashes all 36 inputs, re-runs all seven analysis scripts, compares every load-bearing value within declared tolerances, and is itself validated against a deliberately broken fixture it must reject).

### B.14 Rebuild Reconciliation Notes

This version of the paper is a verified rebuild: every empirical value was regenerated from committed scripts on hashed data and adjudicated against the original study's computational artifacts. Five reconciliations from that adjudication are disclosed here; the full record (rulings, row-by-row comparisons, and tolerances) is in the repository's `DECISIONS.md` and `claims.lock`.

1. **Instrument set in the robustness batteries.** The original study's horizon, filter-matched, threshold, and IS/OOS grids used the NQ E-mini future in place of the NDX cash index, while its main decomposition (Section 5.1) used NDX. The rebuild preserves that substitution because the published robustness numbers derive from it; the inconsistency is disclosed rather than silently harmonized.
2. **EMA definition.** This paper's B.2 specifies the normalized EMA (`ewm(span=N, adjust=True)`), which is what the rebuild computes. The original artifact's filter-matched EMA columns were produced by a different EMA variant (every EMA row differs by 1–3 events); the rebuild follows the stated definition.
3. **Era method.** An earlier draft's B.9 stated per-era threshold recalibration, but the published era values derive from full-history binning under the span rule; B.9 now states the method the numbers actually come from, and the rebuild reproduces three of the four published era values exactly (the fourth, 1990–2026, is 80.6% vs the earlier 81.5% at equal event count — a single boundary-event difference).
4. **Rolling windows.** The original interior-window implementation could not be exactly reconstructed after extensive testing of candidate variants (only the 1871–1936 catch-all reproduces exactly). Section 5.6 reports the verified rebuild values (13 of 18 windows above 50%, worst window 1991–2001 at $-8.0\%$), superseding the earlier draft's 14 of 18.
5. **Superseded draft values.** Where this version's numbers differ from the prior circulated draft (Schelling statistics, the synthetic-control batteries, $H=126$ horizon count, modern-era $S_W$, OOS mean, maximum PE-volatility $\rho$), the rebuild's regenerated values are authoritative; each is locked in `claims.lock` with its generating script and tolerance.

---

*© 2026 Jae Kim. This paper is licensed under [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)](https://creativecommons.org/licenses/by-nc-nd/4.0/). You may share it with attribution, for non-commercial purposes, without modification. The accompanying reconstruction and verification code is released separately under the MIT License; see the repository `LICENSE`.*
