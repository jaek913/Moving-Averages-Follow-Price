# Citation Check — Moving Averages Follow Price (Standard 5b, all-tier)

**Manuscript:** `paper/Moving-Averages-Follow-Price.md` MD5 `2c39d55b95766e0e6f1150f86091a031` (31 references; pre-adjustment pin c069ea1bdfe85201ef3bc54b7e968630 — this gate's Ehlers §2.4 precision edit is the only difference)
**Date:** 2026-06-11
**Status:** Complete — 31/31 closed (the final two full-text confirms closed 2026-06-11 via extended web verification; see rows and the closure record).

## Basis and method

Three verification layers, each documented:

1. **Lineage verification (authoritative, 2026-05-26).** All 29 references of the v4/v5-lineage bibliography were verified fresh, reference-by-reference, via web search against authoritative sources (publisher pages, JSTOR, RePEc, Semantic Scholar, DOIs), with three checks per reference (existence; bibliographic accuracy; claim-support) and verbatim checking of direct quotes. Record: `verification/Stage_1.3_Citation_Verification.md` in the predecessor repository `lagging-truth-paper-01` (committed there; summarized in the project memory). Result: 29/29 verified, 25 fully clean, 4 discrepancies flagged.
2. **Rebuild-era fresh verifications (this repository, Phase 5b, 2026-06-10).** Working (1960) — clean, with one tier-3 in-text precision fix applied (first differences of the averages); Miller, Muthuswamy & Whaley (1994) — clean on all three tiers; Avramov, Kaplanski & Subrahmanyam (2021) — spot-check clean on all three tiers. Recorded in DECISIONS.md (Phase 5b).
3. **Reconciliation of the lineage record against the current manuscript (2026-06-11, this document).** Every lineage discrepancy and open item checked against the current (c069ea1b) text.

## Reconciliation of the four lineage discrepancies — all resolved

| # | Reference | Lineage finding (2026-05-26) | Current-manuscript status |
|---|---|---|---|
| 1 | Cogley & Nason 1995 | Direct quote "is sufficient to generate business cycles" unverifiable; verifiable wording is "can generate business cycle dynamics" | **RESOLVED.** Current §2.2 carries no quote; the paraphrase ("concluding that the filter can generate business cycle dynamics even when none exist") matches the verifiable wording. |
| 2 | LeBaron 2000 | Window-stability claim belongs to BLL 1992 (+ LeBaron 1998); LeBaron 2000's thesis is the post-1986 breakdown | **RESOLVED.** Current §2.3 attributes the 50–200-day window-range observation to Brock et al. (1992) directly (consistent with LeBaron 2000's own attribution) and cites LeBaron (2000) only for the post-1986 breakdown. |
| 3 | Osler 2003 | End-page 1820 (v4) vs 1819 (RePEc); Wiley supports 1820 | **RESOLVED.** Current References keep the Wiley-supported 1791–1820. |
| 4 | Oppenheim & Willsky 1997 | 2nd-edition title page adds "with S. Hamid Nawab" | **RESOLVED by ruling.** Standard two-author form retained (widely accepted; judgment call per the lineage record). |

## Reference-by-reference verdicts (31)

Tier legend: T1 = full-text/deepest (load-bearing or quoted); T2 = supports-claim; T3 = existence + bibliographic. "Lineage" = verified fresh 2026-05-26; "5b" = verified fresh in this repo 2026-06-10.

| Reference | Tier | Verdict | Basis |
|---|---|---|---|
| Avramov, Kaplanski & Subrahmanyam 2021 | T2 | CLEAN | Lineage + 5b spot-check (DOI 10.1002/rfe.1118); both citing locations supported |
| Baltas & Kosowski 2013 (WP) | T2 | CLEAN | Lineage (SSRN 1968996); the §1 $300B CTA AUM figure confirmed genuinely in the source |
| Balvers, Wu & Gilliland 2000 | T3 | CLEAN | Lineage (DOI 10.1111/0022-1082.00225) |
| Bollerslev 1986 | T3 | CLEAN | Lineage |
| Brock, Lakonishok & LeBaron 1992 | T2 | CLEAN | Lineage (DOI 10.1111/j.1540-6261.1992.tb04681.x); the once-flagged fabricated quote confirmed absent; excess-returns and window-range readings supported |
| Brown 1963 | T3 | CLEAN | Lineage (HathiTrust; JRSS 1964 review) |
| Chang & Dasgupta 2009 | T2 | CLEAN (note) | Lineage (DOI 10.1111/j.1540-6261.2009.01479.x); mechanical-reversion-under-random-financing claim confirmed from authors' abstract. Note: the phrase "mechanical mean reversion" is verbatim in the authors' working-paper version; the published abstract uses "mechanical reversal." The manuscript introduces the phrase as a concept name rather than quoting the published text; defensible as written. |
| Cogley & Nason 1995 | T2 | CLEAN | Lineage (DOI 10.1016/0165-1889(93)00781-X); quote removed (see reconciliation #1) |
| Ehlers 2001 | T2 | CLEAN (wording adjusted) | Lineage bibliographic + 2026-06-11 full-text verification (Internet Archive copy + publisher TOC): Ch. 3 "Moving Averages" (pp. 17–32) analyzes SMA/EMA lag; SMA lag plotted (Fig. 3.2, price-ramp, lag = (N−1)/2); the EMA step response analyzed explicitly in text (p. 28: "It is instructive to examine the EMA response to a step function…"); lag framed as an engineering problem to overcome (Ch. 16 "Removing Lag"; Ch. 20). §2.4 wording adjusted in the same gate: the EMA step response is *derived*, not plotted — the plotted EMA step-response curve appears in Ehlers & Way's later "Zero Lag (well, almost)" article, not the 2001 book. |
| Engle 1982 | T3 | CLEAN | Lineage (987–1008 consistent with Springer/academic sources; RePEc's 987–1007 a known one-page artifact) |
| Fama & French 1988 | T3 | CLEAN | Lineage (DOI 10.1086/261535) |
| Franses 1991 | T1 | CLEAN | Lineage (Econ Letters 37, 399–403); AR(1)-inflation wording confirmed from the paper's own summary |
| Hamilton 2018 | T1 | CLEAN | Lineage: the quoted phrase "spurious dynamic relations that have no basis in the underlying data-generating process" verbatim-confirmed against the published abstract (DOI 10.1162/rest_a_00706) |
| Harvey & Jaeger 1993 | T1 | CLEAN | Lineage: quoted phrase "mechanical detrending" verbatim-confirmed in the source abstract (DOI 10.1002/jae.3950080302) |
| Hull 2005 | T2 | CLEAN | Lineage (alanhull.com article; format independently validated by a 2025 Springer citing source) |
| LeBaron 2000 | T2 | CLEAN | Lineage + reconciliation #2 (re-attribution implemented) |
| Lo & MacKinlay 1988 | T3 | CLEAN | Lineage (DOI 10.1093/rfs/1.1.41) |
| Mandelbrot 1963 | T3 | CLEAN | Lineage (JSTOR 2350970) |
| Miller, Muthuswamy & Whaley 1994 | T1 | CLEAN | 5b fresh: exists (RePEc/Wiley), bibliographic exact (JF 49(2), 479–513), thesis supports §2.1 |
| Narayan & Bannigidadmath 2015 | T3 | CLEAN | Lineage (DOI 10.1016/j.jbankfin.2015.05.001) |
| Nelson & Kang 1981 | T2 | CLEAN | Lineage (Econometrica 49, 741–751) |
| Oppenheim & Willsky 1997 | T3 | CLEAN | Lineage + reconciliation #4 |
| Osler 2003 | T2 | CLEAN | Lineage + reconciliation #3; the §2.3 price-level-vs-parameter-space distinction verified accurate |
| Phillips & Jin 2021 | T1 | CLEAN | Lineage (DOI 10.1111/iere.12494); remnant-trend reading supported |
| Poterba & Summers 1988 | T3 | CLEAN | Lineage (DOI 10.1016/0304-405X(88)90021-9) |
| Shintani, Yabu & Nagakura 2012 | T1 | CLEAN | Lineage (DOI 10.1016/j.jeconom.2012.01.019); quoted title exact; golden/dead-cross-under-random-walk reading supported |
| Slutsky 1937 | T1 | CLEAN | Lineage bibliographic + 2026-06-11 full-text-basis verification: the original/basic demonstration (Model I) is a 10-item TRAILING moving summation — each output is a random digit plus the nine that PRECEDED it (Minneapolis Fed, "The Meaning of Slutsky," 2009; Barnett 2006, EJHET 13(3), quoting Slutsky 1937: 108 — "the influence, not of one, but of a number of the preceding causes"); Barnett: "a ten-item moving summation of the first basic series of random numbers" produced the graph juxtaposed to English business cycles 1855–77. None of Slutsky's demonstration models is two-sided/centered. The §2.2 sentence stands as written. Caveat: the e-m-h.org primary PDF is an image-only scan; page references are via Barnett's peer-reviewed quotations of the 1937 text. |
| Sullivan, Timmermann & White 1999 | T2 | CLEAN | Lineage (DOI 10.1111/0022-1082.00163) |
| Working 1960 | T1 | CLEAN | 5b fresh: JSTOR-verified (Econometrica 28(4), 916–918); in-text precision fix applied (first differences of the averages) |
| Yule 1927 | T3 | CLEAN | Lineage (DOI 10.1098/RSTA.1927.0007); the historical 1926→1927 misattribution long fixed |
| Zakamulin & Giner 2020 | T2 | CLEAN | Lineage (DOI 10.1080/14697688.2020.1716057); exact percentages (">90%", EMA pairs ">80%") confirmed via the April-20 source-reading |

**Count note:** 31 references = 29 lineage-verified + Working 1960 + Miller-Muthuswamy-Whaley 1994 (both added at adversarial-review Round 2 and verified fresh). DECISIONS' Phase-5b figure of "27 carried-over" should read 28; corrected in the closing DECISIONS entry.

## Closure record (2026-06-11)

The two open rows were closed by an extended web verification run (full report preserved in the session record):

1. **Slutsky 1937 — confirmed one-sided/trailing; sentence retained as written.** The basic demonstration sums each random digit with the nine preceding it (causal), and Slutsky's own notation describes consequences determined by "preceding causes" (1937: 108, via Barnett). No demonstration model in the paper uses future values. Sources: Minneapolis Fed, "The Meaning of Slutsky" (2009), minneapolisfed.org/article/2009/the-meaning-of-slutsky; Barnett, V. (2006), "Chancing an interpretation: Slutsky's random cycles revisited," *EJHET* 13(3): 411–432, DOI 10.1080/09672560600875596; JSTOR record jstor.org/stable/1907241.
2. **Ehlers 2001 — confirmed at chapter/page level with one precision; §2.4 adjusted in this gate.** Ch. 3 "Moving Averages" (pp. 17–32) analyzes SMA/EMA lag and the EMA's step-function response (p. 28); the SMA's lag is plotted; the EMA step response is derived in text, with the *plotted* EMA step-response curve appearing only in the later Ehlers & Way "Zero Lag (well, almost)" article (mesasoftware.com/papers/ZeroLag.pdf). The manuscript's "analyzed and plotted the step responses of SMA and EMA" was accordingly tightened to "analyzed the lag and step-function response … plotting the SMA's lag and deriving the EMA's step response." Sources: Internet Archive full text archive.org/details/rocketsciencefor0000ehle; Wiley/publisher table of contents.

Both are confirm-and-precision outcomes on otherwise-verified references; no ledger value affected.

## Verdict

31 of 31 CLEAN with documented bases. No fabricated references, no failed claim-support, no quote discrepancies. One wording adjustment arose from this pass (the Ehlers §2.4 precision above) and entered through the standard re-pin gate alongside this file's commit.
