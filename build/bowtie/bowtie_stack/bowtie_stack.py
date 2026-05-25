"""
CDK stack for building Bowtie 2 indexes for Index Zone.

The stack provisions one EC2 spot instance, builds Bowtie 2 from source, runs
build_indexes.bash over selected rows from targets.tsv, and uploads index
artifacts plus logs to S3.
"""

import base64
import gzip
import json
import re
import shlex
import subprocess
from pathlib import Path

from aws_cdk import (
    CfnOutput,
    CfnTag,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct


def _shell_quote(value: str) -> str:
    return shlex.quote(str(value))


def _safe_run_id_component(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "run"


def _builder_id(root: Path) -> str:
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--short=12", "HEAD"],
            text=True,
        ).strip()
        status = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain", "--", str(root)],
            text=True,
        )
        suffix = "+dirty" if status.strip() else ""
        return f"aws-indexes:{commit}{suffix}"
    except (OSError, subprocess.CalledProcessError):
        return "aws-indexes:unknown"


def _heredoc(path: str, marker: str, content: str, mode: str = "0644") -> list[str]:
    return [
        f"cat > {path} << '{marker}'",
        content.rstrip("\n"),
        marker,
        f"chmod {mode} {path}",
    ]


def _gzip_b64_file(path: str, marker: str, content: str, mode: str = "0644") -> list[str]:
    encoded = base64.b64encode(gzip.compress(content.encode())).decode()
    wrapped = "\n".join(encoded[i:i + 76] for i in range(0, len(encoded), 76))
    tmp = f"/tmp/{Path(path).name}.gz.b64"
    return [
        f"cat > {tmp} << '{marker}'",
        wrapped,
        marker,
        f"base64 -d {tmp} | gzip -d > {path}",
        f"chmod {mode} {path}",
    ]


def _s3_bucket_arn(s3_uri: str) -> str:
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"expected S3 URI, got {s3_uri!r}")
    bucket = s3_uri[5:].split("/", 1)[0]
    if not bucket:
        raise ValueError(f"expected S3 URI with bucket, got {s3_uri!r}")
    return f"arn:aws:s3:::{bucket}"


def _s3_objects_arn(s3_uri: str) -> str:
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"expected S3 URI, got {s3_uri!r}")
    rest = s3_uri[5:]
    bucket, _, prefix = rest.partition("/")
    if not bucket:
        raise ValueError(f"expected S3 URI with bucket, got {s3_uri!r}")
    if prefix:
        return f"arn:aws:s3:::{bucket}/{prefix.rstrip('/')}/*"
    return f"arn:aws:s3:::{bucket}/*"


class BowtieStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        root = Path(__file__).resolve().parents[1]
        with open(root / "config.json", "r") as f:
            cfg = json.load(f)

        instance_profile = cfg.get("instance_profile")
        if not instance_profile:
            raise ValueError('config.json must set "instance_profile"')
        instance_defs = cfg.get("instance_type") or {}
        if instance_profile not in instance_defs:
            raise ValueError(
                f"config.json instance_profile {instance_profile!r} is not a key "
                f"under instance_type. Available: {sorted(instance_defs)}"
            )
        inst_cfg = instance_defs[instance_profile]
        for key in ("region", "availability_zone", "type", "spot_price"):
            if key not in inst_cfg:
                raise ValueError(
                    f"config.json instance_type.{instance_profile} is missing {key!r}"
                )

        preferred_azs = inst_cfg.get(
            "preferred_availability_zones", [inst_cfg["availability_zone"]]
        )
        key_name = cfg.get("key_name", "bowtie-build")
        instance_role_name = cfg.get(
            "instance_role_name", "index-zone-bowtie-builder-role"
        )
        launch_instance = bool(cfg.get("launch_instance", True))
        volume_gb = int(cfg.get("volume_gb", 1000))
        volume_iops = int(cfg.get("volume_iops", 12000))
        volume_throughput = int(cfg.get("volume_throughput", 500))
        output_s3_prefix = (cfg.get("output_s3_prefix") or "s3://bt2-bench/indexes").rstrip("/")
        log_s3_prefix = (cfg.get("log_s3_prefix") or "s3://genome-idx/bt/build-logs").rstrip("/")
        upload_outputs = bool(cfg.get("upload_outputs", True))
        targets_file = cfg.get("targets_file", "targets.tsv")
        build_script = cfg.get("build_script", "build_indexes.bash")
        target_ids = cfg.get("target_ids", [])
        if target_ids is None:
            target_ids = []
        if not isinstance(target_ids, list):
            raise ValueError('config.json "target_ids" must be a list, or empty for all targets')
        bowtie2_repo = cfg.get("bowtie2_repo", "https://github.com/BenLangmead/bowtie2.git")
        bowtie2_ref = cfg.get("bowtie2_ref", "master")
        upload_profile = cfg.get("upload_profile", "data-langmead")
        upload_role_arn = (cfg.get("upload_role_arn") or "").strip()
        builder_id = cfg.get("builder_id") or _builder_id(root)

        build_script_text = (root / build_script).read_text()
        targets_text = (root / targets_file).read_text()

        # Networking
        vpc = ec2.Vpc(
            self,
            "BowtieVpc",
            max_azs=6,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="bowtie-public-subnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
        )

        security_group = ec2.SecurityGroup(
            self, "BowtieSecurityGroup", vpc=vpc, allow_all_outbound=True
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH access"
        )

        cfn_key_pair = ec2.CfnKeyPair(
            self,
            "BowtieKeyPair",
            key_name=key_name,
            tags=[CfnTag(key="application", value="bowtie-build")],
        )
        key_pair_ref = ec2.KeyPair.from_key_pair_name(
            self, "BowtieKeyPairRef", key_pair_name=cfn_key_pair.key_name
        )

        instance_role = iam.Role(
            self,
            "BowtieInstanceRole",
            role_name=instance_role_name,
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        if upload_role_arn:
            instance_role.add_to_policy(
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    resources=[upload_role_arn],
                )
            )
        else:
            instance_role.add_to_policy(
                iam.PolicyStatement(
                    actions=[
                        "s3:ListBucket",
                        "s3:GetBucketLocation",
                    ],
                    resources=[
                        _s3_bucket_arn(output_s3_prefix),
                        _s3_bucket_arn(log_s3_prefix),
                    ],
                )
            )
            instance_role.add_to_policy(
                iam.PolicyStatement(
                    actions=[
                        "s3:AbortMultipartUpload",
                        "s3:GetObject",
                        "s3:ListMultipartUploadParts",
                        "s3:PutObject",
                    ],
                    resources=[
                        _s3_objects_arn(output_s3_prefix),
                        _s3_objects_arn(log_s3_prefix),
                    ],
                )
            )

        arch = ec2.InstanceType(inst_cfg["type"]).architecture
        machine_image = (
            ec2.MachineImage.latest_amazon_linux2023(
                cpu_type=ec2.AmazonLinuxCpuType.ARM_64
            )
            if arch == ec2.InstanceArchitecture.ARM_64
            else ec2.MachineImage.latest_amazon_linux2023(
                cpu_type=ec2.AmazonLinuxCpuType.X86_64
            )
        )

        launch_template = ec2.LaunchTemplate(
            self,
            "BowtieLaunchTemplate",
            instance_type=ec2.InstanceType(inst_cfg["type"]),
            machine_image=machine_image,
            security_group=security_group,
            key_pair=key_pair_ref,
            role=instance_role,
            spot_options=ec2.LaunchTemplateSpotOptions(
                max_price=float(inst_cfg["spot_price"])
            ),
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_gb,
                        volume_type=ec2.EbsDeviceVolumeType.GP3,
                        iops=volume_iops,
                        throughput=volume_throughput,
                    ),
                )
            ],
        )
        launch_template.node.add_dependency(cfn_key_pair)

        run_id_targets = _safe_run_id_component("-".join(target_ids) if target_ids else "all")

        threads_cfg = cfg.get("threads", "$(nproc)")
        threads_assignment = (
            "THREADS=$(nproc)"
            if threads_cfg in ("", "$(nproc)")
            else f"THREADS={_shell_quote(threads_cfg)}"
        )
        run_build_lines = [
            "#!/bin/bash",
            "set -u",
            "set -o pipefail",
            "export PATH=/home/ec2-user/bowtie2:$PATH",
            f"export INDEX_ZONE_BUILDER={_shell_quote(builder_id)}",
            *([f"export AWS_PROFILE={_shell_quote(upload_profile)}"] if upload_role_arn else []),
            threads_assignment,
            "cmd=(",
            "  /home/ec2-user/build_indexes.bash",
            "  --targets /home/ec2-user/targets.tsv",
            "  --out-dir /data/output",
            "  --work-dir /data/work",
            "  --threads \"$THREADS\"",
            ")",
        ]
        if upload_outputs:
            run_build_lines.append(f"cmd+=(--upload-prefix {_shell_quote(output_s3_prefix)})")
        for target_id in target_ids:
            run_build_lines.append(f"cmd+=({_shell_quote(target_id)})")
        run_build_lines.append('"${cmd[@]}"')

        aws_profile_export = (
            f"export AWS_PROFILE={_shell_quote(upload_profile)}"
            if upload_role_arn
            else "# upload_role_arn not set; using the EC2 instance role directly"
        )
        aws_s3_cmd = (
            f"AWS_PROFILE={_shell_quote(upload_profile)} aws"
            if upload_role_arn
            else "aws"
        )
        job_lines = [
            "#!/bin/bash",
            "set -u",
            "set -o pipefail",
            "",
            f"BOWTIE2_REPO={_shell_quote(bowtie2_repo)}",
            f"BOWTIE2_REF={_shell_quote(bowtie2_ref)}",
            f"LOG_S3_PREFIX={_shell_quote(log_s3_prefix)}",
            f"OUTPUT_S3_PREFIX={_shell_quote(output_s3_prefix)}",
            aws_profile_export,
            f"UPLOAD_OUTPUTS={1 if upload_outputs else 0}",
            f"RUN_ID=$(date -u +%Y%m%d-%H%M%S)-{run_id_targets}",
            "LOG_DIR=/data/logs",
            "OUT_DIR=/data/output",
            "WORK_DIR=/data/work",
            "mkdir -p $LOG_DIR $OUT_DIR $WORK_DIR",
            "",
            "cat /etc/os-release > $LOG_DIR/os_info.txt",
            "echo '---' >> $LOG_DIR/os_info.txt",
            "df -h / /data > $LOG_DIR/disk_start.txt 2>&1 || true",
            "python3 --version > $LOG_DIR/python_version.txt 2>&1 || true",
            "aws --version > $LOG_DIR/aws_version.txt 2>&1 || true",
            "samtools --version > $LOG_DIR/samtools_version.txt 2>&1 || true",
            "",
            "cd /home/ec2-user",
            "git clone --depth 1 --branch \"$BOWTIE2_REF\" \"$BOWTIE2_REPO\" bowtie2",
            "make -C bowtie2 -j$(nproc)",
            "/home/ec2-user/bowtie2/bowtie2-build --version > $LOG_DIR/bowtie2_build_version.txt 2>&1 || true",
            "",
            "cat > /home/ec2-user/run_build.sh << 'RUNEOF'",
            *run_build_lines,
            "RUNEOF",
            "chmod +x /home/ec2-user/run_build.sh",
            "",
            "touch $LOG_DIR/disk_monitor_running",
            "(",
            "  while [ -f $LOG_DIR/disk_monitor_running ]; do",
            "    date -u +%Y-%m-%dT%H:%M:%SZ >> $LOG_DIR/disk_usage_samples.log",
            "    df -k /data >> $LOG_DIR/disk_usage_samples.log 2>/dev/null || true",
            "    sleep 30",
            "  done",
            ") &",
            "DISK_MONITOR_PID=$!",
            "",
            "BUILD_STATUS=0",
            "/usr/bin/time -v /home/ec2-user/run_build.sh \\",
            "  > $LOG_DIR/build_stdout.log \\",
            "  2> $LOG_DIR/build_stderr.log || BUILD_STATUS=$?",
            "",
            "rm -f $LOG_DIR/disk_monitor_running",
            "wait $DISK_MONITOR_PID 2>/dev/null || true",
            "",
            "WALL_CLOCK=$(grep 'Elapsed (wall clock) time' $LOG_DIR/build_stderr.log | awk '{print $NF}' || echo 'N/A')",
            "MAX_RSS_KB=$(grep 'Maximum resident set size' $LOG_DIR/build_stderr.log | awk '{print $NF}' || echo 'N/A')",
            "MAX_RSS_MB=N/A",
            "MAX_VIRT_MB=N/A",
            "OUTPUT_COUNT=$(find $OUT_DIR -maxdepth 1 -type f | wc -l)",
            "cat > $LOG_DIR/summary.txt << SUMEOF",
            "Run Date: $(date -u)",
            f"Instance Type: {inst_cfg['type']}",
            f"Instance profile: {instance_profile}",
            "Run ID: $RUN_ID",
            f"Target IDs: {' '.join(target_ids) if target_ids else 'all'}",
            f"Builder: {builder_id}",
            "Upload outputs: $UPLOAD_OUTPUTS",
            "Output S3 prefix: $OUTPUT_S3_PREFIX",
            "Log S3 prefix: $LOG_S3_PREFIX/$RUN_ID/",
            "---",
            "Build status: $BUILD_STATUS",
            "Wall Clock Time: $WALL_CLOCK",
            "Peak RSS, kB (from /usr/bin/time -v): $MAX_RSS_KB",
            "Peak RSS, MB (external sampler): $MAX_RSS_MB",
            "Peak Virtual Memory, MB (external sampler): $MAX_VIRT_MB",
            "Output file count: $OUTPUT_COUNT",
            "SUMEOF",
            "",
            f"{aws_s3_cmd} s3 sync $LOG_DIR ${{LOG_S3_PREFIX}}/${{RUN_ID}}/logs/ || true",
            "if [ \"$UPLOAD_OUTPUTS\" = \"0\" ]; then",
            f"  {aws_s3_cmd} s3 sync $OUT_DIR ${{LOG_S3_PREFIX}}/${{RUN_ID}}/output/ || true",
            "fi",
            "exit $BUILD_STATUS",
        ]

        aws_config_lines = [
            "cat > /home/ec2-user/.aws/config << 'EOL'",
            f"[profile {upload_profile}]",
            f"region = {inst_cfg['region']}",
        ]
        if upload_role_arn:
            aws_config_lines += [
                f"role_arn = {upload_role_arn}",
                "credential_source = Ec2InstanceMetadata",
            ]
        else:
            aws_config_lines += [
                "# No upload_role_arn configured; AWS CLI will use the instance role directly.",
            ]
        aws_config_lines += [
            "EOL",
            "chmod 600 /home/ec2-user/.aws/config",
        ]

        root_lines = [
            "#!/bin/bash",
            "set -x",
            "dnf update -y",
            "dnf install -y --allowerasing make gcc gcc-c++ git zlib-devel zip gzip tar curl python3-pip time procps-ng bzip2 bzip2-devel xz-devel ncurses-devel openssl-devel libcurl-devel",
            "dnf install -y samtools || true",
            "if ! command -v aws >/dev/null 2>&1; then dnf install -y awscli || dnf install -y awscli-2 || python3 -m pip install awscli; fi",
            "if ! command -v samtools >/dev/null 2>&1; then",
            "  cd /opt",
            "  curl -L -o htslib.tar.bz2 https://github.com/samtools/htslib/releases/download/1.22/htslib-1.22.tar.bz2",
            "  tar -xjf htslib.tar.bz2",
            "  make -C htslib-1.22 -j$(nproc)",
            "  curl -L -o samtools.tar.bz2 https://github.com/samtools/samtools/releases/download/1.22/samtools-1.22.tar.bz2",
            "  tar -xjf samtools.tar.bz2",
            "  make -C samtools-1.22 -j$(nproc) HTSDIR=/opt/htslib-1.22",
            "  install -m 0755 samtools-1.22/samtools /usr/local/bin/samtools",
            "fi",
            "mkdir -p /data /home/ec2-user/.aws",
            "chown ec2-user:ec2-user /data",
            *aws_config_lines,
            "chown -R ec2-user:ec2-user /home/ec2-user/.aws",
            * _gzip_b64_file("/home/ec2-user/build_indexes.bash", "BUILDINDEXESEOF", build_script_text, "0755"),
            * _gzip_b64_file("/home/ec2-user/targets.tsv", "TARGETSTSVEOF", targets_text),
            * _heredoc("/home/ec2-user/job.sh", "JOBEOF", "\n".join(job_lines), "0755"),
            "chown ec2-user:ec2-user /home/ec2-user/build_indexes.bash /home/ec2-user/targets.tsv /home/ec2-user/job.sh",
            "su - ec2-user -c '/home/ec2-user/job.sh'",
        ]
        user_data_script = "\n".join(root_lines)

        vpc_azs = {s.availability_zone for s in vpc.public_subnets}
        selected_subnet = None
        selected_az = None
        for preferred in preferred_azs:
            if preferred in vpc_azs:
                selected_subnet = next(
                    s for s in vpc.public_subnets if s.availability_zone == preferred
                )
                selected_az = preferred
                break
        if selected_subnet is None:
            if all(zone.startswith("dummy") for zone in vpc_azs):
                selected_subnet = vpc.public_subnets[0]
                selected_az = selected_subnet.availability_zone
            else:
                raise ValueError(
                    f"No subnet for preferred AZs {preferred_azs}; available: {sorted(vpc_azs)}"
                )

        instance = None
        if launch_instance:
            instance = ec2.CfnInstance(
                self,
                "BowtieInstance",
                launch_template=ec2.CfnInstance.LaunchTemplateSpecificationProperty(
                    launch_template_id=launch_template.launch_template_id,
                    version=launch_template.latest_version_number,
                ),
                availability_zone=selected_az,
                subnet_id=selected_subnet.subnet_id,
                user_data=base64.b64encode(user_data_script.encode()).decode(),
                tags=[CfnTag(key="application", value="bowtie-build")],
            )

        CfnOutput(
            self,
            "KeyPairId",
            value=cfn_key_pair.attr_key_pair_id,
            description="id of the bowtie-build key pair",
            export_name="bowtie-keypair-id",
        )
        CfnOutput(
            self,
            "InstanceRoleArn",
            value=instance_role.role_arn,
            description="ARN of the Bowtie build EC2 instance role",
            export_name="bowtie-instance-role-arn",
        )
        if instance is not None:
            CfnOutput(
                self,
                "PublicIp",
                value=instance.attr_public_ip,
                description="public IP of the Bowtie build instance",
                export_name="bowtie-public-ip",
            )
        CfnOutput(
            self,
            "LogPrefix",
            value=log_s3_prefix,
            description="S3 prefix where build logs are uploaded",
            export_name="bowtie-log-prefix",
        )
        CfnOutput(
            self,
            "OutputPrefix",
            value=output_s3_prefix,
            description="S3 prefix where index artifacts are uploaded",
            export_name="bowtie-output-prefix",
        )
