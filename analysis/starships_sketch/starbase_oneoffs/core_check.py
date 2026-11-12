"""One-off 2026-11-12: is each Starbase representative (SBcNNN) a mobile element or core sequence? Per target: containment of its k=21 sketch (scaled 20) in the Af293 and A1163 reference genomes,
screen prevalence and specific hashes (screen_starbase_afum), and Starbase metadata for the whole cluster (members with a captain gene, curated, empty-site and boundary records, quality tags)."""
import collections, csv, re, sqlite3
import numpy as np
from sourmash import MinHash
P = "/bigdata/stajichlab/jstajich/projects/MATPredict"; R = P + "/results/2026-11-11_starbase_fetch/"
B = "/bigdata/stajichlab/shared/projects/A_fumigatus/baf/"
def sketch(seq):
    mh = MinHash(n=0, ksize=21, scaled=20); mh.add_sequence(seq.upper(), force=True); return set(mh.hashes)
def fasta_hashes(path):
    mh = MinHash(n=0, ksize=21, scaled=20); buf = []
    def flush():
        if buf: mh.add_sequence("".join(buf).upper(), force=True); buf.clear()
    for ln in open(path):
        if ln.startswith(">"): flush()
        else: buf.append(ln.strip())
    flush(); return set(mh.hashes)
ref = {"Af293": fasta_hashes(B + "genomes/Af293.scaffolds.fasta"), "A1163": fasta_hashes(B + "genomes/A1163.scaffolds.fasta")}
print("reference hashes:", {k: len(v) for k, v in ref.items()})
summ = {}
for ln in open(P + "/sketch_store/aspergillus_fumigatus/query/screen_starbase_afum/summary.txt"):
    m = re.match(r"(SBc\d+)\s+len\s+(\d+)\s+specific hashes\s+(\d+)\s+present\s+(\d+)\s+partial\s+(\d+)", ln)
    if m: summ[m.group(1)] = tuple(int(x) for x in m.groups()[1:])
db = sqlite3.connect("file:" + R + "starbase_v0.1.0-pre.sqlite?mode=ro", uri=True)
cl = {r["cluster"]: r for r in csv.DictReader(open(R + "derep_clusters.tsv"), delimiter="\t")}
mem = collections.defaultdict(list)
for r in csv.DictReader(open(R + "derep_members.tsv"), delimiter="\t"):
    if r["key"].startswith("SB"): mem[r["cluster"]].append(int(r["key"][2:]))
tg = {r["target"]: r for r in csv.DictReader(open(R + "starbase_targets.tsv"), delimiter="\t") if r["target"].startswith("SBc")}
out = open(R + "core_check.tsv", "w")
cols = ["target", "cluster", "length", "specific_hashes", "present_isolates", "partial_isolates", "cont_Af293", "cont_A1163", "members", "members_with_captain", "members_curated", "members_with_empty_site", "members_with_boundary", "tag_types"]
out.write("\t".join(cols) + "\n")
for t, r in sorted(tg.items()):
    c = r["cluster"]; sid = int(cl[c]["rep"][2:])
    seq = db.execute("select sequence from ships where id=?", (sid,)).fetchone()[0]; h = sketch(seq)
    ids = mem[c]; q = ",".join("?" * len(ids))
    cap = db.execute(f"select count(distinct j.ship_id) from joined_ships j where j.ship_id in ({q}) and j.captain_id is not null", ids).fetchone()[0]
    cur = db.execute(f"select count(distinct ship_id) from joined_ships where ship_id in ({q}) and curated_status='curated'", ids).fetchone()[0]
    emp = db.execute(f"select count(distinct ship_id) from starship_features where ship_id in ({q}) and emptySiteID is not null and emptySiteID!=''", ids).fetchone()[0]
    bnd = db.execute(f"select count(distinct ship_id) from starship_features where ship_id in ({q}) and boundaryType is not null and boundaryType!=''", ids).fetchone()[0]
    tags = ";".join(f"{a}:{b}" for a, b in db.execute(f"select tag_type, count(*) from ship_quality_tags where joined_ship_id in (select id from joined_ships where ship_id in ({q})) group by tag_type order by 2 desc limit 4", ids))
    s = summ.get(t, (0, 0, 0, 0))
    out.write("\t".join(map(str, [t, c, s[0], s[1], s[2], s[3], round(len(h & ref["Af293"]) / len(h), 3), round(len(h & ref["A1163"]) / len(h), 3), len(ids), cap, cur, emp, bnd, tags])) + "\n")
out.close()
rows = list(csv.DictReader(open(R + "core_check.tsv"), delimiter="\t"))
use = [r for r in rows if int(r["specific_hashes"]) >= 10]
def bins(r): p = int(r["present_isolates"]); return "0" if p == 0 else "1-49" if p < 50 else "50-499" if p < 500 else "500-2000" if p <= 2000 else ">2000"
print("targets with >=10 specific hashes:", len(use))
for b in ("0", "1-49", "50-499", "500-2000", ">2000"):
    g = [r for r in use if bins(r) == b]
    if not g: continue
    print(f"prevalence {b:9s} n={len(g):3d} | median containment Af293 {np.median([float(r['cont_Af293']) for r in g]):.2f} (>=0.9: {sum(float(r['cont_Af293'])>=0.9 for r in g)}) A1163 {np.median([float(r['cont_A1163']) for r in g]):.2f} | clusters with a captain-bearing member: {sum(int(r['members_with_captain'])>0 for r in g)} | with a curated member: {sum(int(r['members_curated'])>0 for r in g)} | with empty-site record: {sum(int(r['members_with_empty_site'])>0 for r in g)}")
print("the 13 most prevalent:")
for r in sorted(use, key=lambda r: -int(r["present_isolates"]))[:13]:
    print(r["target"], "len", r["length"], "present", r["present_isolates"], "Af293", r["cont_Af293"], "A1163", r["cont_A1163"], "members", r["members"], "captain", r["members_with_captain"], "curated", r["members_curated"], "empty", r["members_with_empty_site"])
