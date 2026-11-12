"""analysis/starships_sketch/strain_starship_heatmap.py: PNG and PDF written, rows sorted by lineage then clone, partial and absent cells handled."""
import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("strain_starship_heatmap", ROOT / "analysis" / "starships_sketch" / "strain_starship_heatmap.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)


def write(path, cols, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)


def test_heatmap(tmp_path):
    els = ["bafA", "Janus-h1", "Janus-h2", "Lamia-h1"]
    meta = ["strain", "sample_id", "clone", "lineage", "n_present", "present_elements", "bafA_all_hits", "bafA_class"]
    rows = [dict(strain="eAF2", sample_id="S2", clone="9", lineage="150", n_present="1", present_elements="Janus-h1", bafA_all_hits="0", bafA_class="none", bafA="-", **{"Janus-h1": "P", "Janus-h2": "p", "Lamia-h1": "-"}),
            dict(strain="eAF1", sample_id="S1", clone="3", lineage="28", n_present="2", present_elements="bafA;Lamia-h1", bafA_all_hits="3", bafA_class="cluster_linked", bafA="P", **{"Janus-h1": "-", "Janus-h2": "-", "Lamia-h1": "P"}),
            dict(strain="eAF3", sample_id="S3", clone="", lineage="", n_present="0", present_elements="", bafA_all_hits="2", bafA_class="standalone_divergent", bafA="-", **{"Janus-h1": "-", "Janus-h2": "-", "Lamia-h1": "-"})]
    write(tmp_path / "calls.tsv", meta + els, rows)
    write(tmp_path / "fractions.tsv", ["strain", "sample_id", "clone", "lineage"] + els,
          [dict(strain=r["strain"], sample_id=r["sample_id"], clone=r["clone"], lineage=r["lineage"], bafA="0.9", **{"Janus-h1": "0.8", "Janus-h2": "0.4", "Lamia-h1": "0.95"}) for r in rows])
    loaded, fr, cols, _ = h.load(str(tmp_path / "calls.tsv"), str(tmp_path / "fractions.tsv"))
    assert [r["strain"] for r in loaded] == ["eAF1", "eAF2", "eAF3"]                          # lineage 28 < 150 < none
    assert cols == ["bafA", "Janus-h1", "Janus-h2", "Lamia-h1"]
    h.main(["--calls", str(tmp_path / "calls.tsv"), "--fractions", str(tmp_path / "fractions.tsv"), "--title", "t", "--out", str(tmp_path / "hm")])
    assert (tmp_path / "hm.png").stat().st_size > 5000 and (tmp_path / "hm.pdf").read_bytes().startswith(b"%PDF")


def test_heatmap_with_starbase_columns(tmp_path):
    meta = ["strain", "sample_id", "clone", "lineage", "n_present", "present_elements", "bafA_all_hits", "bafA_class", "n_starbase_present"]
    els = ["bafA", "Janus-h1", "SBc002", "SBc010"]
    rows = [dict(strain="eAF1", sample_id="S1", clone="3", lineage="28", n_present="1", present_elements="Janus-h1", bafA_all_hits="0", bafA_class="none", n_starbase_present="1",
                 bafA="-", **{"Janus-h1": "P", "SBc002": "P", "SBc010": "-"})]
    write(tmp_path / "calls.tsv", meta + els, rows)
    write(tmp_path / "fractions.tsv", ["strain", "sample_id", "clone", "lineage"] + els, [dict(strain="eAF1", sample_id="S1", clone="3", lineage="28", bafA="0", **{"Janus-h1": "0.9", "SBc002": "0.8", "SBc010": "0"})])
    loaded, fr, cols, _ = h.load(str(tmp_path / "calls.tsv"), str(tmp_path / "fractions.tsv"))
    assert cols == ["bafA", "Janus-h1", "SBc002", "SBc010"] and h.family("SBc002") == "Starbase" and h.family("Janus-h1") == "Janus"
    h.main(["--calls", str(tmp_path / "calls.tsv"), "--fractions", str(tmp_path / "fractions.tsv"), "--out", str(tmp_path / "hm")])
    assert (tmp_path / "hm.png").stat().st_size > 5000
