# Starships and the baf family from read sketches

Copied from MATPredict `datasets/reads/sketch_store/` (MATPredict `main` `f7531b8` plus PR #333 commits `8d2224f` and `712232b`). The sketch store itself, its planner and query tools stay in MATPredict.

| File | What it does |
|---|---|
| `starship_dynamics.py` | Clone-by-element matrix, prevalence (Wilson), Fitch parsimony gain/loss on the tree, co-occurrence, threshold sweep against a truth set. `--set Osiris-h3=0.7` raises a present cut. |
| `starship_candidates.py` | Tiered strain list (strong / probable / discordant) for bafA with Nebuchadnezzar-h1 and the wide call table. Names local isolates, so its output stays in the results folder. |
| `baf_family.py` | `targets`: one target per baf gene from assembly haplotypes; `summarize`: screen against the strain gene counts and the population, with the cluster-linked / standalone divergent bafA classes. |
| `strain_starship_table.py` | Per-strain table for a name prefix (for example eAF) with every Starship call and the bafA class. |
| `strain_starship_heatmap.py` | Heatmap (PNG + PDF) of that table: strains down, bafA and the Starships across, tint = hash fraction, solid = present, dashed = partial; `reports/starship/eAF/heatmap.png` is the eAF example. |
| `starship_report_data.py`, `starship_report_md.py` | Report data and the markdown archive with PNG + PDF figures. |
| `reports/starship/` | The archived report (`report.md`, `figures/`, `tables/`) and the `eAF/` table. `reports/starship_report.html` is the page template. |

bafA means three things here: AF293-type (cluster-linked, in the hrmA cluster, 2 usable hashes), standalone divergent (found only by the all-alleles screen, outside the hrmA cluster), or all alleles.

Open: Starbase / Gluck-Thaler Starships are not screened, and whether the 20 targets (pangenome Table S21) equal them is not checked.
