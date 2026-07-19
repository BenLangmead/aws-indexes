"""
Stack for building a full Movi pangenome index on AWS spot, cost-minimized.

Reproduces the Rockfish grlBWT -> TeraLCP -> Movi pipeline end to end on a single
large spot instance, starting from the small (~3 GB) AGC archive in S3, so only that
one file has to be staged.  Pipeline: agc decompress -> movi-prepare-ref (separators
+ reverse-complement) -> concat -> grlBWT -> grlbwt2rle -> grlbwt2teralcp adapter ->
TeraLCP construct (checkpointed) -> TeraLCP thresholds -> movi build -> ftab(s).

Cost design (spot, ~12-day build, interruption near-certain):
  - Working set (~5-6 TB peak) lives on instance-store NVMe striped RAID-0 at /data
    (fast + free with the instance), NOT EBS.
  - The job is split into resumable PHASES, each guarded by a marker object in S3.
    On completion a phase syncs its small, expensive-to-recompute artifacts to S3:
      * rlbwt      : grl.bwt.heads/len + ref.fa.bwt.heads/len  (~50 GB; captures the
                     ~3.5-day grlBWT run, so it is never repeated after the first success)
      * construct  : teralcp.lcp_index (and the live -checkpoint dir is synced every
                     few minutes AND on the spot 2-minute termination notice)
      * thresholds : septera.thr/.thr_pos
      * movi       : final index.movi + ftabs -> output prefix
  - An Auto Scaling Group (desired=1, spanning several AZs) relaunches a replacement
    on spot reclaim; its user-data reruns job.sh, which pulls the latest S3 checkpoint
    and continues from the last unfinished phase.  Instance-store loss is harmless
    because all durable state is in S3.
  - On final success the instance scales the ASG to 0 to stop billing.

Mirrors build/tera conventions: config.json instance profiles, NVMe RAID-0 at /data,
AWS creds embedded from ~/.aws/credentials [data-langmead], psrecord+/usr/bin/time
monitoring, job.sh written via a quoted heredoc and run as ec2-user.

Author: Ben Langmead
"""

import configparser
import os
import base64
import json

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    CfnOutput,
    Duration,
)

from constructs import Construct


class MoviIndexBuildStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open('config.json', 'r') as f:
            cfg = json.load(f)

        collection = cfg["collection"]
        key_name = cfg["key_name"]
        agc_s3 = cfg["agc_s3"]
        haplotypes = str(cfg.get("haplotypes", "ALL"))
        ftab_k = int(cfg.get("ftab_k", 12))
        ftab_extra_k = cfg.get("ftab_extra_k", [])
        teralcp_p = int(cfg.get("teralcp_p", 0))   # 0 => nproc
        s3_work = f'{cfg["s3_work_prefix"].rstrip("/")}/{collection}'
        s3_out = f'{cfg["s3_output_prefix"].rstrip("/")}/{collection}'
        asg_name = cfg["asg_name"]
        repos = cfg["repos"]

        instance_profile = cfg.get("instance_profile")
        instance_defs = cfg.get("instance_type") or {}
        if instance_profile not in instance_defs:
            raise ValueError(
                f'config.json "instance_profile" {instance_profile!r} not under '
                f'"instance_type". Available: {sorted(instance_defs)}'
            )
        inst_cfg = instance_defs[instance_profile]
        for ky in ("region", "availability_zone", "type", "spot_price"):
            if ky not in inst_cfg:
                raise ValueError(
                    f'config.json instance_type.{instance_profile} missing key {ky!r}'
                )
        preferred_azs = inst_cfg.get(
            "preferred_availability_zones", [inst_cfg["availability_zone"]]
        )
        region = inst_cfg["region"]

        # ── Networking ────────────────────────────────────────────────────────
        vpc = ec2.Vpc(
            self, "MoviIdxVpc",
            max_azs=6,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="movi-idx-public-subnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
        )

        sec_group = ec2.SecurityGroup(
            self, "MoviIdxSecurityGroup", vpc=vpc, allow_all_outbound=True
        )
        sec_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH access"
        )

        # ── Key pair ─────────────────────────────────────────────────────────
        cfn_key_pair = ec2.CfnKeyPair(self, "MoviIdxKeyPair", key_name=key_name)
        key_pair_ref = ec2.KeyPair.from_key_pair_name(
            self, "MoviIdxKeyPairRef", key_pair_name=cfn_key_pair.key_name
        )

        # ── AMI: match instance architecture (ARM64 vs x86_64) ────────────────
        _arch = ec2.InstanceType(inst_cfg["type"]).architecture
        machine_image = (
            ec2.MachineImage.latest_amazon_linux2023(cpu_type=ec2.AmazonLinuxCpuType.ARM_64)
            if _arch == ec2.InstanceArchitecture.ARM_64
            else ec2.MachineImage.latest_amazon_linux2023(cpu_type=ec2.AmazonLinuxCpuType.X86_64)
        )

        # ── AWS credentials (read at synth time, embedded in user data) ───────
        aws_creds = configparser.ConfigParser()
        aws_creds.read(os.path.expanduser('~/.aws/credentials'))
        aws_access_key_id = aws_creds['data-langmead']['aws_access_key_id']
        aws_secret_access_key = aws_creds['data-langmead']['aws_secret_access_key']

        # ── job.sh: full resumable pipeline (runs as ec2-user) ────────────────
        job_script = _JOB_TEMPLATE
        subs = {
            "__COLLECTION__": collection,
            "__AGC_S3__": agc_s3,
            "__HAPLOTYPES__": haplotypes,
            "__FTAB_K__": str(ftab_k),
            "__FTAB_EXTRA_KS__": " ".join(str(k) for k in ftab_extra_k if k != ftab_k),
            "__TERALCP_P__": str(teralcp_p),
            "__S3_WORK__": s3_work,
            "__S3_OUT__": s3_out,
            "__REGION__": region,
            "__ASG_NAME__": asg_name,
            "__AGC_URL__": repos["agc"]["url"],     "__AGC_BR__": repos["agc"]["branch"],
            "__GRL_URL__": repos["grlbwt"]["url"],  "__GRL_BR__": repos["grlbwt"]["branch"],
            "__TERA_URL__": repos["teratools"]["url"], "__TERA_BR__": repos["teratools"]["branch"],
            "__MOVI_URL__": repos["movi"]["url"],   "__MOVI_BR__": repos["movi"]["branch"],
        }
        for token, value in subs.items():
            job_script = job_script.replace(token, value)
        job_lines = job_script.splitlines()

        # ── Root user-data: packages, NVMe RAID-0, creds, write+run job.sh ────
        root_lines = [
            "#!/bin/bash",
            "set -x",
            "",
            "# ── System packages ──────────────────────────────────────────",
            "dnf update -y",
            "dnf install -y make gcc gcc-c++ git cmake zlib-devel mdadm python3-pip time libatomic tar gzip",
            "",
            "# ── Mount NVMe instance store(s) as RAID-0 at /data ──────────",
            "ROOT_SRC=$(findmnt -n -o SOURCE /)",
            "ROOT_DISK=''",
            "if [ -b \"$ROOT_SRC\" ]; then",
            "    ROOT_DISK=$(lsblk -no pkname \"$ROOT_SRC\" 2>/dev/null | head -1)",
            "fi",
            "if [ -z \"$ROOT_DISK\" ]; then",
            "    ROOT_DISK=$(basename \"$ROOT_SRC\" | sed 's/p[0-9]*$//')",
            "fi",
            "ROOT_DISK=$(basename \"$ROOT_DISK\")",
            "NVME_STORES=''",
            "for dev in /dev/nvme*n1; do",
            "    [ -b \"$dev\" ] || continue",
            "    devname=$(basename \"$dev\")",
            "    [ \"$devname\" = \"$ROOT_DISK\" ] && continue",
            "    NVME_STORES=\"$NVME_STORES $dev\"",
            "done",
            "NVME_COUNT=$(echo $NVME_STORES | wc -w)",
            "mkdir -p /data",
            "if [ \"$NVME_COUNT\" -ge 2 ]; then",
            "    mdadm --create --verbose /dev/md0 --level=0 --raid-devices=$NVME_COUNT $NVME_STORES",
            "    mkfs.xfs /dev/md0",
            "    mount /dev/md0 /data",
            "elif [ \"$NVME_COUNT\" -eq 1 ]; then",
            "    mkfs.xfs $NVME_STORES",
            "    mount $NVME_STORES /data",
            "else",
            "    echo 'WARNING: no instance store NVMe found; /data on root EBS'",
            "fi",
            "chown ec2-user:ec2-user /data",
            "",
            "# ── Python monitoring tools ───────────────────────────────────",
            "python3 -m pip install psrecord matplotlib",
            "",
            "# ── AWS credentials + default region ──────────────────────────",
            "mkdir -p /home/ec2-user/.aws",
            "cat > /home/ec2-user/.aws/credentials << 'EOL'",
            "[data-langmead]",
            f"aws_access_key_id = {aws_access_key_id}",
            f"aws_secret_access_key = {aws_secret_access_key}",
            "EOL",
            "cat > /home/ec2-user/.aws/config << 'EOL'",
            "[profile data-langmead]",
            f"region = {region}",
            "EOL",
            "chmod 600 /home/ec2-user/.aws/credentials",
            "chown -R ec2-user:ec2-user /home/ec2-user/.aws",
            "",
            "# ── Write job script ──────────────────────────────────────────",
            "cat > /home/ec2-user/job.sh << 'JOBEOF'",
        ] + job_lines + [
            "JOBEOF",
            "",
            "chmod +x /home/ec2-user/job.sh",
            "chown ec2-user:ec2-user /home/ec2-user/job.sh",
            "",
            "# ── Execute job as ec2-user (nohup so it survives the boot shell) ─",
            "su - ec2-user -c 'nohup /home/ec2-user/job.sh > /data/job.out 2>&1 &'",
        ]
        user_data_script = '\n'.join(root_lines)

        # ── Launch template (spot) ────────────────────────────────────────────
        launch_template = ec2.LaunchTemplate(
            self, "MoviIdxLaunchTemplate",
            instance_type=ec2.InstanceType(inst_cfg["type"]),
            machine_image=machine_image,
            security_group=sec_group,
            key_pair=key_pair_ref,
            user_data=ec2.UserData.custom(user_data_script),
            require_imdsv2=True,
            spot_options=ec2.LaunchTemplateSpotOptions(
                max_price=float(inst_cfg["spot_price"]),
                # If the spot instance is reclaimed, terminate it; the ASG brings up a
                # replacement, whose user-data resumes from the last S3 checkpoint.
                interruption_behavior=ec2.SpotInstanceInterruption.TERMINATE,
            ),
        )
        launch_template.node.add_dependency(cfn_key_pair)

        # ── Subnets: all public subnets whose AZ is in the preferred list ─────
        # Spanning several AZs lets the ASG place the (replacement) instance wherever
        # spot capacity is available — better availability and price than pinning one AZ.
        vpc_azs = {s.availability_zone for s in vpc.public_subnets}
        chosen = [s for s in vpc.public_subnets if s.availability_zone in preferred_azs]
        if not chosen:
            # Synth-time dummy AZs (dummy1a, ...) before region AZ lookup resolves
            chosen = list(vpc.public_subnets) if all(
                z.startswith("dummy") for z in vpc_azs) else []
        if not chosen:
            raise ValueError(
                f"No subnet for any preferred AZ {preferred_azs}; VPC has {sorted(vpc_azs)}"
            )

        # ── Auto Scaling Group (desired=1) for auto-relaunch on spot reclaim ──
        asg = autoscaling.AutoScalingGroup(
            self, "MoviIdxAsg",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=chosen),
            launch_template=launch_template,
            min_capacity=0,
            max_capacity=1,
            desired_capacity=1,
            auto_scaling_group_name=asg_name,
            # Give the boot + tool build + first S3 sync plenty of time before health checks
            health_checks=autoscaling.HealthChecks.ec2(grace_period=Duration.minutes(30)),
        )

        # ── Outputs ───────────────────────────────────────────────────────────
        CfnOutput(self, "KeyPairId", value=cfn_key_pair.attr_key_pair_id,
                  description="id of the movi-idx-build key pair")
        CfnOutput(self, "AsgName", value=asg.auto_scaling_group_name,
                  description="Auto Scaling Group name (desired=1; job scales to 0 on completion)")
        CfnOutput(self, "S3Work", value=s3_work,
                  description="S3 prefix holding phase markers + checkpoints")
        CfnOutput(self, "S3Output", value=s3_out,
                  description="S3 prefix for the finished Movi index")


# ──────────────────────────────────────────────────────────────────────────────
# job.sh template. Tokens (__FOO__) are substituted at synth time from config.json;
# all $VAR / ${VAR} expand at run time on the instance.  Written into user-data via a
# quoted heredoc (<< 'JOBEOF') so nothing here is expanded at write time.
# ──────────────────────────────────────────────────────────────────────────────
_JOB_TEMPLATE = r"""#!/bin/bash
set -x
export AWS_PROFILE=data-langmead
AWS="aws --profile data-langmead"

COLLECTION=__COLLECTION__
AGC_S3=__AGC_S3__
HAPLOTYPES=__HAPLOTYPES__
FTAB_K=__FTAB_K__
FTAB_EXTRA_KS="__FTAB_EXTRA_KS__"
TERALCP_P=__TERALCP_P__
S3_WORK=__S3_WORK__
S3_OUT=__S3_OUT__
REGION=__REGION__
ASG_NAME=__ASG_NAME__

[ "$TERALCP_P" -eq 0 ] 2>/dev/null && TERALCP_P=$(nproc)

D=/data
LOG=$D/logs
mkdir -p $D $LOG $D/state
cd $D

# ── phase markers live in S3 so they survive instance-store loss ──────────────
phase_done() { $AWS s3 ls "$S3_WORK/state/phase.$1.done" >/dev/null 2>&1; }
mark_done()  { echo "$(date -u)" > /tmp/.m && $AWS s3 cp /tmp/.m "$S3_WORK/state/phase.$1.done"; }

scale_down() {
    # Stop billing once the build is complete (needs autoscaling:UpdateAutoScalingGroup
    # on the embedded IAM creds; if denied, the instance just idles — run destroy.sh).
    $AWS autoscaling update-auto-scaling-group --region "$REGION" \
        --auto-scaling-group-name "$ASG_NAME" --min-size 0 --desired-capacity 0 \
        || echo "WARN: could not scale ASG to 0 — tear down manually with destroy.sh"
}

# ── completion short-circuit (a relaunch after the job already finished) ──────
if phase_done complete; then
    echo "Build already complete; scaling to 0 and exiting."
    scale_down
    exit 0
fi

# ── Build tools from source (fresh each launch; cheap vs. the pipeline) ───────
cd /home/ec2-user
git clone -b __AGC_BR__  --recursive __AGC_URL__  agc       || true
git clone -b __GRL_BR__  --recursive __GRL_URL__  grlBWT    || true
git clone -b __TERA_BR__ --recursive __TERA_URL__ TeraTools || true
git clone -b __MOVI_BR__ --recursive __MOVI_URL__ Movi      || true

( cd agc && git submodule update --init --recursive && cmake -B build -DCMAKE_BUILD_TYPE=Release . && cmake --build build -j$(nproc) )
( cd grlBWT && git submodule update --init --recursive && mkdir -p build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release && make -j$(nproc) )
( cd TeraTools && git submodule update --init --recursive && make -j$(nproc) )
( cd Movi && git submodule update --init --recursive && mkdir -p build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release && make -j$(nproc) )

AGC=/home/ec2-user/agc/build/agc
GRLBWT=/home/ec2-user/grlBWT/build/grlbwt-cli
GRL2RLE=/home/ec2-user/grlBWT/build/grlbwt2rle
TERALCP=/home/ec2-user/TeraTools/src/TeraLCP/TeraLCP
ADAPTER=/home/ec2-user/TeraTools/src/TeraLCP/tools/grlbwt2teralcp
MOVI=/home/ec2-user/Movi/build/movi
MOVI_PREP=/home/ec2-user/Movi/build/bin/movi-prepare-ref

$TERALCP --help > $LOG/teralcp_help.txt 2>&1 || true

# ── (Re)materialize the cleaned reference FASTA from the AGC archive ───────────
# Same steps as Snakefile rules `extract` + `prepare`: agc -> %-separated + revcomp.
# Deterministic, so it can be regenerated for `movi build` on a fresh resumed instance.
make_clean_ref() {   # writes $D/clean.fa
    [ -s $D/clean.fa ] && return 0
    $AWS s3 cp "$AGC_S3" $D/input.agc
    if [ "$HAPLOTYPES" = "ALL" ]; then
        $AGC getcol -t $(nproc) $D/input.agc > $D/input.fa
    else
        $AGC getset -t $(nproc) $D/input.agc $(echo "$HAPLOTYPES" | tr ',' ' ') > $D/input.fa
    fi
    test -s $D/input.fa
    $MOVI_PREP $D/input.fa $D/clean.fa separators
    rm -f $D/input.fa
}

# ── Background: sync TeraLCP checkpoint dir to S3 every 10 min while it exists ─
start_ckpt_syncer() {
    ( while [ -d $D/teralcp.ckpt ]; do
        sleep 600
        $AWS s3 sync $D/teralcp.ckpt/ "$S3_WORK/ckpt/teralcp.ckpt/" --only-show-errors
      done ) &
    CKPT_SYNCER_PID=$!
}
# ── Background: on the spot 2-minute termination notice, flush checkpoint now ──
start_spot_watcher() {
    ( TOK=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
            -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
      while :; do
        ACT=$(curl -s -H "X-aws-ec2-metadata-token: $TOK" \
              http://169.254.169.254/latest/meta-data/spot/instance-action)
        if echo "$ACT" | grep -q action; then
            echo "SPOT TERMINATION NOTICE — flushing checkpoint to S3" >> $LOG/spot_watcher.log
            [ -d $D/teralcp.ckpt ] && $AWS s3 sync $D/teralcp.ckpt/ "$S3_WORK/ckpt/teralcp.ckpt/" --only-show-errors
            break
        fi
        sleep 5
      done ) &
    SPOT_WATCHER_PID=$!
}
start_spot_watcher

# ── Background disk-usage sampler ─────────────────────────────────────────────
touch $LOG/disk_monitor_running
( while [ -f $LOG/disk_monitor_running ]; do
    df $D | tail -1 | awk '{print $3}' >> $LOG/disk_usage_samples.log 2>/dev/null || true
    sleep 30
  done ) &

# ══════════════════════════════════════════════════════════════════════════════
# PHASE rlbwt: agc -> prepare -> concat -> grlBWT -> rle -> adapter
# Captures the ~3.5-day grlBWT in ~50 GB of O(r) artifacts; never repeated after success.
# Pre-grlBWT steps run from the 3 GB agc, so a resume needs no multi-TB S3 transfer.
# ══════════════════════════════════════════════════════════════════════════════
if phase_done rlbwt; then
    echo "[rlbwt] cached — pulling RLBWT artifacts from S3"
    $AWS s3 sync "$S3_WORK/ckpt/rlbwt/" $D/ --only-show-errors
else
    make_clean_ref                                        # -> $D/clean.fa

    # concat (Snakefile rule `concat`): %-separated single string;
    # trailing newline is the grlBWT sentinel.
    { grep -v '^>' $D/clean.fa | tr -d '\n'; echo; } > $D/grl_in.txt
    rm -f $D/clean.fa

    /usr/bin/time -v $GRLBWT $D/grl_in.txt -o $D/grl_out -t $(nproc) -T $D/grltmp \
        > $LOG/grlbwt.stdout 2> $LOG/grlbwt.stderr
    rm -rf $D/grltmp $D/grl_in.txt

    $GRL2RLE $D/grl_out.rl_bwt $D/grl_rle           # -> grl_rle.syms, grl_rle.len

    # adapter twice (Snakefile adapter_teralcp + adapter_movi):
    #   plain           -> $D/grl.bwt.heads/len      (TeraLCP -f rlbwt input)
    #   --movi-sentinel -> $D/ref.fa.bwt.heads/len   (Movi build BWT)
    $ADAPTER $D/grl_rle $D/grl -q
    $ADAPTER $D/grl_rle $D/ref.fa --movi-sentinel -q
    rm -f $D/grl_out.rl_bwt $D/grl_rle.*

    $AWS s3 sync $D/ "$S3_WORK/ckpt/rlbwt/" --only-show-errors \
        --exclude "*" --include "grl.bwt.*" --include "ref.fa.bwt.*"
    mark_done rlbwt
fi

# ══════════════════════════════════════════════════════════════════════════════
# PHASE construct: TeraLCP build (checkpointed). The long pole (~8.5 d for yr2).
# -checkpoint makes it resumable; the syncer + spot watcher protect it from reclaim.
# ══════════════════════════════════════════════════════════════════════════════
if phase_done construct; then
    echo "[construct] cached — pulling lcp_index from S3"
    $AWS s3 cp "$S3_WORK/ckpt/teralcp.lcp_index" $D/teralcp.lcp_index
else
    $AWS s3 sync "$S3_WORK/ckpt/teralcp.ckpt/" $D/teralcp.ckpt/ --only-show-errors || true
    start_ckpt_syncer
    /usr/bin/time -v $TERALCP -f rlbwt -i $D/grl -checkpoint $D/teralcp.ckpt \
        -t $D/teralcp.construct.tmp -oindex $D/teralcp -p $TERALCP_P -v time \
        > $LOG/construct.stdout 2> $LOG/construct.stderr
    rm -f $D/teralcp.construct.tmp
    $AWS s3 cp $D/teralcp.lcp_index "$S3_WORK/ckpt/teralcp.lcp_index"
    mark_done construct
    # checkpoint dir no longer needed; stop syncer + clear S3 copy
    rm -rf $D/teralcp.ckpt
    $AWS s3 rm "$S3_WORK/ckpt/teralcp.ckpt/" --recursive --only-show-errors || true
fi

# ══════════════════════════════════════════════════════════════════════════════
# PHASE thresholds: TeraLCP thresholds from the lcp_index.
# ══════════════════════════════════════════════════════════════════════════════
if phase_done thresholds; then
    echo "[thresholds] cached — pulling from S3"
    $AWS s3 sync "$S3_WORK/ckpt/thr/" $D/ --only-show-errors
else
    /usr/bin/time -v $TERALCP -f lcp_index -i $D/teralcp \
        -othresholds $D/septera --rlbwt-meta $D/grl -p $TERALCP_P -v time \
        > $LOG/thresholds.stdout 2> $LOG/thresholds.stderr
    $AWS s3 sync $D/ "$S3_WORK/ckpt/thr/" --only-show-errors \
        --exclude "*" --include "septera.thr" --include "septera.thr_pos"
    mark_done thresholds
fi

# ══════════════════════════════════════════════════════════════════════════════
# PHASE movi: stage thresholds, build the Movi index + ftabs, upload to OUTPUT.
# ══════════════════════════════════════════════════════════════════════════════
if ! phase_done movi; then
    OUT=$D/index
    mkdir -p $OUT
    # Assemble the index dir from the checkpointed artifacts (already in $D):
    cp $D/ref.fa.bwt.heads $D/ref.fa.bwt.len $OUT/
    cp $D/septera.thr      $OUT/ref.fa.thr
    cp $D/septera.thr_pos  $OUT/ref.fa.thr_pos
    # movi build needs the cleaned reference FASTA (Snakefile stages clean.fa as ref.fa).
    # Regenerate it from AGC if this (possibly fresh) instance doesn't have it.
    make_clean_ref
    cp $D/clean.fa $OUT/ref.fa

    # movi build (Snakefile rule movi_build): also writes ftab.$FTAB_K.bin
    /usr/bin/time -v $MOVI build --separators --preprocessed --skip-prepare --skip-pfp \
        --type regular-thresholds --ftab-k $FTAB_K \
        --fasta $OUT/ref.fa --index $OUT \
        > $LOG/movi_build.stdout 2> $LOG/movi_build.stderr
    test -s $OUT/index.movi

    # Extra ftabs (k != FTAB_K) for the finished index (Snakefile rule ftab)
    for k in $FTAB_EXTRA_KS; do
        /usr/bin/time -v $MOVI ftab --index $OUT --ftab-k $k \
            >> $LOG/ftab.stdout 2>> $LOG/ftab.stderr
    done

    $AWS s3 sync $OUT/ "$S3_OUT/index/" --only-show-errors
    mark_done movi
fi

# ── Finalize: logs, summary, mark complete, stop billing ──────────────────────
rm -f $LOG/disk_monitor_running
PEAK_DISK_KB=$(sort -n $LOG/disk_usage_samples.log 2>/dev/null | tail -1 | tr -d ' ')
cat > $LOG/summary.txt << SUMEOF
Collection: $COLLECTION
Instance: $(curl -s -H "X-aws-ec2-metadata-token: $(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 60')" http://169.254.169.254/latest/meta-data/instance-type)
Finished: $(date -u)
Peak disk usage (kB, sampled): $PEAK_DISK_KB
Output: $S3_OUT/index/
SUMEOF
$AWS s3 sync $LOG/ "$S3_OUT/logs/" --only-show-errors
mark_done complete
scale_down
echo "MOVI INDEX BUILD COMPLETE"
"""
