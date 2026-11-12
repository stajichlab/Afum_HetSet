"""One-off 2026-11-11: screen targets from the Starbase A. fumigatus dereplication: our 20 Table S21 targets plus one representative per cluster that has none of ours (121).
Representative = the curated, then longest, member chosen in derep_clusters.tsv. Writes starbase_targets.fa and starbase_targets.tsv (target, cluster, source, length, curated, navis, haplotype, genome)."""
import csv, sqlite3
P = "/bigdata/stajichlab/jstajich/projects/MATPredict"; R = P + "/results/2026-11-11_starbase_fetch/"
c = sqlite3.connect("file:" + R + "starbase_v0.1.0-pre.sqlite?mode=ro", uri=True)
cl = list(csv.DictReader(open(R + "derep_clusters.tsv"), delimiter="\t"))
new = [r for r in cl if not r["ours"]]
print("clusters:", len(cl), "without ours:", len(new))
out = open(R + "starbase_targets.fa", "w"); tsv = open(R + "starbase_targets.tsv", "w")
tsv.write("target\tcluster\tsource\tlength\tn_cluster_members\tcurated_in_cluster\tnavis\thaplotypes\n")
n = 0
for ln in open(P + "/sketch_store/aspergillus_fumigatus/targets/starships.fa"):
    out.write(ln)
    if ln.startswith(">"): tsv.write(f"{ln[1:].split()[0]}\t\ttable_S21\t\t\t\t\t\n"); n += 1
for r in new:
    sid = int(r["rep"][2:]); seq, hdr = c.execute("select sequence, header from ships where id=?", (sid,)).fetchone()
    name = f"SBc{int(r['cluster']):03d}"
    out.write(f">{name}\n"); out.write("\n".join(seq[i:i + 80] for i in range(0, len(seq), 80)) + "\n")
    tsv.write(f"{name}\t{r['cluster']}\tstarbase:{r['rep']}\t{len(seq)}\t{r['n_starbase']}\t{r['curated_members']}\t{r['navis']}\t{r['haplotypes']}\n"); n += 1
print("targets written:", n)
