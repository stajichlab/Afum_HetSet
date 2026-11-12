# Afum_HetSet

Profiling of *Aspergillus fumigatus* isolates from read sketches: mating-type frequency and accessory elements (Starships, the baf gene family including bafA).

Layout:

- `analysis/MAT_sketch/`: MAT idiomorph frequency from read data (per isolate and per clone group, by study, country and lineage) and the population report.
- `analysis/starships_sketch/`: Starship and bafA screens on the same sketch store: presence/absence, gain/loss on the tree, the baf family, per-strain tables, and the archived reports.

Both read a sketch store built on the UCR HPCC (4,849 isolates). The store builder, planner and query tools live in [MATPredict](https://github.com/stajichlab/MATPredict) (`datasets/reads/sketch_store/`); this repository holds the analysis on top of the store. Run on the HPCC; the laptop only edits code and opens pull requests.

See `CLAUDE.md` for working rules.
