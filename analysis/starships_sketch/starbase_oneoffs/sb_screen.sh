#!/bin/bash
#SBATCH -J starbase-screen -p stajichlab -A stajichlab -c 16 --mem 64G -t 4:00:00
#SBATCH -o /bigdata/stajichlab/jstajich/projects/MATPredict/results/2026-11-11_starbase_fetch/screen.%j.log
# 2026-11-11: new named screen of the 4,849-isolate store with 141 targets (our 20 + 121 Starbase representatives). Existing store outputs untouched.
set -euo pipefail
P=/bigdata/stajichlab/jstajich/projects/MATPredict; S=$P/sketch_store/aspergillus_fumigatus; R=$P/results/2026-11-11_starbase_fetch
PY=/opt/linux/rocky/8.x/x86_64/pkgs/sourmash_branchwater/0.9.13/bin/python
cd $R && $PY sb_targets.py
$PY $S/bin/sketch_query.py --store $S --threads 16 screen --name starbase_afum --targets $R/starbase_targets.fa --truth $S/targets/truth_store.tsv --truth-id sample_id
ls -l $S/query/screen_starbase_afum | head
head -30 $S/query/screen_starbase_afum/summary.txt | cut -c1-200
