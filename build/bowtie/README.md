# Bowtie 2 index builds

This directory builds newer Bowtie 2 indexes that are candidates for the
Index Zone Bowtie page.  The CDK workflow uploads directly to
`s3://genome-idx/bt`; the older `xfer/bt` workflow can still copy
already-built staging files from `s3://bt2-bench/indexes`.

## Targets

Targets are listed in `targets.tsv`.  The current set covers recent gaps
identified in the Bowtie catalog:

- Human: `GRCh38.p14`, `hs1` / T2T-CHM13v2.0
- Rat: `GRCr8`
- Cow: `ARS-UCD2.0`
- Dog: `ROS_Cfam_1.0`
- Chicken: `bGalGal1.mat.broiler.GRCg7b`
- Rice: `IRGSP-1.0`
- Wheat: `IWGSC`
- Barley: `MorexV3_pseudomolecules_assembly`

Wheat and barley are expected to produce Bowtie 2 large-index files
ending in `.bt2l`; the build script detects `.bt2` versus `.bt2l`
after `bowtie2-build` completes.

## Local build

Install Bowtie 2 and make sure `bowtie2-build`, `samtools`, `curl`,
`gzip`, and `zip` are on `PATH`.

```bash
./build_indexes.bash --list
./build_indexes.bash hs1 grcr8
```

By default, outputs are written to `build/bowtie/out` and temporary
downloads/build files are kept under `build/bowtie/work`.

For a full batch on a large EC2 instance:

```bash
THREADS=32 ./build_indexes.bash --out-dir /work/bt2-indexes --work-dir /work/bt2-build
```

Each successful target produces:

- `${index_base}.zip`
- the six individual `${index_base}.*.bt2` or `${index_base}.*.bt2l` files
- `${index_base}.dict` sequence dictionary from `samtools dict`
- `${index_base}.manifest.json` provenance manifest with source URLs in a
  top-level `source_urls` list, input checksums, build command, tool version,
  output list, and builder ID
- `${index_base}.md5`
- `${index_base}.build.txt` provenance

To upload directly after each target is built:

```bash
./build_indexes.bash --upload-prefix s3://genome-idx/bt hs1 grcr8
```

When adding wheat, barley, or any other large index to
`xfer/bt/shortname_map.csv`, use the optional seventh CSV field
`bt2l` so the generated links point at `.bt2l` files.

## Preflight

Check that the source FASTA URLs in the target catalog still resolve:

```bash
./check_sources.bash
```

For the legacy metadata backfill catalog:

```bash
./check_sources.bash --targets legacy_targets.tsv
```

## Legacy metadata backfill (dict / manifest / build.txt)

Indexes that predate the current CDK workflow often lack `.dict`, `.manifest.json`,
and `.build.txt` on `s3://genome-idx/bt/` even though the `.bt2` / `.bt2l` shards
are present.  The metadata-only path reuses existing shards (no `bowtie2-build`),
downloads a curated reference FASTA from `legacy_targets.tsv`, runs `samtools dict`,
repacks `.zip`, regenerates `.md5`, and uploads sidecars plus updated zip/md5.

**Inventory (read-only):** compare the catalog to the bucket. Authenticate first
(`aws login --profile data-langmead`, then `export AWS_PROFILE=index-zone-s3`;
see `AWS.md` in the repo root), then:

```bash
python3 audit_s3.py
python3 audit_s3.py --require-metadata --strict   # after backfill is complete
```

**Pilot (small genomes):** yeast, BDGP6 fly, WBcel235 worm:

```bash
./run_pilot_metadata_backfill.bash
```

**Full legacy batch:** every id in `legacy_targets.tsv`:

```bash
./run_legacy_metadata_backfill.bash
```

To **resume** after a partial run, use the audit-driven loop (one id per invocation so
failures do not stop the batch):

```bash
./run_resume_missing_metadata_backfill.bash
```

Progress is appended to `legacy_backfill_resume.log`.  `grch37` is passed `--force`
because prior runs left partial uploads.  After starting a long batch, you can run
`./wait_and_audit_legacy_backfill.bash` in another terminal (or `nohup … &`); it
logs progress every five minutes to `legacy_backfill_watch.log` and runs
`audit_s3.py --require-metadata --strict` when the main job writes `EXIT:` to
`legacy_backfill_remaining.log`.

Both runners honor `FROM_S3_PREFIX` and `UPLOAD_PREFIX` (default `s3://genome-idx/bt`).
Manual invocation for a subset:

```bash
./build_indexes.bash --metadata-only --backfill \
  --from-s3-prefix s3://genome-idx/bt \
  --targets legacy_targets.tsv \
  --upload-prefix s3://genome-idx/bt \
  r6411 bdgp6 wbcel235
```

**Docs / link check:** after uploads, confirm objects (see `audit_s3.py`), regenerate
`docs/bowtie.md` from `xfer/bt/` per that directory’s workflow, then:

```bash
cd ../docs && python3 check_site_links.py --only bowtie.md --check-s3
```

Use `--only` to scope S3 HEAD checks to the Bowtie page; a full-repo run still includes
unrelated pages and external URLs that may fail independently.

## CDK build on AWS

This directory also includes a CDK workflow for running the same builder on
an EC2 spot instance.  It is modeled after `build/tera` and
`build/pfp_thresh_builder`: CDK creates a VPC, security group, key pair,
launch template, IAM instance role, and a single EC2 instance.  The
instance user data:

1. Installs build tools, AWS CLI, Python monitoring tools, `curl`, `zip`,
   and related dependencies.
2. Builds Bowtie 2 from `bowtie2_repo` / `bowtie2_ref` in `config.json`.
3. Writes this directory's `build_indexes.bash` and `targets.tsv` onto the
   instance.
4. Runs selected target IDs under `/usr/bin/time -v` while sampling disk use.
5. Uploads index artifacts to `output_s3_prefix` and logs to
   `log_s3_prefix`.

The CDK workflow is designed for a two-profile setup without exposing static
keys:

- Your local temporary deployment profile is used only by CDK/AWS CLI on your
  machine, e.g. `AWS_PROFILE=index-zone-ec2 ./deploy.sh`.
- The EC2 instance uses its IAM instance role for the build.  If
  `upload_role_arn` is set, the instance writes an AWS CLI profile named by
  `upload_profile` (default `data-langmead`) that assumes that role via EC2
  instance metadata.  That profile is used for S3 uploads to the configured
  output and log prefixes:

```ini
[profile data-langmead]
role_arn = arn:aws:iam::ACCOUNT:role/ROLE
credential_source = Ec2InstanceMetadata
```

No static AWS access key or secret key is read from `~/.aws/credentials` or
written into EC2 user data.

Configure the run in `config.json`:

- `target_ids`: list of target IDs to build, or `[]` to build all targets.
- `instance_role_name`: fixed Stack-account IAM role name for the build EC2
  instance.  Default: `index-zone-bowtie-builder-role`.
- `launch_instance`: set to `false` for the first Stack-account bootstrap
  deploy that creates the stable role but does not launch a build instance.
  Set to `true` for the real build run.
- `instance_profile`: one of `small`, `medium`, `large`, `xlarge`.
- `volume_gb`: EBS root volume size used for FASTA downloads, temporary
  files, and outputs.
- `output_s3_prefix`: flat S3 prefix for the final `.zip`, `.bt2`/`.bt2l`,
  `.dict`, `.manifest.json`, `.md5`, and `.build.txt` files.
- `log_s3_prefix`: S3 prefix for `summary.txt`, stdout/stderr, tool versions,
  and disk-use samples.
- `upload_profile`: AWS CLI profile name used on the EC2 instance for final
  uploads.  Default: `data-langmead`.
- `upload_role_arn`: optional role for the EC2 instance to assume for final
  uploads.  Use this for the secure two-profile setup.  If this is left blank,
  S3 uploads use the EC2 instance role directly instead of a
  `data-langmead` profile.

Quick start:

```bash
cd build/bowtie
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# First deploy: leave launch_instance=false so the stable Stack-account role
# exists before configuring the Data-account upload role trust policy.
AWS_PROFILE=index-zone-ec2 ./deploy.sh
```

After the first deploy, read `InstanceRoleArn` from `outputs.json` and use it
as the trusted principal for the Data-account upload role.  Then set
`upload_role_arn` to the Data-account role ARN, set `launch_instance` to
`true`, and deploy again to start the build instance.

Monitor progress:

```bash
./ssh.sh
tail -f /var/log/cloud-init-output.log
tail -f /data/logs/build_stdout.log
```

When the job is done, logs should be under:

```bash
aws s3 ls s3://genome-idx/bt/build-logs/
```

Index artifacts should be under:

```bash
aws s3 ls s3://genome-idx/bt/
```

Destroy the stack when finished:

```bash
./destroy.sh
```
