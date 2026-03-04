# pfp_thresh_builder

## Project Summary

`pfp_thresh_builder` is a Python AWS CDK project that automatically provisions an EC2 spot instance and runs compute job: building a **run-length BWT index with thresholds** (via [`pfp-thresholds`](https://github.com/mohsenzakeri/pfp-thresholds)) over the HPRC (Human Pangenome Reference Consortium) genome dataset. The resulting index is intended for downstream tools like [Movi](https://github.com/mohsenzakeri/movi) or [SPUMONI](https://github.com/oma219/spumoni). It lives within the broader [`aws-indexes`](https://benlangmead.github.io/aws-indexes/) repository, which maintains a catalog of publicly accessible genomic indexes on AWS.

---

## Core Components

### `app.py` — CDK Entry Point

Reads `config.json`, instantiates `CdkEc2Stack`, and calls `app.synth()` to emit the CloudFormation template. The region is passed explicitly from config (hardcoded account: `159168350739`).

### `ec2_example/ec2_example_stack.py` — `CdkEc2Stack`

The single CDK stack. Responsibilities at synth time:

- Creates a **VPC** with a single public /24 subnet (max 2 AZs)
- Creates a **Security Group** with SSH ingress (port 22) and all-egress
- Creates an EC2 **key pair** named `hprc-build`
- Defines an EC2 **Launch Template** using the latest Amazon Linux 2023 AMI with a **spot instance** bid
- Reads local AWS credentials (`~/.aws/credentials`, profile `data-langmead`) and **embeds them into the EC2 user data script**
- Constructs a multi-step **bash user data script** (see Runtime Behavior)
- Instantiates a `CfnInstance` using the launch template, pinned to a specific AZ
- Exports the key pair ID and public IP as CloudFormation outputs

### `config.json` — Deployment Configuration

Controls all environment-specific settings:

- `region`: `eu-north-1`, `availability_zone`: `eu-north-1b`
- `instance_type.large`: `x2iedn.24xlarge` at $3.00/hr spot (96 vCPUs, ~3 TiB RAM — appropriate for large BWT construction)
- `instance_type.small`: `t3.micro` at $0.005/hr (for testing)
- `use_large_instance`: boolean flag to toggle between the two

### `deploy.sh` — Deployment Orchestrator

Runs `cdk bootstrap` → `cdk synth` → `cdk deploy --outputs-file outputs.json`, then retrieves the EC2 SSH private key from **AWS SSM Parameter Store** and writes it to `hprc-build.pem`.

### `ssh.sh` — SSH Convenience Wrapper

Parses `outputs.json` for the instance's public IP and SSHs in as `ec2-user`.

---

## Component Interactions

```
config.json
    │
    ├──► app.py  ──► CdkEc2Stack (ec2_example_stack.py)
    │                      │
    │          ~/.aws/credentials (data-langmead profile)
    │                      │  (read at CDK synth time)
    │                      │
    │                EC2 user data script (bash, base64-encoded)
    │                      │
    │           ┌──────────┴──────────────┐
    │           S3 (genome-idx bucket)   GitHub (pfp-thresholds)
    │
deploy.sh ──► cdk deploy ──► CloudFormation ──► EC2 instance
                                 │
                           SSM Parameter Store (private key)
```

- `config.json` is read **twice**: once in `app.py` (for region/env) and once inside `CdkEc2Stack.__init__` (for AZ and instance type). Both reads happen at CDK synth time on the developer's machine.
- AWS credentials are read from the local `~/.aws/credentials` file at synth time and written verbatim into the EC2 user data — making the credential provisioning part of the CloudFormation template itself.
- The user data script executes **only on the EC2 instance at boot**, not during synthesis.

---

## Deployment Architecture

| Aspect | Detail |
|---|---|
| IaC Framework | AWS CDK (Python), `aws-cdk-lib==2.198.0` |
| AWS Account / Region | `159168350739` / `eu-north-1` |
| Instance type (large) | `x2iedn.24xlarge` (spot), max $3.00/hr |
| AMI | Latest Amazon Linux 2023 (resolved at deploy time) |
| Networking | New VPC, 1 public subnet (/24), AZ: `eu-north-1b` |
| Key management | CDK creates key pair; private key stored in SSM Parameter Store, retrieved by `deploy.sh` |
| No containers | All tooling installed directly on the EC2 host via user data |
| Dependencies | `aws-cdk-lib`, `constructs` (runtime); `pytest` (dev) |

---

## Runtime Behavior

The EC2 user data script executes sequentially on boot in four phases:

**1. System Setup**
```bash
yum update && yum install docker git emacs gcc g++ cmake zlib-devel
systemctl enable/start docker
python3 -m pip install psrecord matplotlib
```

**2. AWS Credential Provisioning on Instance**

Writes the credentials (embedded at synth time) to `/home/ec2-user/.aws/credentials` with `chmod 600`.

**3. Tool Build**
```bash
git clone -b build-options https://github.com/mohsenzakeri/pfp-thresholds.git
mkdir -p pfp-thresholds/build && cmake .. && make -j 16
```

**4. Data Download + Job Execution**
```bash
aws s3 cp s3://genome-idx/movi/hprcv2_inputs/hprc466.fa.dict /tmp/
aws s3 cp s3://genome-idx/movi/hprcv2_inputs/hprc466.fa.parse /tmp/
cd /tmp && pfp_thresholds --skip-parsing -r -f ./hprc466.fa
```

The job is wrapped with `psrecord` (via `_wrapped_named_command`) which logs CPU/memory usage at 15-second intervals and produces a resource usage plot — enabling post-hoc performance analysis.

All stdout/stderr and resource plots go to a `logs/` directory on the instance. The `-r` flag is required to avoid exhausting disk space.

There are no background daemons, web services, or request/response patterns — this is a **one-shot batch compute system**. Monitor progress by SSHing in via `ssh.sh` and inspecting the `logs/` directory.

---

## Quick Start

```bash
# Set up Python virtualenv
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Deploy (bootstrap + synth + deploy + retrieve SSH key)
./deploy.sh

# SSH into the running instance
./ssh.sh
```

### Useful CDK commands

- `cdk ls` — list all stacks
- `cdk synth` — emit the synthesized CloudFormation template
- `cdk deploy` — deploy to the configured AWS account/region
- `cdk diff` — compare deployed stack with current state
- `cdk docs` — open CDK documentation
