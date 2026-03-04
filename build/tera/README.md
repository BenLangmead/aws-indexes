# tera

AWS CDK workflow for running [TeraLCP](https://github.com/BenLangmead/TeraTools)
on the OpenHGL `human579` FMD index.

## What it does

Provisions an EC2 spot instance that:
1. Mounts local NVMe drives as a RAID-0 volume at `/data`
2. Clones and builds [TeraTools](https://github.com/BenLangmead/TeraTools) (`sdsl-integrate` branch)
3. Downloads `human579.fmd` from `s3://openhgl/human/human579/`
4. Runs `TeraLCP` under `psrecord` + `/usr/bin/time -v` with a background disk sampler
5. Collects wall-clock time, peak RSS, peak virtual memory, and peak disk usage
6. Uploads output files, logs, a summary `.txt`, and a `TeraTools.tar.gz` to:
   `s3://genome-idx/movi/tera-openhgl/YYYYMMDD/`

## Instance choice

| Property | Value |
|---|---|
| Instance type | `m7gd.metal` |
| vCPUs | 64 (Graviton3, ARM) |
| RAM | 256 GB |
| Local storage | 3800 GB NVMe SSD (2×1900 GB, RAID-0) |
| Region / AZ | `ap-northeast-2` (Seoul; AZs: 2a, 2b, 2c) |
| Spot bid | $1.00/hr |

Configure in `config.json`: `region`, `preferred_availability_zones`, and `instance_type.large` (type + spot_price).

**Storage:** The instance has one EBS (gp3) root volume from the AMI—required for the OS. All job data uses instance store (NVMe) mounted at `/data`; the stack does not add any extra EBS volumes.

**Availability zone choice:** `preferred_availability_zones` lists AZs in try order. The stack uses the first AZ in that list that has a subnet.

## S3 output layout

```
s3://genome-idx/movi/tera-openhgl/YYYYMMDD/
    output/          ← TeraLCP output files (human579.*, human579.rlcp)
    logs/
        summary.txt            ← wall clock, peak RSS, peak virt, peak disk
        tera_resource_usage.log  ← psrecord time-series (CPU, RSS MB, virt MB)
        tera_resource_plot.png
        tera_stdout.log
        tera_stderr.log        ← also contains /usr/bin/time -v output
        disk_usage_samples.log
        os_info.txt
        teralcp_help.txt
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
