"""
verify.py -- Phase 3 integrity checker (Research-to-Publication Standard v1.2).

"Moving Averages Follow Price". Done = this script exits green.

THE CONTRACT
    A number may appear in the paper only if a committed script, run on hashed
    input data, regenerates it on demand. This checker enforces that contract:

    CHECK 1  Re-hash every raw input against the claims.lock datasets block.
    CHECK 2  Re-run every generating script and compare each load-bearing value
             to the ledger within its declared tolerance (--quick compares the
             committed analysis/outputs/*.json instead of re-running).
    CHECK 3  Every claim's 7-point CIC flags are all true and signed.
    CHECK 4  Every ledger value appears in the paper at its {{LB-id}} anchor
             (SKIPPED until paper/ contains a paper*.md -- Phase 4).

    Exit 0 (green) only if all non-skipped checks pass.

MODES
    python verify.py              full: re-hash + re-run + compare + CIC + paper
    python verify.py --quick      compare committed outputs (no re-run)
    python verify.py --replicator hash mismatches downgrade to WARN if the local
                                  file is a plausible fresh vendor export (same
                                  start date, >= row count); claims still must
                                  pass within tolerance (SOURCES.md schema)
    python verify.py --selftest   run the checker against the deliberately
                                  broken fixture in verification/fixtures/ and
                                  PASS only if the checker turns RED on it

TOLERANCES (DECISIONS.md 2026-06-09)
    integers / booleans: exact; deterministic floats: rel 1e-12;
    optimizer-dependent (GARCH MLE): abs 0.1 (percentage-point scale).

RUNTIME
    Full mode re-runs all seven analysis scripts (~15-30 minutes; E5 and E7
    dominate). Set LT_DATA_DIR to the project-local data store if it is not at
    the default location recorded in data/SOURCES.md.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.join(REPO, "analysis")
OUTPUTS = os.path.join(ANALYSIS, "outputs")
sys.path.insert(0, ANALYSIS)

GREEN, RED, YELLOW, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[0m"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve(obj, path):
    """claims.lock json_path: dot keys; [int] index; [?f=v&g=w] unique query."""
    tokens = re.findall(r"[^.\[\]]+|\[[^\]]*\]", path)
    cur = obj
    for tok in tokens:
        if tok.startswith("["):
            inner = tok[1:-1]
            if inner.startswith("?"):
                conds = dict(p.split("=", 1) for p in inner[1:].split("&"))
                matches = [x for x in cur
                           if all(str(x.get(k)) == v for k, v in conds.items())]
                if len(matches) != 1:
                    raise KeyError(f"query [{inner}]: {len(matches)} matches")
                cur = matches[0]
            else:
                cur = cur[int(inner)]
        else:
            cur = cur[tok]
    return cur


def within(value, ledger, tol):
    if isinstance(ledger, bool) or isinstance(value, bool):
        return value == ledger
    if isinstance(ledger, (int, float)) and isinstance(value, (int, float)):
        diff = abs(float(value) - float(ledger))
        if "abs" in tol:
            return diff <= tol["abs"]
        if "rel" in tol:
            scale = max(abs(float(ledger)), 1e-300)
            return diff <= tol["rel"] * scale
    return value == ledger


def data_dir():
    d = os.environ.get("LT_DATA_DIR")
    if d:
        return d
    try:
        from decomposition import DATA_DIR
        return DATA_DIR
    except Exception:
        return None


def check1_datasets(lock, replicator, fails, warns):
    dd = data_dir()
    if dd is None or not os.path.isdir(dd):
        fails.append(f"CHECK1: data store not found (LT_DATA_DIR='{dd}')")
        return
    for key, ds in lock["datasets"].items():
        path = os.path.join(dd, ds["file"])
        if not os.path.exists(path):
            fails.append(f"CHECK1: {key}: missing file {ds['file']}")
            continue
        actual = sha256_of(path)
        if actual == ds["sha256"]:
            continue
        if replicator:
            ok, why = _plausible_fresh_export(path, ds)
            if ok:
                warns.append(f"CHECK1: {key}: hash differs from author archive; "
                             f"accepted as fresh export ({why})")
                continue
            fails.append(f"CHECK1: {key}: hash mismatch and not a plausible "
                         f"fresh export ({why})")
        else:
            fails.append(f"CHECK1: {key}: SHA-256 mismatch "
                         f"(got {actual[:16]}..., ledger {ds['sha256'][:16]}...)")


def _plausible_fresh_export(path, ds):
    """Replicator acceptance per SOURCES.md: same start date, >= row count."""
    try:
        import pandas as pd
        df = pd.read_csv(path)
        cols = {c.strip().lower(): c for c in df.columns}
        if "time" not in cols or "close" not in cols:
            return False, "no time/close columns"
        n = len(df)
        if n < ds["rows"]:
            return False, f"only {n} rows < ledger {ds['rows']}"
        start = str(df[cols["time"]].iloc[0])[:10]
        ledger_start = ds["coverage"].split("..")[0]
        first = pd.to_datetime(start, format="mixed", errors="coerce")
        ref = pd.to_datetime(ledger_start, errors="coerce")
        if first is None or ref is None or first.date() != ref.date():
            return False, f"start {start} != ledger {ledger_start}"
        return True, f"{n} rows >= {ds['rows']}, start matches"
    except Exception as e:
        return False, f"unreadable ({e})"


def check2_claims(lock, rerun, fails):
    scripts = sorted({c["script"] for c in lock["claims"]})
    if rerun:
        env = dict(os.environ)
        for s in scripts:
            spath = os.path.join(REPO, s)
            print(f"  re-running {s} ...")
            r = subprocess.run([sys.executable, spath], capture_output=True,
                               text=True, env=env, cwd=REPO)
            if r.returncode != 0:
                fails.append(f"CHECK2: {s} exited {r.returncode}: "
                             f"{r.stderr.strip()[-400:]}")
    outputs = {}
    for c in lock["claims"]:
        out = c["output"]
        if out not in outputs:
            opath = os.path.join(REPO, out)
            if not os.path.exists(opath):
                fails.append(f"CHECK2: {c['id']}: output missing: {out}")
                outputs[out] = None
                continue
            outputs[out] = json.load(open(opath))
        data = outputs[out]
        if data is None:
            continue
        for chk in c["checks"]:
            try:
                fresh = resolve(data, chk["json_path"])
            except Exception as e:
                fails.append(f"CHECK2: {c['id']}: path '{chk['json_path']}' "
                             f"unresolvable: {e}")
                continue
            if not within(fresh, chk["value"], c["tolerance"]):
                fails.append(f"CHECK2: {c['id']}: {chk['json_path']} = {fresh} "
                             f"vs ledger {chk['value']} "
                             f"(tolerance {c['tolerance']})")


CIC_FLAGS = ["reexecutes_to_claim", "index_row_alignment",
             "nan_gap_handling_explicit", "no_look_ahead",
             "overlap_subsample_consistent", "no_cross_boundary_computation",
             "input_integrity_vs_claim"]


def check3_cic(lock, fails):
    for c in lock["claims"]:
        cic = c.get("cic", {})
        bad = [f for f in CIC_FLAGS if cic.get(f) is not True]
        if bad:
            fails.append(f"CHECK3: {c['id']}: CIC flags not true: {bad}")
        if cic.get("signed") is not True or not cic.get("signed_by"):
            fails.append(f"CHECK3: {c['id']}: CIC not signed")


def check4_paper(lock, fails, skips):
    paper_dir = os.path.join(REPO, "paper")
    papers = []
    if os.path.isdir(paper_dir):
        papers = [f for f in os.listdir(paper_dir)
                  if f.startswith("paper") and f.endswith(".md")
                  and "companion" not in f]
    if not papers:
        skips.append("CHECK4: no paper/paper*.md yet (Phase 4) -- skipped")
        return
    text = ""
    for p in papers:
        text += open(os.path.join(paper_dir, p), encoding="utf-8").read()
    for c in lock["claims"]:
        if "{{" + c["id"] + "}}" not in text:
            fails.append(f"CHECK4: {c['id']}: anchor {{{{{c['id']}}}}} "
                         f"not found in paper")


def run(lock_path, rerun, replicator):
    lock = json.load(open(lock_path))
    fails, warns, skips = [], [], []
    print(f"verify.py -- ledger: {lock_path}")
    print(f"[1/4] datasets: re-hashing {len(lock['datasets'])} inputs ...")
    check1_datasets(lock, replicator, fails, warns)
    print(f"[2/4] claims: {len(lock['claims'])} claims, "
          f"{sum(len(c['checks']) for c in lock['claims'])} checks "
          f"({'re-running scripts' if rerun else 'quick: committed outputs'}) ...")
    check2_claims(lock, rerun, fails)
    print(f"[3/4] CIC: 7 flags x {len(lock['claims'])} claims ...")
    check3_cic(lock, fails)
    print("[4/4] paper anchors ...")
    check4_paper(lock, fails, skips)
    for w in warns:
        print(f"{YELLOW}WARN{RESET}  {w}")
    for s in skips:
        print(f"{YELLOW}SKIP{RESET}  {s}")
    for f in fails:
        print(f"{RED}FAIL{RESET}  {f}")
    if fails:
        print(f"\n{RED}RED -- {len(fails)} failure(s).{RESET}")
        return 1
    print(f"\n{GREEN}GREEN -- all checks passed "
          f"({len(warns)} warn, {len(skips)} skipped).{RESET}")
    return 0


def selftest():
    """The checker must turn RED on the deliberately broken fixture."""
    fixture = os.path.join(REPO, "verification", "fixtures",
                           "broken_claims.lock")
    if not os.path.exists(fixture):
        print(f"{RED}SELFTEST FAIL: fixture missing: {fixture}{RESET}")
        return 1
    print("selftest: running checker against the deliberately broken fixture")
    print("-" * 70)
    rc = run(fixture, rerun=False, replicator=False)
    print("-" * 70)
    if rc != 0:
        print(f"{GREEN}SELFTEST PASS -- checker turned RED on the broken "
              f"fixture, as required.{RESET}")
        return 0
    print(f"{RED}SELFTEST FAIL -- checker passed a fixture with a corrupted "
          f"hash, a corrupted value, and an unsigned CIC.{RESET}")
    return 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="compare committed outputs; do not re-run scripts")
    ap.add_argument("--replicator", action="store_true",
                    help="accept fresh vendor exports per SOURCES.md tolerance")
    ap.add_argument("--selftest", action="store_true",
                    help="verify the checker turns RED on the broken fixture")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    sys.exit(run(os.path.join(REPO, "claims.lock"),
                 rerun=not a.quick, replicator=a.replicator))
