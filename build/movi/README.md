# movi (Slurm)

Build a finished, query-validated **Movi index** from a pangenome collection on the
JHU **Rockfish** cluster via Slurm. This is the Slurm counterpart to the EC2/CDK
`build/tera` stack: same TeraLCP→Movi science, but scheduled with `sbatch` instead of
provisioning a spot instance.

See [HANDOFF.md](HANDOFF.md) for the full background (goal, upstream validation,
design space). This README covers the Slurm workflow concretely.

## Pipeline

The default (and only fully turnkey) path is the **grlBWT separator path**, which is the
one proven byte-identical to stock pfp/Movi in TeraTools `test/validate_against_movi.sh`.
It produces a separator-aware index that feeds **all** Movi query modes (PML, ZML,
count, MEM, k-mer):

```
input (FASTA | list of FASTAs | AGC)
  → movi-prepare-ref … separators            (clean + %-separate, add revcomp)
  → grlbwt-cli → grlbwt2rle                   (run-length BWT)
  → grlbwt2teralcp → TeraLCP -f rlbwt -othresholds   (thresholds + heads/len)
  → grlbwt2teralcp --movi-sentinel            (heads/len with 0x00 end marker)
  → movi build --separators --preprocessed --skip-prepare --skip-pfp
  → smoke test (--pml + --count); optional full diff vs stock pfp
```

## Files

| File | Role |
|------|------|
| `submit.sh` | Driver run **on a Rockfish login node**. Parses args, picks a Slurm resource profile, and `sbatch`es the job. |
| `movi_build.slurm` | The batch job. Self-contained; all config arrives as exported env vars. Runs the pipeline, captures resources, smoke-tests, stages outputs. |

The job calls the **prebuilt binaries on shared `/home`** (no in-job compilation):
`~/git/movi-langmead/build/movi`, `~/git/TeraTools-pr/src/TeraLCP/{TeraLCP,tools/grlbwt2teralcp}`,
`~/git/grlBWT/build/{grlbwt-cli,grlbwt2rle}`, `~/bin/agc`. Override any of these with the
`MOVI` / `TERALCP` / `ADAPTER` / `GRLBWT_CLI` / `GRLBWT2RLE` / `AGC` env vars.

## Quick start

Copy the two scripts to the cluster (e.g. `~/movi-slurm/`) and from a login node:

```bash
# Single FASTA
./submit.sh --collection mycoll --fasta /path/to/ref.fa

# A list of FASTA files (one path per line; '#' comments ok)
./submit.sh --collection mycoll --list /path/to/fastas.txt

# An AGC archive: all samples, or a selected subset
./submit.sh --collection mycoll --agc /path/to/arch.agc
./submit.sh --collection mycoll --agc /path/to/arch.agc --haplotypes "HG002.1,HG002.2"
```

Watch it: `squeue --me`, then read `<OUT_BASE>/<collection>/<YYYYMMDD>/logs/summary.txt`.

### Resource profiles (`--profile`)

| Profile | Partition | Time | CPUs | Mem | Account | Use |
|---------|-----------|------|------|-----|---------|-----|
| `express` | express | 2h | 4 | 16G | blangme2 | tiny tests (QOS caps cpu=4/job) |
| `pilot` *(default)* | shared | 4h | 8 | 32G | blangme2 | small collections |
| `parallel` | parallel | 12h | 24 | (node) | blangme2 | medium, compute-bound |
| `bigmem` | bigmem | 24h | 24 | 720G | blangme2_bigmem | RAM-bound large collections |

Override any field with `--time`, `--mem`, `--cpus`, `--partition`, `--account`.

### Build options

| Flag | Default | Meaning |
|------|---------|---------|
| `--ftab-k K` | 16 | ftab k for `movi build`/query. Use ~5 for tiny test refs. |
| `--validate-full` | off | Also build a stock-pfp `--separators` index and diff `--count` (proves correctness on small inputs; expensive on large). |
| `--keep-work` | off | Keep the scratch work dir after success (debugging). |
| `--work-base DIR` | `/scratch16/blangme2/movi-build` | Scratch root (prefer scratch16). |
| `--out-base DIR` | `/data/blangme2/movi` | Durable output root. |
| `--dry-run` | — | Print the `sbatch` command and exit. |

## Output layout

```
<out-base>/<collection>/<YYYYMMDD>/
  index/                      finished Movi index (query-ready)
    index.movi
    ftab.<k>.bin
    movi.pml.nulldb  movi.zml.nulldb
  logs/
    summary.txt               wall clock, peak RSS/step, peak disk, smoke + validation
    step_times.log
    time.<step>.txt           /usr/bin/time -v per step
    smoke_count.txt  smoke_pml.log
    tool_versions.txt
    disk_usage_samples.log
```

Scratch (`<work-base>/<collection>/<date>.<jobid>/`) is removed on success unless
`--keep-work`.

## Verified

All piloted end-to-end on Slurm (express profile), `--ftab-k 5 --validate-full`, each
producing a clean index and **full validation PASS — `--count` byte-identical to a
stock-pfp `--separators` index**:

| Input mode | Fixture | Result |
|------------|---------|--------|
| `--fasta`  | `shred1_mini/minishred1_20_002.fa` (~0.4 Mbp) | smoke + validation PASS |
| `--agc` (all samples, `getcol`) | 2-sample tiny.agc | smoke + validation PASS |
| `--agc --haplotypes sampleA` (`getset`) | 2-sample tiny.agc | smoke + validation PASS |

AGC sample-name semantics confirmed: `agc listset <archive>` lists names; `--haplotypes`
takes a comma/space list of those names (a single `agc getset` call); the build fails
loudly with a `listset` hint if extraction yields an empty FASTA. The tiny AGC fixture
lives at `/scratch16/blangme2/movi-build/agc_fixture/tiny.agc` (built from the test FASTA).

Real HPRC/OpenHGL archives are available at `/data/blangme2/fasta/*/*.agc` (e.g.
`hprc-v2/human320.agc`, `openHGL/human579.agc`); a full pangenome build is RAM-bound —
use the `bigmem` profile (see HANDOFF §6).

## Not yet exercised / open items

- **ropeBWT3 (no-separator) path** is intentionally omitted: ropebwt3 isn't built on the
  cluster, and the separator path already covers every query mode.
- **S3 publish + catalog row** (HANDOFF §5 steps 5–6) are not wired in yet; the index
  currently lands on `/data`. Add an optional upload to `s3://genome-idx/movi/...` once
  AWS creds on the cluster are sorted.
- **N policy** (HANDOFF §6.5): currently inherits `movi-prepare-ref` behavior via the
  `separators` mode. Revisit the published-index convention before large runs.
