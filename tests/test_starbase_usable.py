"""analysis/starships_sketch/starbase_usable.py: drop unscreenable, absent and core-like targets; flag widespread uncertain ones."""
import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("starbase_usable", ROOT / "analysis" / "starships_sketch" / "starbase_usable.py")
u = importlib.util.module_from_spec(spec); spec.loader.exec_module(u)


def test_usable(tmp_path):
    cols = ["target", "cluster", "length", "specific_hashes", "present_isolates", "cont_Af293", "cont_A1163", "members", "members_with_captain", "members_curated"]
    rows = [("A", 1, 1000, 5, 100, 0.1, 0.1), ("B", 2, 1000, 50, 0, 0.1, 0.1), ("C", 3, 1000, 50, 4600, 0.97, 0.98), ("D", 4, 1000, 50, 3500, 0.84, 1.0),
            ("E", 5, 1000, 50, 2113, 0.056, 0.96), ("F", 6, 1000, 50, 300, 0.05, 0.05), ("G", 7, 1000, 50, 800, 0.95, 0.95)]
    with open(tmp_path / "cc.tsv", "w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(cols)
        for t, c, l, s, p, a, b in rows: w.writerow([t, c, l, s, p, a, b, 1, 0, 0])
    u.main(["--core-check", str(tmp_path / "cc.tsv"), "--out", str(tmp_path / "o")])
    keep = {r["target"]: r["status"] for r in csv.DictReader(open(tmp_path / "o" / "usable_targets.tsv"), delimiter="\t")}
    drop = {r["target"]: r["reason"] for r in csv.DictReader(open(tmp_path / "o" / "dropped_targets.tsv"), delimiter="\t")}
    assert keep == {"E": "uncertain", "F": "usable", "G": "usable"}                       # G is in the references but not widespread, so it stays
    assert set(drop) == {"A", "B", "C", "D"} and "core-like" in drop["C"] and "probably core" in drop["D"] and "no isolate" in drop["B"]
