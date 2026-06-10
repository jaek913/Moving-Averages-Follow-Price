"""
make_fixture.py -- regenerate the deliberately broken selftest fixture.

Phase 3 (Research-to-Publication Standard v1.2). Reads the repo's claims.lock
and writes verification/fixtures/broken_claims.lock with exactly three planted
defects, which verify.py --selftest must catch (turn RED):

  1. datasets.SPX.sha256 corrupted (all zeros)        -> CHECK 1 failure
  2. claims[0] (LB-001) first check value 44 -> 43    -> CHECK 2 failure
  3. claims[8] (LB-009) CIC signed -> false           -> CHECK 3 failure

Deterministic: identical claims.lock in -> identical fixture bytes out.

Run from the repo root:  python verification\\make_fixture.py
"""
import copy
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lock = json.load(open(os.path.join(REPO, "claims.lock")))
b = copy.deepcopy(lock)
b["schema"] += " -- DELIBERATELY BROKEN SELFTEST FIXTURE"
b["datasets"]["SPX"]["sha256"] = "0" * 64
b["claims"][0]["checks"][0]["value"] = 43
b["claims"][8]["cic"]["signed"] = False

out_dir = os.path.join(REPO, "verification", "fixtures")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "broken_claims.lock")
with open(out, "w", newline="\n") as f:
    json.dump(b, f, indent=2)
    f.write("\n")
print(f"fixture written: {out} (3 planted defects: hash, value, CIC)")
