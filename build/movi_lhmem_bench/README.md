# movi_mem_bench

CDK stack that provisions a **bare-metal `c5.metal` spot instance** and runs
**granular hardware-PMU profiling of the Movi MEM query** — the per-source-line
attribution we cannot get on the Rockfish dev node (its `perf_event_paranoid=2`
blocks event-based sampling).

Sibling of `build/movi_kmer_bench/` (same conventions, same reused instance role);
this one targets `--mem` instead of `--kmer`.

## Why this stack exists

The redesigned MEM coroutine (`query_mem_coroutine`, branch `coroutine`, HEAD
`e8d4dea`) is **correct** (gate 7899/7899) but **~15% slower than production at
all widths**, with a **flat width curve**. The standing hypothesis is that MEM is
**compute/scan-bound** — the O(#runs) skip-count and rc-interval scans inside
`extend_bidirectional` dominate, so there's almost no LF-jump latency to hide. But
that was only inferred from *wall-clock* on Rockfish; it has never been confirmed
with hardware counters, and we have no per-line attribution telling us *where* the
MEM time actually goes. This stack settles it.

## Why c5.metal

- **Bare metal → full PMU/PEBS.** Virtualized Nitro instances hide event-based
  sampling, so per-line `perf`/VTune attribution needs metal.
- **Cascade Lake (Xeon Platinum 8275CL)** — same microarchitecture as the
  Rockfish Xeon Gold 6248R we profiled, so `mem_load_retired`, `cycle_activity`
  and TMA behave identically and numbers are comparable.
- **192 GB RAM** holds the full 37 GB index; ~$4.08/hr on-demand. We bid
  **spot at $2.10 (~½ on-demand)** so price-based interruption is very unlikely.

## What it measures

Workload: **~2000 reads (`mem2k`), `--min-mem-length 25`**, pinned to one core on
NUMA node 0. Two axes:

- **path:** production **sequential** MEM (`movi-regular-thresholds query --mem`,
  the real optimization target) vs the **coroutine** (`movi-co --mem`) at
  width `W ∈ {1, 8}`.
- **ftab depth:** `--ftab-k ∈ {10, 12}` (deeper ftab → fewer extension steps/MEM).

Per case:

- `perf stat` — IPC, L3-miss loads, DRAM-stall cycles, MLP
  (`offcore_requests_outstanding`).
- `likwid-perfctr` — `TMA`, `CYCLE_STALLS`, `MEM` (DRAM bandwidth; uncore, since
  we're root at `paranoid=-1`).

At the two most informative cases per ftab regime (`prod_seq` + `co_w8`):

- `perf record -e mem_load_retired.l3_miss:pp` → **per-source-line DRAM-miss**
  histogram (`*.l3miss.byline.txt`) — *where the misses are*.
- `perf record -e cycles` → **per-source-line cycles** histogram
  (`*.cycles.byline.txt`) — *where the time goes*. **This is the key MEM signal**:
  for a compute/scan-bound query, where time is spent (e.g.
  `MoveInterval::count`, the skip-count loop, the rc-walk in
  `move_structure_search.cpp` vs `LF_move`) matters more than where misses land.

A 1-read `one453` run per binary/regime bounds the index-load contribution for
differencing.

Results are tarred to `s3://genome-idx/movi/mem_bench/results/` (see the
`ResultsLocation` output), with a `SENTINEL_DONE` marker when finished.

## Authentication model — no permanent credentials (same as `build/bowtie`)

- **Instance → S3 downloads:** the `genome-idx` inputs are public-read, so the
  instance fetches them with `aws s3 cp --no-sign-request` — no credentials.
- **Instance → results upload:** the instance role is allowed to
  `sts:AssumeRole` the pre-existing cross-account role
  `S3UploadFromComputeRole` (genome-idx account `128342663110`); the AWS CLI
  assumes it via `credential_source = Ec2InstanceMetadata`. No keys ever stored.
- **You → uploading inputs:** profile **`index-zone-s3`** (`aws login --profile data-langmead` first).
- **You → `cdk deploy`:** profile **`jhu-langmead`** (`aws sso login` first).

### Instance role — already exists, no setup needed

This stack **reuses** the standing role `index-zone-movi-kmer-bench-role` created
once by `build/movi_kmer_bench/setup_permanent_role.sh`. Its trust on
`S3UploadFromComputeRole` is **account-scoped to `159168350739:root`**, so the MEM
stack works with **no IAM changes** — do *not* re-run `setup_permanent_role.sh`
(a copy is included only for reference). The stack references the role with
`iam.Role.from_role_name(..., mutable=False)`, so `cdk destroy` never touches it.

> If results upload is ever denied, the run still completes — the tarball stays on
> the instance under `~/bench/movi_mem_pmu_results.tar.gz` (scp via the `.pem`).

## Inputs in S3 — stage these before the first deploy

The index reuses the existing public `index.movi`; `ftab.10.bin` and `one453.fasta`
are reused from the kmer-bench prefix. **New MEM inputs you must upload:**

| config key | object | how to produce |
|-----|--------|-----|
| `src_s3_uri`   | `…/mem_bench/movi_src.tar.gz` | tar the local `movi-work/Movi` at branch `coroutine` HEAD `e8d4dea` (the MEM redesign). Verify `query_mem_coroutine` / `step_prep` are present. |
| `ftab_s3_uris[1]` | `…/mem_bench/ftab.12.bin` (537 MB) | from the Rockfish index dir `/scratch16/blangme2/movi_coro_bench/ftab.12.bin`. |
| reads | `…/mem_bench/reads/mem2k.fasta.gz` | gzip `…/movi_coro_bench/reads/mem2k.fasta` from Rockfish. |
| `index_s3_uri` | `s3://genome-idx/movi/movi2_hprc1_thresh/index.movi` | already public (reused). |
| `ftab_s3_uris[0]` | `s3://genome-idx/movi/kmer_bench/ftab.10.bin` | already public (reused). |
| reads | `…/mem_bench/reads/one453.fasta` | copy/reuse from kmer_bench, or re-upload. |

Upload from the Mac (where the `index-zone-s3` role works):

```bash
aws login --profile data-langmead     # refresh base creds (index-zone-s3 chains off it)
aws s3 --profile index-zone-s3 cp dist/movi_src.tar.gz s3://genome-idx/movi/mem_bench/movi_src.tar.gz
aws s3 --profile index-zone-s3 cp ftab.12.bin          s3://genome-idx/movi/mem_bench/ftab.12.bin
aws s3 --profile index-zone-s3 cp mem2k.fasta.gz       s3://genome-idx/movi/mem_bench/reads/mem2k.fasta.gz
aws s3 --profile index-zone-s3 cp one453.fasta         s3://genome-idx/movi/mem_bench/reads/one453.fasta
```

## Deploy

```bash
aws sso login --profile jhu-langmead
export AWS_PROFILE=jhu-langmead
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
# cdk's JS SDK cannot read the SSO-session profile directly -> export temp creds:
eval "$(aws configure export-credentials --profile jhu-langmead --format env)"
export AWS_DEFAULT_REGION=us-east-1
./deploy.sh           # bootstrap + synth + deploy, writes movi-mem-bench.pem
./ssh.sh              # optional: watch /var/log/movi-bench-userdata.log and ~/bench/bench.out
```

When `SENTINEL_DONE` appears in S3, fetch the results tarball. The headline
artifacts to read are the `prod_seq_f10_lines.cycles.byline.txt` (does scan code
dominate cycles?) and `prod_seq_f10_lines.l3miss.byline.txt` (are misses diffuse /
low?) — that pair confirms compute- vs memory-bound and points at the optimization
target.

## ⚠️ Cost / teardown

`c5.metal` is a whole physical server (~$2.10/hr spot here). It does **not**
self-terminate. When done:

```bash
cdk destroy
```

## Optional: VTune

Set `"install_vtune": true` in `config.json` to also install Intel VTune. `perf`
already provides the per-line attribution, so this is off by default.
