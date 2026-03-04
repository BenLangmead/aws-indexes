"""
Stack for running TeraLCP on the OpenHGL human579 FMD dataset.

Provisions a spot instance (type and region from config.json), builds
TeraTools from source, runs TeraLCP with full resource monitoring, and
uploads results to S3. Default: m7gd.metal in ap-northeast-2 at $1.00/hr.

Design notes vs pfp_thresh_builder:
  - Fixes gcc-c++ package name (not g++)
  - Fixes user-data line joining (uses newlines throughout, no ' '.join())
  - Spot price stored as string in config.json (avoids CDK float->string issue)
  - NVMe instance stores discovered and striped into RAID 0 at /data
  - Job script written to /home/ec2-user/job.sh and run as ec2-user,
    avoiding inline heredoc termination issues
  - Full monitoring: psrecord, /usr/bin/time -v, background disk sampler
  - All outputs and logs uploaded to dated S3 prefix on completion

Author: Ben Langmead
"""

import configparser
import os
import base64
import json

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput,
    CfnTag,
)

from constructs import Construct


class TeraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load deployment configuration
        with open('config.json', 'r') as f:
            cfg = json.load(f)

        # Prefer AZs that commonly have capacity first; fall back to cheaper AZs (e.g. 1f)
        preferred_azs = cfg.get(
            "preferred_availability_zones",
            [cfg["availability_zone"]],
        )
        key_name = cfg['key_name']
        instance_size = 'large' if cfg['use_large_instance'] else 'small'
        inst_cfg = cfg['instance_type'][instance_size]

        # ── Networking ────────────────────────────────────────────────────────
        # Use enough AZs so the configured AZ (e.g. ap-northeast-2a) is included
        vpc = ec2.Vpc(
            self,
            "TeraVpc",
            max_azs=6,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="tera-public-subnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
        )

        sec_group = ec2.SecurityGroup(
            self, "TeraSecurityGroup", vpc=vpc, allow_all_outbound=True
        )
        sec_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH access"
        )

        # ── Key pair ─────────────────────────────────────────────────────────
        cfn_key_pair = ec2.CfnKeyPair(
            self,
            "TeraKeyPair",
            key_name=key_name,
            tags=[CfnTag(key="application", value="tera-build")],
        )
        key_pair_ref = ec2.KeyPair.from_key_pair_name(
            self, "TeraKeyPairRef", key_pair_name=cfn_key_pair.key_name
        )

        # ── AMI: match instance architecture (ARM64 vs x86_64) ─────────────────
        instance_type_str = inst_cfg["type"].lower()
        is_arm = instance_type_str.startswith("a1.") or "g" in instance_type_str.split(".")[0]
        machine_image = (
            ec2.MachineImage.latest_amazon_linux2023(cpu_type=ec2.AmazonLinuxCpuType.ARM_64)
            if is_arm
            else ec2.MachineImage.latest_amazon_linux2023(cpu_type=ec2.AmazonLinuxCpuType.X86_64)
        )

        # ── Launch template ───────────────────────────────────────────────────
        # Note: You will see one EBS (gp3) volume on the instance. That is the root volume
        # created by default from the AMI; it is required for the OS. Instance store is used for /data.
        launch_template = ec2.LaunchTemplate(
            self,
            "TeraLaunchTemplate",
            instance_type=ec2.InstanceType(inst_cfg['type']),
            machine_image=machine_image,
            security_group=sec_group,
            key_pair=key_pair_ref,
            spot_options=ec2.LaunchTemplateSpotOptions(
                max_price=float(inst_cfg['spot_price'])
            ),
        )
        launch_template.node.add_dependency(cfn_key_pair)

        # ── AWS credentials (read at synth time, embedded in user data) ───────
        aws_creds = configparser.ConfigParser()
        aws_creds.read(os.path.expanduser('~/.aws/credentials'))
        aws_access_key_id = aws_creds['data-langmead']['aws_access_key_id']
        aws_secret_access_key = aws_creds['data-langmead']['aws_secret_access_key']

        # ── User data ─────────────────────────────────────────────────────────
        #
        # Structure:
        #   1. Root section: package install, NVMe RAID-0 mount, credential
        #      provisioning, Python tool install, write job.sh, execute job.sh
        #   2. job.sh (runs as ec2-user): build TeraTools, download FMD,
        #      run TeraLCP under psrecord+time, collect metrics, upload to S3
        #
        # The job.sh is written into the user data via a heredoc
        # (<< 'JOBEOF') so that all bash variable expansions in job.sh
        # happen at job run time, not at write time.  The outer user data
        # uses '\n'.join() throughout to ensure proper line separation.

        # ── job.sh content (runs as ec2-user) ─────────────────────────────────
        job_lines = [
            "#!/bin/bash",
            "set -x",
            "",
            "LOG_DIR=/data/logs",
            "OUT_DIR=/data/output",
            "TMP_DIR=/data/tmp",
            "mkdir -p $LOG_DIR $OUT_DIR $TMP_DIR",
            "",
            "# ── OS and tool info ─────────────────────────────────────────",
            "cat /etc/os-release > $LOG_DIR/os_info.txt",
            "echo '---' >> $LOG_DIR/os_info.txt",
            "g++ --version >> $LOG_DIR/os_info.txt 2>&1",
            "cmake --version >> $LOG_DIR/os_info.txt 2>&1",
            "python3 --version >> $LOG_DIR/os_info.txt 2>&1",
            "",
            "# ── Clone and build TeraTools ────────────────────────────────",
            "cd /home/ec2-user",
            "git clone -b sdsl-integrate https://github.com/BenLangmead/TeraTools.git",
            "cd TeraTools",
            "git submodule update --init --recursive",
            "make -j$(nproc)",
            "cd /home/ec2-user",
            "",
            "TERALCP=/home/ec2-user/TeraTools/src/TeraLCP/TeraLCP",
            "",
            "# Record TeraLCP help/version",
            "$TERALCP --help > $LOG_DIR/teralcp_help.txt 2>&1 || true",
            "",
            "# ── Download input FMD ───────────────────────────────────────",
            "aws s3 --profile data-langmead cp \\",
            "    s3://openhgl/human/human579/human579.fmd /data/",
            "",
            "# ── Background disk usage monitor ────────────────────────────",
            "touch $LOG_DIR/disk_monitor_running",
            "(",
            "  while [ -f $LOG_DIR/disk_monitor_running ]; do",
            "    df /data | tail -1 | awk '{print $3}' >> $LOG_DIR/disk_usage_samples.log 2>/dev/null || true",
            "    sleep 30",
            "  done",
            ") &",
            "DISK_MONITOR_PID=$!",
            "",
            "# ── Run TeraLCP under psrecord and /usr/bin/time ─────────────",
            "# Pass one argument to psrecord (bash -c '...') so it does not parse TeraLCP flags (-v, -f, etc.)",
            "TERA_CMD=\"bash -c \\\"/usr/bin/time -v $TERALCP -f fmd -i /data/human579.fmd -v verb -oindex $OUT_DIR/human579 -orlcp $OUT_DIR/human579.rlcp -t $TMP_DIR/teratools.tmp -otsv $OUT_DIR/human579 -tsvmode thresholds > $LOG_DIR/tera_stdout.log 2> $LOG_DIR/tera_stderr.log\\\"\"",
            "psrecord \\",
            "    --log $LOG_DIR/tera_resource_usage.log \\",
            "    --interval 15 \\",
            "    --plot $LOG_DIR/tera_resource_plot.png \\",
            "    --include-children \\",
            "    -- \"$TERA_CMD\"",
            "",
            "# ── Stop disk monitor ────────────────────────────────────────",
            "rm -f $LOG_DIR/disk_monitor_running",
            "wait $DISK_MONITOR_PID 2>/dev/null || true",
            "",
            "# ── Extract measurements ──────────────────────────────────────",
            "#  Wall clock time and RSS from /usr/bin/time -v (in tera_stderr.log)",
            "WALL_CLOCK=$(grep 'Elapsed (wall clock) time' $LOG_DIR/tera_stderr.log \\",
            "             | awk '{print $NF}' || echo 'N/A')",
            "MAX_RSS_KB=$(grep 'Maximum resident set size' $LOG_DIR/tera_stderr.log \\",
            "             | awk '{print $NF}' || echo 'N/A')",
            "",
            "#  Peak RSS (MB) and peak virtual memory (MB) from psrecord log",
            "#  psrecord log columns: elapsed_sec  cpu_pct  rss_mb  virt_mb",
            "MAX_RSS_MB=$(awk 'NR>1 && NF>=3 {v=$3+0; if(v>m) m=v} END {print (m>0?m:\"N/A\")}' \\",
            "             $LOG_DIR/tera_resource_usage.log || echo 'N/A')",
            "MAX_VIRT_MB=$(awk 'NR>1 && NF>=4 {v=$4+0; if(v>m) m=v} END {print (m>0?m:\"N/A\")}' \\",
            "              $LOG_DIR/tera_resource_usage.log || echo 'N/A')",
            "",
            "#  Peak disk usage (KB) from sampled df output",
            "PEAK_DISK_KB=$(sort -n $LOG_DIR/disk_usage_samples.log 2>/dev/null \\",
            "               | tail -1 | tr -d ' ' || echo 'N/A')",
            "",
            "OUTPUT_DATE=$(date +%Y%m%d)",
            "",
            "# ── Write summary file ───────────────────────────────────────",
            "# If TeraLCP/psrecord failed, capture tera_stderr.log tail so we see the error",
            "TERA_STDERR_TAIL=''",
            "if [ -s $LOG_DIR/tera_stderr.log ]; then",
            "  TERA_STDERR_TAIL=\"$(tail -50 $LOG_DIR/tera_stderr.log | sed 's/^/  /')\"",
            "else",
            "  TERA_STDERR_TAIL='  (file missing or empty - TeraLCP may not have run; check spot termination)'",
            "fi",
            "cat > $LOG_DIR/summary.txt << SUMEOF",
            "Run Date: $(date -u)",
            f"Instance Type: {inst_cfg['type']}",
            "Input: s3://openhgl/human/human579/human579.fmd",
            "Output S3 prefix: s3://genome-idx/movi/tera-openhgl/${OUTPUT_DATE}/",
            "---",
            "Wall Clock Time: $WALL_CLOCK",
            "Peak RSS, kB (from /usr/bin/time -v): $MAX_RSS_KB",
            "Peak RSS, MB (from psrecord): $MAX_RSS_MB",
            "Peak Virtual Memory, MB (from psrecord): $MAX_VIRT_MB",
            "Peak Disk Usage, kB (sampled every 30s): $PEAK_DISK_KB",
            "---",
            "Last 50 lines of tera_stderr.log (if run failed, error appears here):",
            "$TERA_STDERR_TAIL",
            "SUMEOF",
            "",
            "# ── Create TeraTools tarball ─────────────────────────────────",
            "tar czf /data/TeraTools.tar.gz -C /home/ec2-user TeraTools/",
            "",
            "# ── Upload everything to S3 ──────────────────────────────────",
            "# output/ includes index, rlcp, and -otsv outputs (human579.thr, human579.thr_pos)",
            "S3_BASE=s3://genome-idx/movi/tera-openhgl/${OUTPUT_DATE}",
            "aws s3 --profile data-langmead sync $OUT_DIR/   ${S3_BASE}/output/",
            "aws s3 --profile data-langmead sync $LOG_DIR/   ${S3_BASE}/logs/",
            "aws s3 --profile data-langmead cp /data/TeraTools.tar.gz ${S3_BASE}/",
        ]

        # ── Root user data section ─────────────────────────────────────────────
        root_lines = [
            "#!/bin/bash",
            "set -x",
            "",
            "# ── System packages ──────────────────────────────────────────",
            "dnf update -y",
            "dnf install -y make gcc gcc-c++ git cmake zlib-devel mdadm python3-pip time libatomic",
            "",
            "# ── Mount NVMe instance store(s) as RAID-0 at /data ──────────",
            "# Exclude the root device (EBS); use only instance-store NVMe devices.",
            "ROOT_DEV=$(findmnt -n -o SOURCE / | sed 's/p[0-9]*$//' | xargs -I {} basename {})",
            "NVME_STORES=''",
            "for dev in /dev/nvme0n1 /dev/nvme1n1 /dev/nvme2n1 /dev/nvme3n1 /dev/nvme4n1; do",
            "    [ -b \"$dev\" ] || continue",
            "    devname=$(basename \"$dev\")",
            "    [ \"$devname\" = \"$ROOT_DEV\" ] && continue",
            "    NVME_STORES=\"$NVME_STORES $dev\"",
            "done",
            "NVME_COUNT=$(echo $NVME_STORES | wc -w)",
            "mkdir -p /data",
            "if [ \"$NVME_COUNT\" -ge 2 ]; then",
            "    mdadm --create --verbose /dev/md0 --level=0 \\",
            "          --raid-devices=$NVME_COUNT $NVME_STORES",
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
            "# ── AWS credentials ───────────────────────────────────────────",
            "mkdir -p /home/ec2-user/.aws",
            "cat > /home/ec2-user/.aws/credentials << 'EOL'",
            "[data-langmead]",
            f"aws_access_key_id = {aws_access_key_id}",
            f"aws_secret_access_key = {aws_secret_access_key}",
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
            "# ── Execute job as ec2-user ───────────────────────────────────",
            "su - ec2-user -c '/home/ec2-user/job.sh'",
        ]

        user_data_script = '\n'.join(root_lines)

        # ── Subnet selection: first preferred AZ that has a subnet (improves capacity likelihood) ─
        vpc_azs = {s.availability_zone for s in vpc.public_subnets}
        az = None
        selected_subnet = None
        for preferred in preferred_azs:
            if preferred in vpc_azs:
                selected_subnet = next(
                    s for s in vpc.public_subnets if s.availability_zone == preferred
                )
                az = preferred
                break
        if selected_subnet is None:
            # CDK may expose dummy AZs (dummy1a, dummy1b, ...) when region AZs aren't resolved yet at synth time
            if all(zone.startswith("dummy") for zone in vpc_azs):
                selected_subnet = vpc.public_subnets[0]
                az = selected_subnet.availability_zone
            else:
                available = sorted(vpc_azs)
                raise ValueError(
                    f"No subnet for any preferred AZ {preferred_azs}. "
                    f"VPC has subnets in: {available}. Ensure config region and max_azs are correct."
                )

        # ── EC2 instance ──────────────────────────────────────────────────────
        instance = ec2.CfnInstance(
            self, "TeraInstance",
            launch_template=ec2.CfnInstance.LaunchTemplateSpecificationProperty(
                launch_template_id=launch_template.launch_template_id,
                version=launch_template.latest_version_number
            ),
            availability_zone=az,
            subnet_id=selected_subnet.subnet_id,
            user_data=base64.b64encode(user_data_script.encode()).decode(),
            tags=[CfnTag(key="application", value="tera-build")]
        )

        # ── Outputs ───────────────────────────────────────────────────────────
        CfnOutput(self, "KeyPairId", value=cfn_key_pair.attr_key_pair_id,
                  description="id of the tera-build key pair",
                  export_name="tera-keypair-id")

        CfnOutput(self, "PublicIp", value=instance.attr_public_ip,
                  description="public IP of the tera instance",
                  export_name="tera-public-ip")
