# CLAUDE.md: working rules for Afum_HetSet

1. **Analysis runs on the HPCC.** The laptop edits code, opens PRs and reads results. Tests run on the HPCC too.
2. **One-offs stay purgeable.** Exploration goes in a named folder (`results/<YYYY-MM-DD>_<topic>/`), temp files in `$SCRATCH`. Do not write into `/bigdata/stajichlab/shared/...` or delete there unless asked.
3. **Open a PR; the curator merges.** Never merge or push to `main` unless asked in that message. Work in a branch or worktree.
4. **Reports are archived in the repo** as markdown with PNG figures linked to PDFs and the tables beside them, so GitHub is the share mechanism.
5. **Local (Population_Genomics) isolates are counted, never named,** in anything committed. Strain-level tables that name them stay in the results folder.
6. **Metadata comes from PopSeq** (`/bigdata/stajichlab/shared/projects/Fungi/PopSeq`). Propose fixes there rather than writing a new query here.
7. Dates are absolute (`2026-11-11`). Say plainly when a result is not verified; retract a wrong claim where it was made.
8. **bafA wording:** "bafA" alone is ambiguous. Say AF293-type (cluster-linked, in the hrmA cluster) or standalone divergent, or all alleles.

Tests: `PYTHONPATH=analysis/MAT_sketch:analysis/starships_sketch python -m pytest tests -q`.
