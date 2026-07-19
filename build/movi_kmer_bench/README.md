# movi_kmer_bench

CDK stack that provisions a **bare-metal `c5.metal` spot instance** and runs
**granular hardware-PMU benchmarking** of the Movi `movi-co` k-mer coroutine
query — the per-source-line cache-miss attribution we could *not* get on the
Rockfish dev node (its `perf_event_paranoid=2` blocks event-based sampling).

## Why c5.metal

- **Bare metal → full PMU/PEBS.** Virtualized Nitro instances hide event-based
  sampling, so per-line `perf`/VTune attribution needs metal.
- **Cascade Lake (Xeon Platinum 8275CL)** — same microarchitecture as the
  Rockfish Xeon Gold 6248R we profiled, so `mem_load_retired`, `cycle_activity`
  and TMA behave identically and numbers are comparable.
- **192 GB RAM** holds the full 37 GB index; ~$4.08/hr on-demand. We bid
  **spot at $2.10 (~½ on-demand)** so price-based interruption is very unlikely.

## What it measures

Two regimes (`no-ftab` = compute-heavy; `ftab-10` = the realistic, memory-bound
one) × latency-hiding width `W ∈ {1, 8}`, all pinned to one core on NUMA node 0:

- `perf stat` — IPC, L3-miss loads, DRAM-stall cycles, and MLP
  (`offcore_requests_outstanding`).
- `perf record -e mem_load_retired.l3_miss:pp` → **per-source-line** histogram of
  the loads that miss to DRAM (`*.l3miss.byline.txt` / `*.bysym.txt`).
- `likwid-perfctr` — `TMA`, `CYCLE_STALLS`, `MEM` (DRAM bandwidth, now with
  uncore since we're root with paranoid=-1).
- A 1-read run per regime bounds the index-load contribution for differencing.

Results are tarred to `s3://genome-idx/movi/kmer_bench/results/` (see the
`ResultsLocation` output), with a `SENTINEL_DONE` marker when finished (~30–45
min after boot).

## Authentication model — no permanent credentials (same as `build/bowtie`)

- **Instance → S3 downloads:** the `genome-idx` inputs are public-read, so the
  instance fetches them with `aws s3 cp --no-sign-request` — no credentials.
- **Instance → results upload:** the instance role is allowed to
  `sts:AssumeRole` the pre-existing cross-account role
  `S3UploadFromComputeRole` (in the genome-idx account `128342663110`); the AWS
  CLI assumes it via an `~/.aws/config` profile with
  `credential_source = Ec2InstanceMetadata`. No keys ever stored.
- **You → uploading inputs:** profile **`index-zone-s3`** (`aws login --profile data-langmead` first).
- **You → `cdk deploy`:** profile **`jhu-langmead`** (`aws sso login` first).

> ⚠️ **Trust prerequisite:** `S3UploadFromComputeRole`'s trust policy must permit
> this stack's instance role (`index-zone-movi-kmer-bench-role`, ARN in the
> `InstanceRoleArn` output) to assume it. If results upload is denied, the
> run still completes — the tarball stays on the instance under `~/bench/` for
> manual retrieval.

### Permanent role (do this ONCE — then never re-save the trust)

The instance role is a **standing, out-of-band role**, not created by CDK. This is
deliberate: a CDK-managed role is deleted on `cdk destroy`, and deleting a role
that is named in a cross-account trust policy invalidates that trust (AWS converts
it to a stale unique-id), so it had to be re-saved after every redeploy. The stack
now only *references* the role (`iam.Role.from_role_name(..., mutable=False)`), so
the trust below is set once and survives any number of deploy/destroy cycles.

**Step 1 — create the role (account `159168350739`, profile `jhu-langmead`):**

```bash
aws sso login --profile jhu-langmead
./setup_permanent_role.sh          # idempotent; prints the role ARN
# -> arn:aws:iam::159168350739:role/index-zone-movi-kmer-bench-role
```

**Step 2 — trust it from the upload role (account `128342663110`).** This needs
IAM-admin access in the genome-idx account (the `index-zone-s3`/`data-langmead`
IAM *user* cannot edit roles — do it in the console or with an admin role). Make
`S3UploadFromComputeRole`'s trust policy include this stack's role. Account-scoping
to `159168350739` is simplest and also covers the bowtie builder role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::159168350739:root" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

If you prefer to list specific roles instead of `:root`, use:
`"AWS": ["arn:aws:iam::159168350739:role/index-zone-movi-kmer-bench-role",
"arn:aws:iam::159168350739:role/index-zone-bowtie-builder-role"]`.

After these two one-time steps, `cdk deploy`/`cdk destroy` never touch the trust.

## Inputs in S3 (already uploaded)

All inputs live under `s3://genome-idx/movi/kmer_bench/` (public-read) except the
index, which reuses the existing public `index.movi`:

| config key | object |
|-----|--------|
| `src_s3_uri`   | `…/kmer_bench/movi_src.tar.gz` — Movi source at the k-mer commit (008f279) |
| `index_s3_uri` | `s3://genome-idx/movi/movi2_hprc1_thresh/index.movi` (37 GB, MODE-6 HPRC) |
| `ftab_s3_uri`  | `…/kmer_bench/ftab.10.bin` |
| reads          | `…/kmer_bench/reads/{real_100k,sim_100k}.fasta.gz`, `one453.fasta` (gz read natively) |

To re-upload (from the Mac, where the `index-zone-s3` role works):

```bash
aws login --profile data-langmead     # refresh base creds (index-zone-s3 chains off it)
aws s3 --profile index-zone-s3 cp dist/movi_src.tar.gz s3://genome-idx/movi/kmer_bench/movi_src.tar.gz
# …ftab.10.bin, reads/*.gz, one453.fasta similarly
```

## Deploy

```bash
aws sso login --profile jhu-langmead
export AWS_PROFILE=jhu-langmead
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
./deploy.sh           # bootstrap + synth + deploy, writes movi-kmer-bench.pem
./ssh.sh              # optional: log in and watch /var/log/movi-bench-userdata.log
                      #           and ~/bench/bench.out
```

When `SENTINEL_DONE` appears in S3, fetch the results tarball.

## ⚠️ Cost / teardown

`c5.metal` is a whole physical server (~$2.10/hr spot here). It does **not**
self-terminate. When done:

```bash
cdk destroy
```

## Optional: VTune

Set `"install_vtune": true` in `config.json` to also install Intel VTune
(`intel-oneapi-vtune`) for a GUI/CLI Memory-Access view. `perf` already provides
the per-line attribution, so this is off by default.
