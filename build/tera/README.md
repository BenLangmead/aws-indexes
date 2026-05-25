# tera

AWS CDK workflow for running [TeraLCP](https://github.com/BenLangmead/TeraTools)
on the OpenHGL `human579` FMD index.

## What it does

Provisions an EC2 spot instance that:
1. Mounts local NVMe drives as a RAID-0 volume at `/data`
2. Clones and builds [TeraTools](https://github.com/BenLangmead/TeraTools) (`sdsl-integrate` branch)
3. Downloads `{index_stem}.fmd` from `s3://openhgl/human/{index_stem}/` (default `human579`)
4. **Either** runs full `TeraLCP` **or** resumes with `RunLCP` from an existing `.lcp_index` (see `run_mode` below)
5. Under `psrecord` + `/usr/bin/time -v`, with a background disk sampler
6. Collects wall-clock time, peak RSS, peak virtual memory, and peak disk usage
7. Uploads output (full sync or threshold files only; see `run_mode`), logs, a summary `.txt`, and `TeraTools.tar.gz` to:
   `s3://genome-idx/movi/tera-openhgl/YYYYMMDD/`

## Instance choice

| Property | Value (example; see `config.json`) |
|---|---|
| Instance type | e.g. `r6gd.metal` or `m7gd.metal` — set per profile under `instance_type` |
| Region / AZ | Per profile: `region`, `availability_zone`, `preferred_availability_zones` |
| Spot bid | Per profile: `spot_price` (string) |

Configure in `config.json`:

- **`instance_profile`**: string key selecting one entry under **`instance_type`** (e.g. `"small"`, `"medium"`, `"large"`).
- Each **`instance_type.<profile>`** object must include: **`region`**, **`availability_zone`**, **`type`** (EC2 instance type), **`spot_price`**, and usually **`preferred_availability_zones`** (list of AZs in try order; if omitted, defaults to a single-element list containing `availability_zone`).

The CDK app deploys into **`instance_type[instance_profile].region`**.

**`/data` (instance store):** First-boot user data discovers whole-disk NVMe namespaces (`/dev/nvme*n1`), skips the EBS root disk (via `lsblk`), stripes the rest with RAID-0, and mounts the array at `/data`. If you see a warning in `cloud-init-output.log` about no instance-store NVMe or `/data` is small and on the root EBS volume, confirm the profile’s **`type`** includes local SSDs (e.g. [R6gd is Graviton with NVMe](https://aws.amazon.com/ec2/instance-types/r6g/), including `r6gd.metal` with 2×1900 GB), and that the **AMI architecture matches the instance** (CDK maps types to `arm64` vs `x86_64` for Amazon Linux 2023).

### `run_mode`: full TeraLCP vs RunLCP resume

| Key | When | Meaning |
|-----|------|---------|
| `run_mode` | Always | `"teralcp"` (default): build index + rlcp + thresholds in one `TeraLCP` run. `"runlcp"`: download an existing `{index_stem}.lcp_index` from S3 and run `RunLCP` (`--mode thresholds`) only. |
| `index_stem` | Always | Default `"human579"`. Used for FMD paths, local filenames, and RunLCP `-o` prefix. |
| `lcp_index_source_s3_prefix` | **Required** if `run_mode` is `"runlcp"` | S3 **directory** prefix (with or without trailing `/`) that contains `{index_stem}.lcp_index`. Example: `s3://genome-idx/movi/tera-openhgl/20260312/output`. May differ from where this run uploads results (the job still uses a new dated `YYYYMMDD` prefix on upload). |

Synth fails fast if `run_mode` is `runlcp` and `lcp_index_source_s3_prefix` is empty or missing.

In **`runlcp`** mode, the instance downloads the `.lcp_index` into `/data/resume_input/` and writes thresholds under `/data/output/`; **only** `thr` and `thr_pos` files are copied to `…/output/` on S3 (not a full directory sync). Logs and `TeraTools.tar.gz` are uploaded the same as in `teralcp` mode. `summary.txt` records `Run mode` and the LCP index S3 source.

**Memory:** the thresholds phase can still need very large RAM (similar to the end of a full `TeraLCP` run). If you previously hit OOM on ~256 GiB instances, use a larger memory footprint (e.g. high-memory metal) for `runlcp` as well.

**RunLCP path:** the job sets `RUNLCP=/home/ec2-user/TeraTools/src/RunLCP/RunLCP`. If your build puts the binary elsewhere, edit that line in [`tera_stack/tera_stack.py`](tera_stack/tera_stack.py).

Example `config.json` snippet for resuming from a prior upload:

```json
"run_mode": "runlcp",
"index_stem": "human579",
"lcp_index_source_s3_prefix": "s3://genome-idx/movi/tera-openhgl/20260312/output"
```

**Storage:** The instance has one EBS (gp3) root volume from the AMI—required for the OS. All job data uses instance store (NVMe) mounted at `/data`; the stack does not add any extra EBS volumes.

**Availability zone choice:** Within the selected `instance_profile`, `preferred_availability_zones` lists AZs in try order. The stack uses the first AZ in that list that has a subnet.

## S3 output layout

```
s3://genome-idx/movi/tera-openhgl/YYYYMMDD/
    output/          ← teralcp: full outputs; runlcp: {stem}.thr and {stem}.thr_pos only
    logs/
        summary.txt            ← wall clock, peak RSS, peak virt, peak disk; run mode + index source
        tera_resource_usage.log  ← psrecord time-series (CPU, RSS MB, virt MB)
        tera_resource_plot.png
        tera_stdout.log
        tera_stderr.log        ← also contains /usr/bin/time -v output
        disk_usage_samples.log
        os_info.txt
        teralcp_help.txt
        runlcp_help.txt        ← present when run_mode is runlcp
    TeraTools.tar.gz ← full build directory (binaries + source)
```

## Quick start

**Note:** `deploy.sh` runs the AWS CDK CLI (`cdk bootstrap`, `cdk synth`, `cdk deploy`). The CDK CLI is a Node.js tool and is not installed via `pip`. Either install it globally (`npm install -g aws-cdk`) or ensure Node.js is available so the script can use `npx aws-cdk`.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Deploy (bootstrap + synth + deploy + fetch SSH key)
./deploy.sh

# SSH into the running instance to monitor progress
./ssh.sh

# Progress is visible in /var/log/cloud-init-output.log on the instance
# Job logs land in /data/logs/ as it runs
```

### Useful CDK commands

- `cdk ls` — list all stacks
- `cdk synth` — emit the synthesized CloudFormation template
- `cdk deploy` — deploy to AWS
- `cdk diff` — compare deployed stack with current state
- `cdk destroy` — tear down the stack

## Design notes vs `pfp_thresh_builder`

- Package name fixed: `gcc-c++` (not `g++`)
- User data uses `'\n'.join()` throughout; no `' '.join()` collapse
- Spot prices are strings in `config.json` (avoids CDK float→string bug)
- NVMe drives discovered dynamically and striped with RAID-0
- Job script written to `/home/ec2-user/job.sh` and executed via
  `su - ec2-user`, avoiding the inline heredoc termination bug
- `gnu time` package explicitly installed for `/usr/bin/time -v`
- `git submodule update --init --recursive` added after clone
