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
    # --- Schelling (E5) daily layer addition: NQ replaces NDX in B.7 ---------
    ("NQ.1D",    "CME_MINI_NQ1!, 1D_de2b2.csv",   6753, "105b8be21760373023f21aa58777933d4299fcfa6a8bdd591e260fb562538375"),
    # --- Schelling (E5) hourly layer: 12 instruments -------------------------
    ("NQ.60",    "CME_MINI_NQ1!, 60_985ba.csv",  24757, "cb78020d2e0af9dd6d08c8009e375f51fc87d4966680ce61042f51213862c2c7"),
    ("NI225.60", "TVC_NI225, 60_b5054.csv",      20848, "0d5756d747cdcbdd7f81565e28bbfe767b28d9d3d5feb6cfd9cfecb0262211b9"),
    ("DAX.60",   "XETR_DLY_DAX, 60_82c16.csv",   20964, "d5f30c75a50c611e4c6e9d86585b8c0b7577a7a45fb5fb260bd91fcdb4ce9745"),
    ("FTSE.60",  "IG_FTSE, 60_6e958.csv",        14458, "80e3bc00085f1d4cf197b87f550d6fac38238b37bafbad496221e360930f44bf"),
    ("HSI.60",   "HKEX_DLY_HSI1!, 60_7c166.csv", 17486, "f3ee58c0f215c592947a2e6e471bfa87a2a5acabe9f7eab8c3a7f0607b1c732e"),
    ("CL.60",    "NYMEX_CL1!, 60_72c46.csv",     24815, "76c86cdd31cde67275a79e83f5115c9c3abd28fe2ade7317d903701e2e64d123"),
    ("GC.60",    "COMEX_GC1!, 60_26eca.csv",     23682, "ea5c1db35ae672c21babff92906bb111a11337420e120ea2a11d62567cc345e0"),
    ("ZN.60",    "CBOT_ZN1!, 60_81641.csv",      23636, "09d2f935b27a4467bb468e75a98cf076adce3022cd1ad1e4f75dfb235c11c56d"),
    ("6E.60",    "CME_6E1!, 60_df31a.csv",       23715, "bd832acaff17c155d64fa963b3eb95ffac6ad6e3175f353dacb75030f8c5f2d9"),
    ("6J.60",    "CME_6J1!, 60_5c795.csv",       23715, "0c129e5897ddf7e44e1d416a211063c672003912b98abbf0b21f295a5a98acbd"),
    ("ES.60",    "CME_MINI_ES1!, 60_127a6.csv",  24757, "af9636e77793376e4eeae541b5c3d440619f0f89d6473d5fa3df34f5f8716b87"),
    ("NKD.60",   "CME_NKD1!, 60_ffee5.csv",      23577, "eb2be2bbfaf556329630e47396e413181ad6d003867c45596ef3177d247d0bb3"),
    # --- Schelling (E5) 5-minute layer: 8 instruments ------------------------
    ("ES.5",     "CME_MINI_ES1!, 5_28d89.csv",   21116, "4c42d1c46421ed8696f8998ab855fe1ac6cb4f9a2f20d24a90bb8f027b689e12"),
    ("NQ.5",     "CME_MINI_NQ1!, 5_c2781.csv",   21117, "68a8c0e43f6182e65d56ac9c08dc65a3cb186c478bff5c5fa619b5c1cb82bed7"),
    ("GC.5",     "COMEX_GC1!, 5_f87e8.csv",      21176, "0348a5ba6186b9b90b47050bbff9031fd67c593ad0852669230da1722d820e39"),
    ("CL.5",     "NYMEX_CL1!, 5_a29b4.csv",      21180, "49babb3e90a39e54c26f66fd9bdd77672f88a1a13c79ef7c52b2962064956c69"),
    ("ZN.5",     "CBOT_ZN1!, 5_bdc1e.csv",       20877, "371db6204f513861aaa2b19d398494bce6ae6ebc583e456281d6d19387073d0c"),
    ("6E.5",     "CME_6E1!, 5_d72d6.csv",        20059, "182f84d3ff659ce269be2da6af8005e2b164ff3afabc3c5d35c510d427b4300a"),
    ("6J.5",     "CME_6J1!, 5_c0f96.csv",        20059, "eb9fa9fe87e55b6b1142f9d86208e5c7db447cc90d569f70771978205a403044"),
    ("NKD.5",    "CME_NKD1!, 5_f1b66.csv",       20757, "52ccdc7ab16bd231131be0c73f318248320f767415add2f282561472910f6411"),
    # --- Schelling (E5) monthly layer: 2 instruments -------------------------
    ("SPX.1M",   "SP_SPX, 1M_9ba20.csv",          1668, "895f28d799cda2b1c8971a62964beb95186c3db69f7cebe2f848272f94370206"),
    ("GC.1M",    "COMEX_GC1!, 1M_958cd.csv",       615, "998151626467226d5578a9a1e827f5175d4a5854576122f6210cc1b443d1ef1c"),
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
