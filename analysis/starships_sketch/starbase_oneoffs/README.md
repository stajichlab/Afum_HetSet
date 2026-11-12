# Starbase one-off scripts (2026-11-11 / 2026-11-12)

These ran on the HPCC from `results/2026-11-11_starbase_fetch/` in MATPredict's results folder, and are kept here only so the numbers can be traced. They are not tested and hard-code HPCC paths.

| Script | Job | What it did |
|---|---|---|
| `sbcmp.py` | 32032338 | A. fumigatus entries in Starbase v0.1.0-pre (Zenodo 10.5281/zenodo.17533381) against our 20 Table S21 targets: names and exact sequence (md5). 15 of 20 match exactly. |
| `derep.py` | 32032355 | k=21 scaled-50 sketches; single-linkage clusters at max containment >= 0.9 with length ratio >= 0.5: 141 clusters, our 20 in 20 distinct clusters, 121 with none of ours. |
| `sb_targets.py`, `sb_screen.sh` | 32032728 | Targets (our 20 + one representative per uncovered cluster, `SBcNNN`) and the named screen `starbase_afum` of the 4,849-isolate store. The joint screen weakens our 20, so use it only for the 121. |
| `core_check.py` | 32035324 | Per target: containment in the Af293 and A1163 assemblies, screen prevalence, Starbase captain / curated / empty-site records. Input to `../starbase_usable.py`. |
