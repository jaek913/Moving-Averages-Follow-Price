"""
pull.py -- Data-layer verifier for "Moving Averages Follow Price".

This project's price data cannot be pulled programmatically (TradingView exports
are made by hand and are exchange-licensed), so unlike a download script, this
script's job is VERIFICATION: it checks that every file named in data/SOURCES.md
is present in the data directory and matches its recorded full SHA-256 and
observation count exactly.

HOW TO RUN (PowerShell)
    $env:LT_DATA_DIR = "C:\\Users\\jaek9\\Documents\\LaggingTruth\\Moving-Averages-Follow-Price"
    python data\\pull.py

Exit code 0 and "ALL n FILES VERIFIED" = the data layer is green.
Any mismatch prints a per-file report and exits 1. Do not run analyses on a red
data layer.

The MANIFEST below is the machine-readable mirror of data/SOURCES.md. If they
ever disagree, SOURCES.md is wrong or this file is stale -- fix whichever
diverged and record it in DECISIONS.md.
"""
import hashlib
import os
import sys

DATA_DIR = os.environ.get(
    "LT_DATA_DIR",
    r"C:\Users\jaek9\Documents\LaggingTruth\Moving-Averages-Follow-Price",
)

# (instrument, filename, expected_obs, full_sha256)
MANIFEST = [
    ("SPX",   "SP_SPX, 1D_5871b.csv",         25187, "c75e8fb61149f5ba606ebe5a3881db40a1015ff49e322a590cf6e7a7d537cbe7"),
    ("NDX",   "NASDAQ_DLY_NDX, 1D_e6961.csv", 10359, "0e93da6e7e3a97cbc377c5b8ad9930ae3261a28d22410322ee5c6e9ec250c1b5"),
    ("NI225", "TVC_NI225, 1D_8be07.csv",      19040, "271da7a404086ff9c939daf8c8ff18cf3eb4d45c60214a3e5e53a42f1ee70228"),
    ("DAX",   "XETR_DLY_DAX, 1D_cd703.csv",   14143, "4531616311c17b8cbd5781ba20717ac5a93c31d348282474fff9c39f7c144491"),
    ("FTSE",  "IG_FTSE, 1D_c9679.csv",         8615, "ae76f4a65e6c65e96ea141fe4d23e8348a7033d9e8348a46efd681c5dbf31e1c"),
    ("HSI",   "HKEX_DLY_HSI1!, 1D_57a14.csv",  9585, "840dbd3fce9da09b06d5e4aa459a8070ed352735230bd171bbcc2546e69ef99c"),
    ("CL",    "NYMEX_CL1!, 1D_de4b1.csv",     10798, "f32fb49cd7653c01cbcd91e43a58615811be04f4ed84c22d4b061711c96494f4"),
    ("GC",    "COMEX_GC1!, 1D_1e2f0.csv",     12878, "cd71339445b1c5107c808b8dad76b77383aadada26b0b240a086d323430e67d0"),
    ("ZN",    "CBOT_ZN1!, 1D_3436b.csv",      11058, "d2d88f9c7614e0c9995952a885f1a297c4fc6eb1a3dfcbef6e593b45fcd44840"),
    ("6E",    "CME_6E1!, 1D_9dd8b.csv",        6451, "4422e3a4631493125d31eaa3906e3bb74351c2b9b90ede76bd3dd53651b06c5f"),
    ("6J",    "CME_6J1!, 1D_01e58.csv",        6373, "f342d871ee4af468f323633e7f857725da67efc82259b3e1d28bb2384b21006c"),
    ("ES",    "CME_MINI_ES1!, 1D_40b30.csv",   7210, "b81fc7a91bd0ee202291b8bfc9411f812f7f99042f167fd87819026fb2d67bab"),
    ("NKD",   "CME_NKD1!, 1D_92650.csv",       5574, "c8468adf2dac6bbf9ec385bfefb69414a3e0e26a639722bccfaface33875afd0"),
]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def count_rows(path):
    """Data rows = physical lines minus the header (matches pandas.read_csv row count
    for these exports, which contain no embedded newlines)."""
    n = 0
    with open(path, "rb") as f:
        for _ in f:
            n += 1
    return n - 1


def main():
    print(f"Data dir: {DATA_DIR}")
    if not os.path.isdir(DATA_DIR):
        print("FAIL: data directory does not exist.")
        return 1
    failures = 0
    print(f"{'Inst':<7}{'present':<9}{'obs_ok':<8}{'sha_ok':<8}file")
    for inst, fn, exp_obs, exp_sha in MANIFEST:
        path = os.path.join(DATA_DIR, fn)
        if not os.path.exists(path):
            print(f"{inst:<7}{'MISSING':<9}{'-':<8}{'-':<8}{fn}")
            failures += 1
            continue
        obs = count_rows(path)
        sha = sha256_of(path)
        ok_obs = obs == exp_obs
        ok_sha = sha == exp_sha
        if not (ok_obs and ok_sha):
            failures += 1
        print(f"{inst:<7}{'yes':<9}{str(ok_obs):<8}{str(ok_sha):<8}{fn}"
              + ("" if ok_obs else f"  [obs {obs} != {exp_obs}]")
              + ("" if ok_sha else f"  [sha {sha[:16]}... != {exp_sha[:16]}...]"))
    print()
    if failures:
        print(f"FAIL: {failures} file(s) missing or mismatched. Do not run analyses.")
        return 1
    print(f"ALL {len(MANIFEST)} FILES VERIFIED against data/SOURCES.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
