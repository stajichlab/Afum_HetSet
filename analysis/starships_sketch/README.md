# Starships and the baf family from read sketches

Copied from MATPredict `datasets/reads/sketch_store/` (MATPredict `main` `f7531b8` plus PR #333 commits `8d2224f` and `712232b`). The sketch store itself, its planner and query tools stay in MATPredict.

| File | What it does |
|---|---|
| `starship_dynamics.py` | Clone-by-element matrix, prevalence (Wilson), Fitch parsimony gain/loss on the tree, co-occurrence, threshold sweep against a truth set. `--set Osiris-h3=0.7` raises a present cut. |
| `starship_candidates.py` | Tiered strain list (strong / probable / discordant) for bafA with Nebuchadnezzar-h1 and the wide call table. Names local isolates, so its output stays in the results folder. |
| `baf_family.py` | `targets`: one target per baf gene from assembly haplotypes; `summarize`: screen against the strain gene counts and the population, with the cluster-linked / standalone divergent bafA classes. |
| `strain_starship_table.py` | Per-strain table for a name prefix (for example eAF) with every Starship call and the bafA class. |
| `strain_starship_heatmap.py` | Heatmap (PNG + PDF) of that table: strains down, bafA and the Starships across, tint = hash fraction, solid = present, dashed = partial; `reports/starship/eAF/heatmap.png` is the eAF example. |
| `starbase_usable.py` | Picks the Starbase targets worth profiling from `starbase_oneoffs/core_check.tsv` (drops unscreenable, absent and core-like ones; flags widespread uncertain ones). Output in `reports/starship/starbase/`. |
| `starship_report_data.py`, `starship_report_md.py` | Report data and the markdown archive with PNG + PDF figures. |
| `reports/starship/` | The archived report (`report.md`, `figures/`, `tables/`) and the `eAF/` table. `reports/starship_report.html` is the page template. |

bafA means three things here: AF293-type (cluster-linked, in the hrmA cluster, 2 usable hashes), standalone divergent (found only by the all-alleles screen, outside the hrmA cluster), or all alleles.

Starbase (v0.1.0-pre, Zenodo 10.5281/zenodo.17533381): 15 of our 20 Table S21 targets match a Starbase sequence exactly; the 944 distinct A. fumigatus ships fall in 141 clusters, 121 with none of ours. The 77 usable representatives (`SBcNNN`, 6 flagged uncertain) are added as columns in `reports/starship/eAF_starbase/` (`--extra-screen` / `--extra-targets` of `strain_starship_table.py`). These calls have no truth set and are unvalidated; the joint 141-target screen weakens our 20, so their calls come from the earlier 21-target screen. The one-off scripts are in `starbase_oneoffs/`.
