# Moving Averages Follow Price — the plain-English version

*Companion to the working paper of the same title. Education, not investment advice.*

## The claim in one sentence

When a price chart "comes back to" its moving average, it is mostly the moving average doing the moving — not the price.

## Why anyone should care

Moving averages are everywhere: the 200-day line on every financial news segment, the 50-day "golden cross," trading strategies built on price "bouncing off" the average. Nearly all of that commentary carries a hidden assumption — that the average is a kind of magnet, and price is attracted to it.

The paper tests that assumption and finds it mostly backwards. A trailing average is, by construction, a follower. If price jumps to a new level and just stays there, the average will drift up to meet it, every time, with mathematical certainty — and on a chart this looks exactly like "the gap closed." No attraction required.

## What the paper actually does

First, the math: for any standard trailing average, a permanent price move is followed by the average closing 100% of the gap by itself. That part is algebra, not statistics.

Then the data: we split every observed gap closure into two parts — how much the price moved toward the average, and how much the average moved toward the price. We do this on 44 instrument-and-filter combinations across 11 instruments (US, European, and Asian stock indices; oil; gold; Treasury futures; two currencies), using up to 155 years of S&P 500 history.

The result: in every one of the 44 combinations, the average did **more than half** of the work. In 33 of 44 it did **more than all** of it — meaning price actually drifted further away while the average caught up.

## The checks

We tried to break the result. Different averages (Hull, simple, exponential, fast and slow), different thresholds, different horizons, different start dates, log and raw prices, in-sample/out-of-sample splits, and decade-by-decade windows. The conclusion holds in aggregate everywhere we looked — and where individual cells dip below 50% (a handful of long-horizon cells; five of eighteen rolling decades, mostly 1986–2016), the paper reports them rather than hiding them.

We also ran the same measurement on fake data — random walks with zero attraction built in — and got the same ~100% mechanical share the math predicts, so the yardstick itself isn't biased.

Two genuine non-mechanical findings survive, and the paper is explicit about both. First, a big gap between price and its average predicts **more volatility** ahead — the strongest statistical result in the paper, and the one with forward-looking content. Second, the S&P 500 specifically shows real mean-reversion at quarterly horizons — slower and smaller than the mechanical effect, but real.

## What this means practically

If a strategy's edge is the claim that "price returns to the moving average," the burden of proof just went up: most of the visual evidence for that claim is the average returning to the price. Read correctly, distance from the moving average is a **volatility gauge**, not a direction signal.

## A test you can run yourself

We also checked the folklore that famous levels (the 50-day, the 200-day) are special because everyone watches them. Across 137 combinations of instruments, timeframes, and windows, popular windows behave exactly like their unpopular neighbors (the 47-day, the 203-day). No magic numbers.

## How much to trust this

Every number in the paper is regenerated on demand by committed code running on fingerprinted data; an automated checker verifies the whole chain and is itself tested against deliberately corrupted inputs it must reject. This version is a full rebuild of the original study — where the rebuild's numbers differ from the earlier draft (a few do, and one robustness count moved from 14/18 to 13/18 *against* the paper's favor), the rebuilt values are the ones printed, and the differences are disclosed in the paper's Appendix B.14. The work was done with extensive AI assistance and has not yet had independent expert review; it is a working paper, posted to be checked.

*Code, data fingerprints, and the verification ledger: github.com/jaek913/Moving-Averages-Follow-Price*
