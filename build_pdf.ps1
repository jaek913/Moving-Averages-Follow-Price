# =====================================================================
# Lagging Truth - series PDF build  (Research-to-Publication Standard)
# Paper: Moving Averages Follow Price
# =====================================================================
# Adapted from the current-Standard copy (Recession-Detection-System),
# which carries:
#   - the stale-output guard: SUCCESS requires the PDF's LastWriteTime to
#     be NEWER than the pre-build stamp (an exists-only check reports
#     SUCCESS on a permission-denied write; closed structurally here), and
#   - the character-level collision lesson in its header notes (word-level
#     comparison is structurally blind to interleaved-character overlap).
#
# PAPER-SPECIFIC DEVIATIONS (this copy):
#   1. The committed manuscript carries its OWN YAML title block (title /
#      author / date incl. DOI) - no YAML injection, no H1 strip. Pandoc
#      reads the source front matter directly.
#   2. LB anchor strip: the source prints every load-bearing value with an
#      adjacent {{LB-nnn}} anchor tag (verify.py CHECK 4 ties each value to
#      the ledger at its anchor). The tags are verification plumbing, not
#      prose: the PDF-only TEMP copy removes them. Committed artifacts
#      untouched.
#   3. Series-conformance transforms (PDF-only): top-level heading dots
#      stripped ('## 1. Introduction' prints as '1 Introduction'); JEL
#      separators comma -> semicolon. Appendix headings are already
#      colon-style in the source; no transform needed.
#   4. In-text citations are conventional parenthetical author-year and
#      print verbatim (no transform; series variance ruled as-is
#      2026-08-07, standardization tracked post-launch).
#
# How to run (from the repo root):  .\build_pdf.ps1
# Requires: pandoc + xelatex on PATH; Cambria + Cambria Math installed.
# =====================================================================

$ErrorActionPreference = "Stop"

# --------------------------- SETTINGS -------------------------------
$PaperDir   = Join-Path $PSScriptRoot "paper"
$Slug       = "Moving-Averages-Follow-Price"
$Manuscript = Join-Path $PaperDir "Moving-Averages-Follow-Price.md"
# --------------------------------------------------------------------

$Output = Join-Path $PaperDir "$Slug.pdf"

Write-Host ""
Write-Host "=== Lagging Truth PDF build: $Slug ===" -ForegroundColor Cyan

foreach ($t in @("pandoc","xelatex")) {
    if (-not (Get-Command $t -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: '$t' not found on PATH." -ForegroundColor Red
        exit 1
    }
    Write-Host ("[ OK ] {0} -> {1}" -f $t, (Get-Command $t).Source)
}
if (-not (Test-Path $Manuscript)) { Write-Host "ERROR: manuscript not found: $Manuscript" -ForegroundColor Red; exit 1 }
Write-Host "[ OK ] manuscript: $Manuscript"

# --- stale-output guard: remember the pre-build stamp ---
$PreBuildStamp = $null
if (Test-Path $Output) {
    $PreBuildStamp = (Get-Item $Output).LastWriteTime
    Write-Host ("[ OK ] existing PDF stamp recorded: {0}" -f $PreBuildStamp)
} else {
    Write-Host "[ OK ] no existing PDF (first build)"
}

# --- series header.tex (Cambria + Cambria Math) ---
$Header = @'
% header.tex - Lagging Truth series preamble (Cambria + Cambria Math)
\usepackage{unicode-math}
\setmainfont{Cambria}[Ligatures=NoCommon]
\setmathfont{Cambria Math}
\usepackage[margin=1.25in]{geometry}
\linespread{1.15}
\setlength{\parskip}{6pt}
\setlength{\parindent}{0pt}
\setlength{\emergencystretch}{3em}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{mathtools}
\usepackage{cases}
\usepackage{pifont}
\usepackage{titlesec}
\titleformat{\section}{\Large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{\thesubsubsection}{1em}{}
\usepackage{booktabs}
\usepackage{array}
\usepackage{tabularx}
\usepackage{longtable}
\usepackage{etoolbox}
\AtBeginEnvironment{longtable}{\small}
\setlength{\tabcolsep}{4pt}
\usepackage{fvextra}
\DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}
\RecustomVerbatimEnvironment{verbatim}{Verbatim}{breaklines,breakanywhere}
\usepackage{titling}
\pretitle{\begin{center}\LARGE}
\posttitle{\par\end{center}\vspace{1em}\begin{center}\rule{0.35\textwidth}{0.5pt}\end{center}\vspace{0.5em}}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
\numberwithin{equation}{section}
\usepackage{xurl}
'@

# --- raw-Unicode mappings (Cambria text face lacks these) ---
$Header = $Header + "`n% raw-Unicode mappings (added by build script)`n\usepackage{newunicodechar}`n"
$Header = $Header + "\newunicodechar{$([char]0x2713)}{\ding{51}}`n"
$Header = $Header + "\newunicodechar{$([char]0x2717)}{\ding{55}}`n"
$Header = $Header + "\newunicodechar{$([char]0x2020)}{\dag}`n"
$Header = $Header + "\newunicodechar{$([char]0x2265)}{\ensuremath{\geq}}`n"
$Header = $Header + "\newunicodechar{$([char]0x2264)}{\ensuremath{\leq}}`n"
$Header = $Header + "\newunicodechar{$([char]0x00D7)}{\ensuremath{\times}}`n"
$Header = $Header + "\newunicodechar{$([char]0x00B1)}{\ensuremath{\pm}}`n"
$Header = $Header + "\newunicodechar{$([char]0x2212)}{\ensuremath{-}}`n"

$Metadata = @'
---
documentclass: article
fontsize: 11pt
papersize: letter
colorlinks: true
linkcolor: blue
urlcolor: blue
citecolor: blue
header-includes:
  - \usepackage{microtype}
...
'@

$utf8NoBom    = New-Object System.Text.UTF8Encoding($false)
$Tmp          = [System.IO.Path]::GetTempPath()
$HeaderPath   = Join-Path $Tmp "lt_header.tex"
$MetadataPath = Join-Path $Tmp "lt_metadata.yaml"
[System.IO.File]::WriteAllText($HeaderPath,   $Header,   $utf8NoBom)
[System.IO.File]::WriteAllText($MetadataPath, $Metadata, $utf8NoBom)
Write-Host "[ OK ] header.tex + metadata.yaml written to TEMP (UTF-8 no-BOM)"

# --- PDF-only TEMP transforms (committed artifacts untouched) ---
$man = [System.IO.File]::ReadAllText($Manuscript, $utf8NoBom)

# 1) LB anchor strip (verification plumbing; see header note 2)
$man = [regex]::Replace($man, '\s*\{\{LB-\d+\}\}', '')

# 1a) standalone approx-tilde: '$\sim$' as a lone token requests U+223C from
#     the TEXT font (missing in Cambria Italic -> dropped glyph, caught by the
#     build warning). The paper's own approx convention elsewhere is ASCII '~'
#     (e.g. '~53%'); conform the two standalone tokens. Distributional \sim
#     inside larger math expressions is untouched (renders via Cambria Math).
$man = $man.Replace('$\sim$', '~')

# 2) Series heading style: '## 2. Related Literature' -> '## 2 Related Literature'
$man = [regex]::Replace($man, '(?m)^## (\d+)\. ', '## $1 ')

# 3) Series JEL separator: semicolons, not commas (label preserved)
$man = [regex]::Replace($man, '(?m)^(\*\*JEL Classification:\*\*[^\r\n]*)$', { param($m) $m.Groups[1].Value -replace ', ', '; ' })

# 4) slash-run break opportunities (long-table insurance; invisible unless
#    a line needs the break point)
$man = [regex]::Replace($man, '(?<=[A-Za-z0-9])/(?=[A-Za-z0-9])', '/\allowbreak ')

$ManTmp = Join-Path $Tmp "lt_manuscript_pdf.md"
[System.IO.File]::WriteAllText($ManTmp, $man, $utf8NoBom)
Write-Host "[ OK ] PDF-only transforms applied -> $ManTmp"

$Inputs = @($ManTmp)

# --- render ---
Write-Host "Building PDF -> $Output" -ForegroundColor Cyan
& pandoc @Inputs `
    --pdf-engine=xelatex `
    --metadata-file="$MetadataPath" `
    --include-in-header="$HeaderPath" `
    --shift-heading-level-by=-1 `
    --output="$Output"

# --- success check: EXISTS *and* actually rewritten by this run ---
if (-not (Test-Path $Output)) {
    Write-Host "=== BUILD FAILED === (no output produced; see xelatex errors above)" -ForegroundColor Red
    exit 1
}
$PostBuildStamp = (Get-Item $Output).LastWriteTime
if ($PreBuildStamp -and ($PostBuildStamp -le $PreBuildStamp)) {
    Write-Host "=== BUILD FAILED === STALE OUTPUT" -ForegroundColor Red
    Write-Host ("The PDF on disk was NOT rewritten by this run (stamp unchanged: {0})." -f $PostBuildStamp) -ForegroundColor Red
    Write-Host "The usual cause is that the PDF is open in a viewer, so the write was denied." -ForegroundColor Red
    Write-Host "Close the PDF and re-run. Do NOT ship this file - it is the previous build." -ForegroundColor Red
    exit 1
}
$kb = [math]::Round((Get-Item $Output).Length / 1KB, 1)
Write-Host "=== SUCCESS ===" -ForegroundColor Green
Write-Host ("PDF: {0}  ({1} KB, modified {2})" -f $Output, $kb, $PostBuildStamp)
Write-Host "Stale-output guard: PASSED (file rewritten by this run)."
