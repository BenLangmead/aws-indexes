# OpenHGL Movi index — run recipe

**Dataset:** `lh3/OpenHGL` = `human579.agc` — 579 high-quality de novo human assemblies
(~1.7 Tbp raw; CHM13 + HPRC(464) + Chinese/Korean/Saudi/Indian/UAE-Arab references).
With %-separators + reverse complement the Movi BWT length n ≈ 3.4 Tbp (~20% > hprc-yr2).

**Source (already on Rockfish):** `/data/blangme2/fasta/openHGL/human579.agc`
(3.68 GB, 579 sets, md5 `617ff48ee2e51d0216192f577ab3f465`). A ropeBWT3 `.fmd` + a prior
NON-separator TeraLCP index also exist at `/vast/blangme2/langmead/OpenHGL/` (benchmark
artifacts — not reusable for the separator-aware Movi index).

**Config:** `config.openhgl.yaml` — mirrors `config.yr2.yaml` but `teralcp:` points at the
**parallel** build `/home/blangme2/git/TeraTools-ssp/src/TeraLCP/TeraLCP` (single-seq-parallel).
This is essential: the separator path feeds TeraLCP one giant %-separated sequence
(numSequences==1), which the OLD binary walks single-threaded; the ssp binary parallelizes it.

**Not in the catalog** — this is a genuinely new build (no OpenHGL/human579 Movi index or
rlbwt exists in movi-index-catalog).

## Prereqs verified (2026-07-04)
- All tool paths exist; agc present; VAST has 128 TB free.
- `snakemake -n` dry run: clean 17-job DAG
  (extract→prepare→concat→grlbwt→rle→adapter_{teralcp,movi}→construct_A/B/C→thresholds
   →stage_{thresholds,ref}→movi_build→ftab×5, plus seqdict).
- Prepared in isolated dir `~/movi-slurm/snakemake-openhgl-prep/` (Snakefile + config +
  scripts/seqdict_build.py) so the live yr2 run was untouched.

## When to launch
**After the hprc-yr2 construct finishes** (frees the 16 cores on devlangmead1). OpenHGL uses
separate workdir (`/vast/blangme2/movi-work/openhgl`) and outdir (`/data/blangme2/movi/openhgl`),
so there is no path collision with yr2 — the only reason to wait is CPU/RAM contention
(two concurrent grlBWTs would need ~800 GB combined; feasible on the 1.5 TB node but risky
to the in-flight yr2 run).

## Launch (devlangmead1 local, mirrors yr2)
```bash
cd ~/movi-slurm/snakemake-openhgl-prep      # this dir is a valid run dir (Snakefile+config+scripts)
source ~/miniforge3/etc/profile.d/conda.sh && conda activate snakemake8
snakemake --unlock --configfile config.openhgl.yaml
OMP_NUM_THREADS=16 nohup snakemake --cores 16 --configfile config.openhgl.yaml \
    --config teralcp_p=16 --rerun-incomplete --printshellcmds --latency-wait 90 \
    >> run.openhgl.devlangmead.log 2>&1 </dev/null & disown
```
Then babysit exactly like yr2: grlbwt (~days) → construct A/B/C (parallel now) → thresholds
→ movi_build → ftab. On success, register `openhgl_m6_sep_<date>` (owned) + the rlbwt/seqdict
precursors via /movi-index, and upload to genome-idx.

## Alt (Slurm, if devlangmead1 is unavailable)
`snakemake --executor slurm --workflow-profile profiles/rockfish --configfile config.openhgl.yaml`
(needs `profiles/rockfish/` copied into the run dir; per-phase bigmem+extended 7-day jobs).
