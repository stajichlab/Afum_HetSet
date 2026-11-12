#!/usr/bin/env python3
"""Heatmap of a strain-by-Starship table (the calls.tsv and fractions.tsv written by strain_starship_table.py).

Rows are isolates (sorted by lineage, clone group, name), columns are bafA (AF293-type, then the all-alleles class) and the Starship haplotypes grouped by family.
Cell tint is the fraction of the element's specific hashes found; the number is printed for calls of present (solid) and partial (dashed outline). Bars above
the columns count the isolates carrying each element. Writes OUT.png and OUT.pdf.

    strain_starship_heatmap.py --calls eAF/calls.tsv --fractions eAF/fractions.tsv --title "eAF strains (PRJNA991533)" --out eAF/heatmap
"""
import argparse
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

META = ("strain", "sample_id", "clone", "lineage", "n_present", "present_elements", "bafA_all_hits", "bafA_class")
CMAP = LinearSegmentedColormap.from_list("hash", ["#e8f1f2", "#0b5a63"])
KCOL = {"cluster_linked": "#3d3fa8", "standalone_divergent": "#c9831f"}
KTXT = {"cluster_linked": "cluster", "standalone_divergent": "standalone"}


def num(v):
    return int(v) if str(v).isdigit() else 10 ** 9


def load(calls, fractions):
    fr = {r["sample_id"]: r for r in csv.DictReader(open(fractions), delimiter="\t")}
    rows = list(csv.DictReader(open(calls), delimiter="\t"))
    els = [c for c in rows[0] if c not in META and c != "bafA"]
    rows.sort(key=lambda r: (num(r["lineage"]), num(r["clone"]), r["strain"]))
    return rows, fr, ["bafA"] + els, els


def draw(rows, fr, cols, title, out):
    n, m = len(rows), len(cols)
    fig = plt.figure(figsize=(max(9, 0.34 * m + 4.2), max(5, 0.16 * n + 3.6)))
    gs = fig.add_gridspec(2, 3, width_ratios=[2.6, 1.0, m * 0.34], height_ratios=[1.3, n * 0.16], wspace=0.02, hspace=0.02,
                          left=0.02, right=0.99, top=0.945, bottom=0.075)
    ax = fig.add_subplot(gs[1, 2]); axb = fig.add_subplot(gs[0, 2], sharex=ax); axk = fig.add_subplot(gs[1, 1], sharey=ax); axt = fig.add_subplot(gs[1, 0], sharey=ax)
    fig.add_subplot(gs[0, 0]).axis("off"); fig.add_subplot(gs[0, 1]).axis("off")
    ax.set_xlim(-0.5, m - 0.5); ax.set_ylim(n - 0.5, -0.5)
    fams = [c.split("-")[0] for c in cols[1:]]
    xcol = list(range(m))
    counts = [0] * m
    for i, r in enumerate(rows):
        f = fr[r["sample_id"]]
        for j, c in enumerate(cols):
            call = r[c]
            if call not in ("P", "p"):
                continue
            v = float(f[c]); counts[j] += call == "P"
            ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=CMAP(v), edgecolor="white", linewidth=0.4))
            if call == "p":
                ax.add_patch(Rectangle((j - 0.4, i - 0.4), 0.8, 0.8, fill=False, edgecolor="#0b5a63", linewidth=0.8, linestyle=(0, (2, 1.5))))
            ax.text(j, i, f"{v:.2f}".lstrip("0"), ha="center", va="center", fontsize=4.6, color="white" if v > 0.55 and call == "P" else "#14211f",
                    style="italic" if call == "p" else "normal")
    prev = None
    for i, r in enumerate(rows):
        key = r["clone"] or "s" + r["sample_id"]
        if prev is not None and key != prev:
            for a in (ax, axk, axt):
                a.axhline(i - 0.5, color="#9fb3b0", linewidth=0.5)
        prev = key
    cut = [j for j in range(2, m) if fams[j - 1] != fams[j - 2]]
    for j in [1] + cut:
        ax.axvline(j - 0.5, color="#50625f", linewidth=0.8); axb.axvline(j - 0.5, color="#50625f", linewidth=0.8)
    ax.set_xticks(xcol); ax.set_xticklabels(["bafA AF293"] + cols[1:], rotation=90, fontsize=6.5); ax.set_yticks([])
    ax.tick_params(length=0)
    axb.bar(xcol, counts, color="#0b5a63", width=0.7); axb.set_ylim(0, max(max(counts), 1) * 1.25); axb.tick_params(axis="x", labelbottom=False, length=0)
    axb.set_ylabel("isolates present", fontsize=6.5); axb.tick_params(axis="y", labelsize=6)
    for s in ("top", "right"):
        axb.spines[s].set_visible(False)
    for j, c in enumerate(counts):
        axb.text(j, c + max(counts) * 0.03, str(c), ha="center", va="bottom", fontsize=5.2)
    axk.set_xlim(0, 1); axk.axis("off")
    for i, r in enumerate(rows):
        k = r["bafA_class"]
        if k in KCOL:
            axk.add_patch(Rectangle((0.02, i - 0.45), 0.96, 0.9, facecolor=KCOL[k], edgecolor="none"))
            axk.text(0.5, i, f"{KTXT[k]} {r['bafA_all_hits']}", ha="center", va="center", fontsize=4.8, color="white")
    axk.set_title("bafA\nall alleles", fontsize=6.5)
    axt.set_xlim(0, 1); axt.axis("off")
    for i, r in enumerate(rows):
        axt.text(0.0, i, r["strain"], ha="left", va="center", fontsize=5.4, fontweight="bold")
        axt.text(0.50, i, r["lineage"], ha="center", va="center", fontsize=5, color="#50625f")
        axt.text(0.68, i, r["clone"], ha="center", va="center", fontsize=5, color="#50625f")
        axt.text(0.92, i, r["n_present"], ha="center", va="center", fontsize=5.4, fontweight="bold")
    for x, t in ((0.0, "strain"), (0.50, "lineage"), (0.68, "clone"), (0.92, "n")):
        axt.text(x, -1.3, t, ha="left" if x == 0 else "center", va="bottom", fontsize=6.2, color="#50625f")
    for fam in dict.fromkeys(fams):
        idx = [j + 1 for j, f in enumerate(fams) if f == fam]
        axb.text(sum(idx) / len(idx), axb.get_ylim()[1] * 1.0, fam, ha="center", va="bottom", fontsize=6.5, color="#50625f", clip_on=False)
    axb.text(0, axb.get_ylim()[1], "bafA", ha="center", va="bottom", fontsize=6.5, color="#50625f", clip_on=False)
    fig.suptitle(title, x=0.02, ha="left", fontsize=11, fontweight="bold")
    fig.text(0.02, 0.006, "Tint = fraction of specific hashes found. Solid = present; dashed, italic = partial (upper bound).", fontsize=6, color="#50625f", ha="left")
    fig.savefig(out + ".png", dpi=200); fig.savefig(out + ".pdf"); plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--calls", required=True); ap.add_argument("--fractions", required=True); ap.add_argument("--title", default="Starship screen"); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows, fr, cols, _ = load(a.calls, a.fractions)
    draw(rows, fr, cols, a.title, a.out)
    print(f"{len(rows)} isolates x {len(cols)} elements -> {a.out}.png, {a.out}.pdf")


if __name__ == "__main__":
    main()
