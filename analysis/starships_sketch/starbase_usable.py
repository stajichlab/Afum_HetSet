#!/usr/bin/env python3
"""Choose the Starbase targets worth profiling from core_check.tsv (starbase_oneoffs/core_check.py).

Dropped: fewer than --min-specific specific hashes (cannot be screened), present in no isolate, or core-like (present in more than --core-prevalence isolates
and contained in both reference assemblies at --core-containment or more; probable-core at --probable-containment). Flagged `uncertain`: present in more than
--core-prevalence isolates but not core-like (widespread, may be a real accessory region). Writes OUT/usable_targets.tsv and OUT/dropped_targets.tsv.

    starbase_usable.py --core-check core_check.tsv --out starbase/
"""
import argparse
import csv
import os


def classify(r, a):
    spec, pres = int(r["specific_hashes"]), int(r["present_isolates"])
    c1, c2 = float(r["cont_Af293"]), float(r["cont_A1163"])
    if spec < a.min_specific:
        return "drop", f"fewer than {a.min_specific} specific hashes"
    if pres == 0:
        return "drop", "present in no isolate"
    if pres > a.core_prevalence and min(c1, c2) >= a.core_containment:
        return "drop", "core-like (widespread, in both references)"
    if pres > a.core_prevalence and min(c1, c2) >= a.probable_containment:
        return "drop", "probably core (widespread, mostly in both references)"
    if pres > a.core_prevalence:
        return "keep", "uncertain"
    return "keep", "usable"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--core-check", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--min-specific", type=int, default=10); ap.add_argument("--core-prevalence", type=int, default=2000)
    ap.add_argument("--core-containment", type=float, default=0.9); ap.add_argument("--probable-containment", type=float, default=0.8)
    a = ap.parse_args(argv)
    rows = list(csv.DictReader(open(a.core_check), delimiter="\t"))
    os.makedirs(a.out, exist_ok=True)
    keep, drop = [], []
    for r in rows:
        verdict, why = classify(r, a)
        (keep if verdict == "keep" else drop).append((r, why))
    cols = ["target", "cluster", "length", "specific_hashes", "present_isolates", "cont_Af293", "cont_A1163", "members", "members_with_captain", "members_curated"]
    for name, items, extra in (("usable_targets.tsv", keep, "status"), ("dropped_targets.tsv", drop, "reason")):
        with open(f"{a.out}/{name}", "w", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(cols + [extra])
            for r, why in sorted(items, key=lambda x: x[0]["target"]):
                w.writerow([r[c] for c in cols] + [why])
    print(f"{len(rows)} targets: {len(keep)} kept ({sum(1 for _, w in keep if w == 'uncertain')} uncertain), {len(drop)} dropped")


if __name__ == "__main__":
    main()
