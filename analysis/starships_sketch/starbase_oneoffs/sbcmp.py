"""One-off 2026-11-11: A. fumigatus entries in Starbase v0.1.0-pre vs the 20 Starship targets (starships.fa, pangenome Table S21): names and exact sequence (md5, either strand)."""
import collections, hashlib, sqlite3
P = "/bigdata/stajichlab/jstajich/projects/MATPredict"; R = P + "/results/2026-11-11_starbase_fetch/"
c = sqlite3.connect("file:" + R + "starbase_v0.1.0-pre.sqlite?mode=ro", uri=True)
q = """select j.starshipID, n.navis_name, h.haplotype_name, f.familyName, s.sequence_length, s.md5, s.rev_comp_md5, g.ome, t.name, j.curated_status
from joined_ships j join taxonomy t on t.id=j.tax_id left join ships s on s.id=j.ship_id left join navis_names n on n.id=j.ship_navis_id
left join haplotype_names h on h.id=j.ship_haplotype_id left join family_names f on f.id=j.ship_family_id left join genomes g on g.id=j.genome_id
where t.name like 'Aspergillus fumigatus%'"""
rows = c.execute(q).fetchall()
print("Starbase A. fumigatus joined ships:", len(rows), "; with sequence:", sum(1 for r in rows if r[5]))
print("navis (family) names:", collections.Counter(r[1] for r in rows).most_common(15))
print("haplotype names:", sorted({r[2] for r in rows if r[2]})[:40])
print("curated_status:", collections.Counter(r[9] for r in rows))
with open(R + "starbase_afum.tsv", "w") as f:
    f.write("starshipID\tnavis\thaplotype\tfamily\tlength\tmd5\tgenome\ttaxon\tcurated\n")
    for r in rows: f.write("\t".join(str(x) if x is not None else "" for x in (r[0], r[1], r[2], r[3], r[4], r[5], r[7], r[8], r[9])) + "\n")
ours = {}
name = None
for ln in open(P + "/sketch_store/aspergillus_fumigatus/targets/starships.fa"):
    if ln.startswith(">"): name = ln[1:].split()[0]; ours[name] = []
    else: ours[name].append(ln.strip())
rc = str.maketrans("ACGTacgt", "TGCAtgca")
def md(s): return hashlib.md5(s.encode()).hexdigest()
sb = collections.defaultdict(list)
for r in rows:
    for m in (r[5], r[6]):
        if m: sb[m].append(r[0])
print("our target lengths:", {k: len("".join(v)) for k, v in ours.items()})
hapnames = {r[2] for r in rows if r[2]}; navnames = {r[1] for r in rows if r[1]}
for k, v in ours.items():
    s = "".join(v).upper(); fw = md(s); rv = md(s.translate(rc)[::-1])
    print(k, "| name in Starbase haplotypes:", k in hapnames or any(k.lower() == h.lower() for h in hapnames), "| navis present:", k.split("-")[0] in navnames, "| exact seq match:", sb.get(fw) or sb.get(rv) or "-")
