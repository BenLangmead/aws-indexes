# Movi-index build — Snakemake + Slurm (Rockfish)

Formalizes the **AGC → grlBWT → TeraLCP → Movi** pipeline as a Snakemake workflow that
runs each stage as a right-sized Slurm job on JHU Rockfish. Default target: a finished,
separator-aware Movi index of **HPRC release 1** (`HPRC-yr1.agc`, 95 haplotypes).

This is the multi-day, full-scale counterpart to the single-node `build/movi` Slurm
scripts and the `build/movi/membench_devlangmead.sh` profiler.

## Pipeline / DAG

```
extract (agc getcol/getset)        -> input.fa
prepare (movi-prepare-ref …separators) -> clean.fa            (adds %-separators + revcomp)
concat  (grep|tr)                  -> grl_in.txt
grlbwt  (grlbwt-cli -T scratch)    -> grl_out.rl_bwt
rle     (grlbwt2rle)               -> grl_rle.{syms,len}
  ├ adapter_teralcp (grlbwt2teralcp)            -> grl.bwt.{heads,len}   (for TeraLCP -f rlbwt)
  └ adapter_movi    (grlbwt2teralcp --movi-sentinel) -> index/ref.fa.bwt.{heads,len}
teralcp_construct_A/B/C (TeraLCP -f rlbwt -checkpoint [-stop-after A|B] / -oindex) -> teralcp.lcp_index [bigmem+extended]
teralcp_thresholds (TeraLCP -f lcp_index -othresholds --rlbwt-meta) -> septera.thr,.thr_pos  [bigmem]
stage_ref/stage_thresholds         -> index/ref.fa, index/ref.fa.thr,.thr_pos
movi_build (movi build --separators --preprocessed …) -> index/index.movi
```

## The TeraLCP per-phase split (why it exists)

Full HPRC-yr1 TeraLCP construct is ~4–5 days; HPRCv2 (~4.9×) is projected at 2–3 weeks,
which exceeds the **7-day** Rockfish walltime cap. So construct is split into per-phase
jobs (`teralcp_construct_A` → `B` → `C`) that share one checkpoint dir and each resume
from the first incomplete phase, so the total can run across successive ≤7-day jobs. The
threshold phase is separately RAM-heavy. We use the **`bigmem`** partition for all legs,
with different QOS to get the walltime each needs:

| partition | RAM/node | walltime | QOS we use |
|---|---|---|---|
| `parallel` | 192 GB | 3 d | `normal` |
| `bigmem` | **1536 GB** | 2 d default / **7 d** under `extended` | `extended` (construct), `qos_bigmem` (thresholds) |

> **NB: the `emr` partition (512 GB / 7 d) is NOT available to us.** It is a condo
> (`AllowQos=emr,emr_condo,emr_tzaki`) and `blangme2` holds none of those QOS — a job
> submitted there sits PENDING forever (*"QOS not permitted to use this partition"*).
> `sbatch --test-only` does **not** catch this, so verify QOS access via
> `sacctmgr show assoc user=$USER`, not a test submission.

So we checkpoint internally and split:
- **`teralcp_construct_A/B/C` → `bigmem` + `qos=extended`**: each builds one slow phase of
  the LCP index, sharing a `teralcp.ckpt` dir; `C` writes `teralcp.lcp_index`. `extended`
  raises the bigmem walltime cap to **7 days** *per phase*, so a >7-day total completes
  across jobs. The 1536 GB node leaves headroom over the ~450–520 GB construction peak.
  Each job re-passes `-f rlbwt -i grl` (the constructor rebuilds + frees the FMD even on
  resume), so all three depend on the grlBWT `heads/len`; `A`/`B` add `-stop-after A|B`.
  > **Caveat:** checkpoints are only at phase *boundaries* — a single phase exceeding 7
  > days cannot yet be chunked (would need the finer two-traversal split inside phase A).
  > Watch `construct_A` at full HPRCv2 scale. The `teralcp.ckpt` dir (100s of GB) may be
  > deleted once `teralcp.lcp_index` exists.
- **`teralcp_thresholds` → `bigmem` + `qos=qos_bigmem`**: resumes from the index and emits
  thresholds in a few hours; the threshold phase is the RAM high-water (fits the 1.5 TB
  node within the 2-day cap). Run metadata is read from the grlBWT `heads/len` via
  **`TeraLCP --rlbwt-meta`** (a small addition so the rlbwt/separator path can resume
  without an FMD). The split is verified **byte-identical** to a one-shot `-othresholds` run.

Because mem on `bigmem` is tied to CPUs at 32 GB/CPU (4 GB/CPU on `parallel`), the cpu
counts in `config.yaml` are sized to *unlock the requested memory*, not because the tools
need them (TeraLCP is effectively serial — see the parallelism analysis in the project
notes). QOS is passed via the Snakemake slurm plugin's first-class `qos` resource (the
plugin forbids `--qos` inside `slurm_extra`).

## Prerequisites

- Conda env `snakemake8` with `snakemake>=8` + `snakemake-executor-plugin-slurm`
  (created at `~/miniforge3/envs/snakemake8`).
- Prebuilt tools on shared `/home` (see paths in `config.yaml`). **TeraLCP must be the
  build carrying the `--rlbwt-meta` flag** (and the Tier A+B threshold-memory work).
- Scratch on `/scratch16` (workdir) — grlBWT needs ~1.2 TB temp and the lcp_index/grl_in
  are large; `/scratch16` has ample headroom.

## Run

From a login node, in `tmux`/`screen` (or `nohup`) since the Snakemake scheduler must
stay alive for the whole build:

```bash
cd ~/movi-slurm/snakemake          # (this directory, deployed to the cluster)
./run.sh -n                        # dry run: print the plan
nohup ./run.sh > run.log 2>&1 &    # real run: submits Slurm jobs and monitors
```

Monitor: `squeue --me`, `tail -f run.log`, and `.snakemake/log/`. The Rockfish dashboard
shows the Slurm jobs.

## Resume / re-entrancy

Snakemake is re-entrant: rerunning `./run.sh` continues from the last completed output, so
a preempted/failed late stage (e.g. `teralcp_thresholds`) reruns *without* repeating the
~5-day construction. The `.lcp_index` is the durable checkpoint between the two TeraLCP jobs.

## Config knobs (`config.yaml`)

- `collection`, `agc_archive`, `haplotypes` (`ALL` or a sample-name list), `ftab_k`.
- `workdir` (scratch), `outdir` (durable index location).
- `res.<rule>`: partition/account/mem_mb/runtime/cpus per stage. `teralcp_p` sets the
  thread count passed to TeraLCP `-p` (independent of the cpus requested for memory).

## Known risks / things the first run tests

- **`teralcp_construct_*` memory.** The ~450–520 GB estimate is extrapolated from the 24-hap
  pilot with wide error bars. Running on `bigmem` (1536 GB) under `qos=extended` gives ample
  headroom, so this is **no longer an OOM/EC2 risk** (it was, back when the plan targeted the
  512 GB `emr` partition — which turned out to be inaccessible to us anyway). Still worth
  watching `sstat MaxRSS` on the first full run to pin down the real peak.
- **A single construct phase exceeding 7 days.** The per-phase split only checkpoints at
  phase *boundaries*. If one phase (e.g. `construct_A`, endmarker repair) alone exceeds the
  7-day cap at HPRCv2 scale, that job is killed with no intra-phase checkpoint and reruns
  from the phase start. The fix would be a finer split (the two endmarker-repair traversals);
  watch `construct_A`'s wall time on the first HPRCv2 run.
- **`movi_build` memory at this scale is not yet benchmarked** — 190 GB is a guess; bump
  the `movi_build` resources (or move it to `bigmem`) if it OOMs.
- Runtimes in `config.yaml` are estimates; they're set comfortably under each partition's
  walltime cap, but watch the first `teralcp_construct_*`.
