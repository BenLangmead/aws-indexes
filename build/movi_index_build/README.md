# movi_index_build

AWS CDK workflow that builds a **full Movi pangenome index** (grlBWT → TeraLCP →
Movi, mode 6 / separators + thresholds) on a single large **spot** instance,
cost-minimized, with **S3 phase-checkpointing and auto-resume** so a ~12-day build
survives the spot interruptions that are otherwise near-certain over that window.

This is the AWS counterpart to the Rockfish Snakemake pipeline in
[`build/movi/snakemake`](../movi/snakemake). It reproduces the same steps, starting
from the small (~3 GB) AGC archive so only that one file is staged to S3.

## How it works

1. An **Auto Scaling Group** (desired = 1) launches one spot instance from a launch
   template, spanning several AZs so the (replacement) instance lands wherever spot
   capacity is cheapest/available.
2. First boot: install toolchain, stripe the instance-store NVMe into a RAID-0 array
   at `/data` (the ~5–6 TB working set lives here — fast and free with the instance),
   write `job.sh`, run it as `ec2-user`.
3. `job.sh` builds `agc`, `grlBWT`, `TeraTools`, and `Movi` from source, then runs the
   pipeline as **resumable phases**, each guarded by a marker object in S3:

   | Phase | Steps | Durable artifact synced to S3 on success |
   |-------|-------|------------------------------------------|
   | `rlbwt` | agc decompress → `movi-prepare-ref` (separators + revcomp) → concat → grlBWT → grlbwt2rle → grlbwt2teralcp | `grl.bwt.heads/len` + `ref.fa.bwt.heads/len` (~50 GB — captures the ~3.5-day grlBWT, never repeated) |
   | `construct` | `TeraLCP -f rlbwt -checkpoint …` (the ~8.5-day long pole) | `teralcp.lcp_index`; the live `-checkpoint` dir is synced every 10 min **and** on the spot 2-minute termination notice |
   | `thresholds` | `TeraLCP -f lcp_index -othresholds …` | `septera.thr` / `septera.thr_pos` |
   | `movi` | stage thresholds → `movi build` → `movi ftab` (k = 12,10,8,6,4,2) | final `index.movi` + ftabs → **output** prefix |

4. On a spot reclaim the ASG brings up a fresh instance; `job.sh` pulls the latest S3
   checkpoint and continues from the first unfinished phase. Instance-store loss is
   harmless — all durable state is in S3.
5. On final success the instance scales the ASG to **0** to stop billing.

### Why this layout minimizes cost

- **Spot + instance-store NVMe**: cheapest compute and the fastest, free scratch.
- **Start from the 3 GB AGC archive**, not the 2.6 TB concatenated input — trivial to
  stage, and the pre-grlBWT steps (cheap CPU) re-run locally on a resume with no
  multi-TB S3 transfer.
- **Phase checkpoints** mean an interruption on day 11 costs minutes, not a restart.
  The single biggest cost risk on a 12-day spot job is recompute-after-reclaim; this
  removes it, leveraging the TeraLCP `-checkpoint`/`-stop-after` work.

## Configure (`config.json`)

| Key | Meaning |
|-----|---------|
| `collection` | Index name; used in S3 prefixes (`…/<collection>/…`) and the ASG name. |
| `agc_s3` | S3 URI of the AGC archive to build from. |
| `haplotypes` | `"ALL"` or a comma-separated subset of AGC sample names. |
| `ftab_k`, `ftab_extra_k` | ftab orders to build (k = 12 plus extras). |
| `teralcp_p` | TeraLCP threads (`0` ⇒ `nproc`). |
| `s3_work_prefix` | Base for phase markers + checkpoints (`<prefix>/<collection>/state,ckpt`). |
| `s3_output_prefix` | Base for the finished index (`<prefix>/<collection>/index,logs`). |
| `repos` | git URL + branch for `agc`, `grlbwt`, `teratools`, `movi`. **The `teratools` branch must have `-checkpoint`/`-stop-after`; the `movi` branch must have parallel `ftab` + `movi-prepare-ref`.** |
| `asg_name` | Fixed ASG name (so `job.sh` can scale it to 0). |
| `instance_profile` | Selects one entry under `instance_type`. |
| `instance_type.<profile>` | `region`, `availability_zone`, `preferred_availability_zones`, `type`, `spot_price` (string). |

### Instance sizing

Two independent constraints, and they point at **storage-optimized** instances:

- **Local scratch disk is the binding constraint: instance-store NVMe ≥ ~6 TB.**
  Peak working set ≈ 5.2 TB (concat `clean.fa` 2.6 TB + `grl_in` 2.6 TB; grlBWT
  `grl_in` 2.6 TB + `grltmp` ~1.8 TB).
- **RAM peak is only ~300 GiB** (yr2 estimate; yr1 actuals: construct ~134 GiB,
  grlBWT ~84 GiB). So ~384–512 GiB of RAM is ample — no need for a high-memory node.

The `i4i` family (storage-optimized, Intel + Nitro NVMe) hits both cheaply; the
memory-optimized `x2*`/`r*` families would force us to pay for 1.5–4 TB of RAM we
never use just to get the NVMe.

| Profile | Type | RAM | Instance-store NVMe | Notes |
|---------|------|-----|---------------------|-------|
| `default` | `i4i.12xlarge` | 384 GiB | 3×3.75 TB ≈ 11.25 TB | Cheapest that clears the ~300 GiB RAM peak and ~6 TB disk peak. |
| `headroom` | `i4i.16xlarge` | 512 GiB | 4×3.75 TB ≈ 15 TB | Use if the yr2 grlBWT RAM peak surprises us, or for extra disk slack. |
| `test` | `t3.micro` | — | — | Synth/deploy smoke test only (no NVMe; will not run the real build). |

`i4i.8xlarge` (256 GiB / 7.5 TB) would clear the disk peak but its RAM is too close to
the ~300 GiB peak to be safe. Confirm the chosen type's spot price/region with
[`../../spot_shopper.py`](../../spot_shopper.py) and [`../../AWS.md`](../../AWS.md);
at ~$1.3–2/hr spot for `i4i.12xlarge`, a ~12-day build is ≈ **$400–600**.

## Credentials & IAM

Like `build/tera`, AWS creds are read at synth time from `~/.aws/credentials`
`[data-langmead]` and embedded in user-data; the instance uses them for all S3 I/O.
For the end-of-job **`scale_down`** to work, those creds need
`autoscaling:UpdateAutoScalingGroup` on the ASG — if denied, the instance simply
idles when done and you tear it down with `./destroy.sh` (the index is already in S3).

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 0. Stage the AGC archive once (from anywhere that has it + S3 access):
#    aws s3 cp human472.agc s3://genome-idx/movi/inputs/human472.agc

# 1. Edit config.json (collection, agc_s3, repo branches, instance_profile, spot prices)

# 2. Deploy (bootstrap + synth + deploy + fetch SSH key)
./deploy.sh

# 3. Watch it
./ssh.sh            # then: tail -f /data/job.out   (or /var/log/cloud-init-output.log)
aws s3 ls s3://genome-idx/movi/aws-build/<collection>/state/   # phase markers as they complete

# 4. When done, the ASG self-scales to 0. Tear down infra (keeps S3 artifacts):
./destroy.sh
```

## Resuming / re-running

Resume is automatic: a fresh instance reads the S3 phase markers and continues. To
**force** a rebuild of a phase, delete its marker (and downstream markers):

```bash
aws s3 rm s3://genome-idx/movi/aws-build/<collection>/state/phase.construct.done
aws s3 rm s3://genome-idx/movi/aws-build/<collection>/state/phase.thresholds.done
# … then bump the ASG back to desired=1 (or redeploy).
```

## Output layout

```
s3://genome-idx/movi/aws-build/<collection>/
    state/   phase.rlbwt.done, phase.construct.done, …, phase.complete.done
    ckpt/    rlbwt/ (grl.bwt.*, ref.fa.bwt.*), teralcp.ckpt/ (live), teralcp.lcp_index, thr/

s3://genome-idx/movi/indexes/<collection>/
    index/   index.movi, ref.fa.bwt.*, ref.fa.thr*, ftab.{12,10,8,6,4,2}.bin
    logs/    summary.txt, *.stdout/.stderr, disk_usage_samples.log
```

## Notes vs `build/tera`

- Whole pipeline (not just TeraLCP) and starts from AGC, not an FMD.
- Auto Scaling Group + spot for auto-relaunch (tera used a single `CfnInstance`).
- S3 phase-marker checkpointing + a spot-termination watcher that flushes the live
  TeraLCP checkpoint on the 2-minute notice.
- Same conventions otherwise: `gcc-c++`, NVMe RAID-0 at `/data`, string `spot_price`,
  `job.sh` via quoted heredoc run as `ec2-user`, psrecord/`time` monitoring.
```
