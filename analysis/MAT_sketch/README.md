# MAT frequency from read sketches

Copied from MATPredict `datasets/reads/sketch_store/` (`main` `f7531b8`).

- `mat_frequency.py`: MAT1-1 fraction per sample and per clone group (one vote per clone group at ANI 0.9995), overall and by study, country, source and lineage, with Wilson intervals and an exact binomial test. Also provides `rd` and `wilson`, which `analysis/starships_sketch/starship_dynamics.py` imports.
- `export_report.py`: writes `population.json` and `runs_public.tsv` for a species; local isolates are counted, never named.
- `reports/aspergillus_fumigatus/`: the committed A. fumigatus population report data (4,849 isolates).
