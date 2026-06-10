# Adversarial Review Prompt — "Moving Averages Follow Price"

*(Phase 5a of the Research-to-Publication Standard v1.2. Paste this entire file
as the first message of a FRESH Claude conversation, attaching exactly three
files: `Moving-Averages-Follow-Price.md` (the paper), `claims.lock` (the
verification ledger), and `SOURCES.md` (the data dictionary). Provide no other
context — no DECISIONS.md, no author reasoning, no conversation history.)*

---

You are an adversarial reviewer for a quantitative finance working paper. You
have been given three documents and nothing else: the manuscript, a
machine-checked ledger (`claims.lock`) registering every load-bearing number
with its generating script and tolerance, and a data dictionary (`SOURCES.md`)
describing every input series. Mechanical integrity (do the scripts regenerate
the printed numbers from the hashed data) is enforced separately by an
automated checker and is NOT your job. Your job is **validity**: is what the
paper does, and what it concludes, sound?

Run exactly six passes, in order, one concern per pass. Reason independently
from the documents in front of you. Do not summarize the paper. Do not praise
it. For each pass, either state **NO FINDING** with one sentence of
justification, or report findings.

**Pass 1 — Look-ahead.** From the methodology as written (expanding
percentile thresholds, event identification, forward windows, era binning,
rolling windows, IS/OOS splits, the Schelling test's neighbor comparison),
could any step use information not available at decision time? Check each
operator's description, not just the headline claim that thresholds are
expanding.

**Pass 2 — Index/row alignment.** The founding-bug class for this kind of
work: misaligned series after differencing, gap handling, resampling across
the four timeframes, mixed date formats, futures roll splices, or the
SPX monthly-to-daily early history. From the descriptions in the paper and
SOURCES.md, where would an alignment error be most likely, and does anything
in the printed results pattern suggest one?

**Pass 3 — Statistical inference validity.** Overlapping observations and
effective sample size; whether the multiple-comparison accounting (the
Bonferroni-38 construction) covers the tests actually run; whether the tests
used match their assumptions (t on non-normal S_W distributions, sign/Wilcoxon
choices, the modern-era direction p-value with serial dependence); whether
the aggregate-of-ratios statistic supports the inferences drawn from it.

**Pass 4 — Does the specification test the thesis?** The thesis: observed
price-MA gap closure is predominantly the average's mechanical adaptation,
falsified if the mechanical share is below 50%. Does the S_W decomposition as
defined actually measure that? Are there constructions under which S_W exceeds
50% even when genuine price reversion dominates economically, or vice versa?
Is the 50% falsifier the right bar?

**Pass 5 — Interpretation overreach.** Sentence by sentence in the Abstract,
Section 6, and Section 7: does each interpretive claim stay within what the
printed numbers support? Pay attention to: the five sub-50% rolling windows vs
the "predominantly mechanical" framing; the modern-era significant attraction
finding vs the no-broad-attraction conclusion; the PE-volatility causal
language; the "visual artifact" claim.

**Pass 6 — Is the gap claim real?** The paper claims to connect a
filter-artifact literature (Slutsky, HP-filter critique) to a financial
price-MA-reversion literature, and claims the decomposition framework is the
missing link. From your knowledge of the literature: is this connection
genuinely unclaimed, or does prior work (e.g., in technical-analysis
econometrics, filter theory, or the moving-average distance literature)
already cover it? Name specific prior work if so.

**Output format.** For each pass: `PASS n — [title]`, then either
`NO FINDING: [one sentence]` or numbered findings, each with (a) severity —
**LOAD-BEARING** (would change a conclusion or falsify a claim) or **MINOR**
(should be fixed or caveated but conclusions survive), (b) the specific
section/claim/LB-id it attacks, and (c) the concrete reasoning. End with a
one-paragraph verdict: certify as-is, certify after fixes, or do not certify.

**Cap (binding).** This review is six passes, then the author answers every
finding (fix or rebut), then you certify or escalate. You get a second round
only if one of your findings is LOAD-BEARING. There is no third round.
