"""One-off 2026-11-11: dereplicate the Starbase A. fumigatus ships (v0.1.0-pre) into distinct elements, with our 20 Table S21 targets added as markers.
k=21 scaled=50 sketches; pairwise max containment (smaller in larger); single-linkage clusters at several cuts, and a stricter rule that also needs length ratio >= 0.5
(so a small ship nested inside a big one is not merged). Output: counts to stdout, derep_clusters.tsv (one row per cluster) and derep_members.tsv."""
import collections, itertools, sqlite3, sys
import numpy as np
from multiprocessing import Pool
from sourmash import MinHash
P = "/bigdata/stajichlab/jstajich/projects/MATPredict"; R = P + "/results/2026-11-11_starbase_fetch/"
c = sqlite3.connect("file:" + R + "starbase_v0.1.0-pre.sqlite?mode=ro", uri=True)
rows = c.execute("""select s.id, s.header, s.sequence, s.sequence_length, max(j.curated_status='curated'), group_concat(distinct g.ome), group_concat(distinct n.navis_name), group_concat(distinct h.haplotype_name)
 from joined_ships j join taxonomy t on t.id=j.tax_id join ships s on s.id=j.ship_id left join genomes g on g.id=j.genome_id left join navis_names n on n.id=j.ship_navis_id left join haplotype_names h on h.id=j.ship_haplotype_id
 where t.name like 'Aspergillus fumigatus%' and s.sequence is not null group by s.id""").fetchall()
items = [dict(key=f"SB{r[0]}", header=r[1] or "", seq=r[2], length=len(r[2]), curated=bool(r[4]), genome=r[5] or "", navis=r[6] or "", hap=r[7] or "") for r in rows]
name = None; ours = {}
for ln in open(P + "/sketch_store/aspergillus_fumigatus/targets/starships.fa"):
    if ln.startswith(">"): name = ln[1:].split()[0]; ours[name] = []
    else: ours[name].append(ln.strip())
for k, v in ours.items(): items.append(dict(key="OURS:" + k, header=k, seq="".join(v), length=sum(map(len, v)), curated=False, genome="", navis="", hap=""))
print("Starbase A. fumigatus distinct ship ids with sequence:", len(rows), "+ ours:", len(ours))
H = []
for it in items:
    mh = MinHash(n=0, ksize=21, scaled=50); mh.add_sequence(it["seq"].upper(), force=True)
    H.append(np.array(sorted(mh.hashes), dtype=np.uint64)); it["seq"] = None
L = np.array([len(h) for h in H]); N = len(H); print("sketched", N, "hash counts min/median/max", L.min(), int(np.median(L)), L.max())
def work(i):
    out = []
    for j in range(i + 1, N):
        m = min(L[i], L[j])
        if m == 0: continue
        out.append((i, j, len(np.intersect1d(H[i], H[j], assume_unique=True)) / m))
    return out
with Pool(8) as p: res = [x for part in p.imap_unordered(work, range(N), chunksize=4) for x in part]
print("pairs", len(res))
ln = [it["length"] for it in items]
def clusters(cut, ratio=0.0):
    par = list(range(N))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for i, j, mc in res:
        if mc >= cut and min(ln[i], ln[j]) / max(ln[i], ln[j]) >= ratio: par[f(i)] = f(j)
    return [f(i) for i in range(N)]
for cut in (0.5, 0.8, 0.9, 0.95, 0.99):
    for ratio in (0.0, 0.5):
        cl = clusters(cut, ratio); sb = {cl[i] for i, it in enumerate(items) if not it["key"].startswith("OURS")}
        ours_cl = {k: cl[i] for i, it in enumerate(items) for k in [it["key"]] if k.startswith("OURS")}
        print(f"max containment >= {cut}, length ratio >= {ratio}: Starbase clusters {len(sb)}; our 20 fall in {len(set(ours_cl.values()))} clusters; clusters with none of ours {len(sb - set(ours_cl.values()))}")
cl = clusters(0.9, 0.5)
groups = collections.defaultdict(list)
for i, it in enumerate(items): groups[cl[i]].append(i)
with open(R + "derep_clusters.tsv", "w") as f, open(R + "derep_members.tsv", "w") as g:
    f.write("cluster\tn_starbase\tn_genomes\trep\trep_length\tmin_len\tmax_len\tcurated_members\tnavis\thaplotypes\tours\n"); g.write("cluster\tkey\tlength\tgenome\tcurated\tnavis\thap\theader\n")
    n = 0
    for k, mem in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        n += 1; sb = [i for i in mem if not items[i]["key"].startswith("OURS")]
        o = [items[i]["key"][5:] for i in mem if items[i]["key"].startswith("OURS")]
        rep = max(sb or mem, key=lambda i: (items[i]["curated"], items[i]["length"]))
        f.write("\t".join(map(str, [n, len(sb), len({items[i]["genome"] for i in sb}), items[rep]["key"], items[rep]["length"], min(ln[i] for i in mem), max(ln[i] for i in mem), sum(items[i]["curated"] for i in sb),
                                   ";".join(sorted({items[i]["navis"] for i in sb if items[i]["navis"]})), ";".join(sorted({items[i]["hap"] for i in sb if items[i]["hap"]})), ";".join(o)])) + "\n")
        for i in mem: g.write("\t".join(map(str, [n, items[i]["key"], ln[i], items[i]["genome"], items[i]["curated"], items[i]["navis"], items[i]["hap"], items[i]["header"][:80]])) + "\n")
sizes = sorted((len([i for i in m if not items[i]["key"].startswith("OURS")]) for m in groups.values()), reverse=True)
print("chosen rule: containment>=0.9 and length ratio>=0.5 ->", len(groups), "clusters;", "clusters with >=1 Starbase member:", sum(1 for s in sizes if s), "; singletons:", sum(1 for s in sizes if s == 1), "; largest sizes:", sizes[:10])
print("length quartiles of cluster representatives:", np.percentile([int(l.split("\t")[4]) for l in open(R + "derep_clusters.tsv").read().splitlines()[1:]], [0, 25, 50, 75, 100]).tolist())
