"""
Stack for granular (hardware-PMU) benchmarking of the Movi MEM query on a
bare-metal EC2 instance where perf PEBS sampling and likwid uncore counters are
fully available (unlike the Rockfish dev node, whose perf_event_paranoid=2 blocks
per-line sampling).

Why this stack exists: the redesigned MEM coroutine (query_mem_coroutine) is
correct but ~15% slower than production at all widths with a FLAT width curve.
The standing hypothesis is that MEM is compute/scan-bound -- the O(#runs)
skip-count and rc-interval scans inside extend_bidirectional dominate, leaving
little LF-jump latency to hide -- but that was only inferred from wall-clock on
Rockfish, never confirmed with hardware counters. This stack profiles the MEM
query (production sequential + coroutine W1/W8) with full PMU access to (a)
confirm compute- vs memory-bound and (b) get per-source-line CYCLES + DRAM-miss
attribution that surfaces concrete optimization targets in the scan code.

Provisions a c5.metal SPOT instance (Cascade Lake -- same microarchitecture as
the Rockfish Xeon Gold 6248R we profiled, so results are directly comparable),
installs perf + likwid (+ optional VTune), downloads the Movi source / index /
ftab(10,12) / reads from S3, builds BOTH movi-regular-thresholds (production
sequential MEM) and movi-co (coroutine) at RelWithDebInfo so perf maps to source
lines, and runs bench/run_bench.sh. Results are tarred up to S3.

Mirrors the conventions of build/movi_kmer_bench (and build/pfp_thresh_builder).

Author: Ben Langmead (scaffolded with Claude Code)
"""

import base64
import json

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnOutput,
    CfnTag,
)
from constructs import Construct


class CdkEc2Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open('config.json', 'r') as f:
            config = json.load(f)

        az = config['availability_zone']
        itype = config['instance_type']['type']
        spot_price = str(config['instance_type']['spot_price'])
        root_gb = int(config.get('root_volume_gb', 200))

        vpc = ec2.Vpc(
            self, "MoviBenchVpc",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="movi-bench-public-subnet-1",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
        )
        sec_group = ec2.SecurityGroup(
            self, "MoviBenchSecurityGroup", vpc=vpc, allow_all_outbound=True
        )
        sec_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH access"
        )

        cfn_key_pair = ec2.CfnKeyPair(
            self, "MoviBenchKeyPair",
            key_name="movi-mem-bench",
            tags=[CfnTag(key="application", value="movi-mem-bench")],
        )

        # Credential model (same as build/bowtie and build/movi_kmer_bench): NO
        # permanent credentials.
        #  - Inputs: public genome-idx objects -> downloaded with --no-sign-request.
        #  - Results: the instance role is allowed to sts:AssumeRole the pre-existing
        #    cross-account upload role (S3UploadFromComputeRole in the genome-idx
        #    account); the AWS CLI assumes it via credential_source=Ec2InstanceMetadata.
        upload_role_arn = config['upload_role_arn'].strip()
        upload_profile = config.get('upload_profile', 'data-langmead')
        results_s3 = config['results_s3_prefix'].rstrip('/')

        # PERMANENT instance role -- REUSED from build/movi_kmer_bench. We do NOT
        # create it in CFN, because a CDK-managed role is deleted on `cdk destroy`,
        # and deleting a role named in a cross-account trust policy invalidates
        # that trust. It was created once by movi_kmer_bench/setup_permanent_role.sh
        # and its trust on S3UploadFromComputeRole is account-scoped to
        # 159168350739:root, so this MEM stack can reuse it with no IAM changes.
        # We only *reference* it (mutable=False => CDK never touches its policies).
        instance_role = iam.Role.from_role_name(
            self, "MoviBenchInstanceRole",
            config.get('instance_role_name', 'index-zone-movi-kmer-bench-role'),
            mutable=False,
        )

        # Bare metal => one whole physical host; bid ~1/2 on-demand so price-based
        # interruption is very unlikely. (AWS can still reclaim on capacity, rare.)
        launch_template = ec2.LaunchTemplate(
            self, "MoviBenchLaunchTemplate",
            instance_type=ec2.InstanceType(itype),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=sec_group,
            role=instance_role,
            key_name=cfn_key_pair.key_name,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        root_gb, volume_type=ec2.EbsDeviceVolumeType.GP3
                    ),
                )
            ],
            spot_options=ec2.LaunchTemplateSpotOptions(max_price=float(spot_price)),
        )

        # The benchmark script, shipped inline (base64) so it lives in this repo.
        with open('bench/run_bench.sh', 'r') as f:
            run_bench_b64 = base64.b64encode(f.read().encode()).decode()

        # Inputs are public in genome-idx -> download unsigned (no credentials).
        reads = config['reads']
        reads_dl = '\n'.join(
            f"aws s3 cp --no-sign-request {config['reads_s3_prefix']}/{r} "
            f"/home/ec2-user/bench/reads/{r}" for r in reads
        )

        # Both ftab files land in the index dir (named ftab.<k>.bin by S3 key) so
        # production read_ftab() and movi-co can use either ftab-k at query time.
        ftab_dl = '\n'.join(
            f"aws s3 cp --no-sign-request {uri} "
            f"/home/ec2-user/bench/index/{uri.rsplit('/', 1)[1]}"
            for uri in config['ftab_s3_uris']
        )

        ftab_ks = ' '.join(str(k) for k in config.get('ftab_ks', []))

        vtune_install = ""
        if config.get('install_vtune', False):
            vtune_install = '\n'.join([
                "cat > /etc/yum.repos.d/oneAPI.repo << 'EOL'",
                "[oneAPI]",
                "name=Intel oneAPI",
                "baseurl=https://yum.repos.intel.com/oneapi",
                "enabled=1", "gpgcheck=1", "repo_gpgcheck=1",
                "gpgkey=https://yum.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB",
                "EOL",
                "dnf install -y intel-oneapi-vtune || true",
            ]) + '\n'

        user_data_script = '\n'.join([
            "#!/bin/bash",
            "set -x",
            "exec > /var/log/movi-bench-userdata.log 2>&1",

            # --- packages ---
            "dnf update -y",
            "dnf install -y gcc gcc-c++ cmake make git zlib-devel numactl perf "
            "hwloc hwloc-devel time tar gzip python3 python3-pip unzip",
            # Ensure AWS CLI v2 is present (instance role used for the results upload)
            "command -v aws || (cd /tmp && curl -sSL "
            "'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o awscliv2.zip && "
            "unzip -q awscliv2.zip && ./aws/install)",

            # --- expose the full PMU (persisted) ---
            "echo 'kernel.perf_event_paranoid=-1' > /etc/sysctl.d/99-perf.conf",
            "echo 'kernel.kptr_restrict=0'      >> /etc/sysctl.d/99-perf.conf",
            "sysctl --system",

            # --- build likwid from source (perf_event backend works at paranoid<=0) ---
            "cd /opt && git clone https://github.com/RRZE-HPC/likwid.git",
            "cd /opt/likwid && sed -i 's|^ACCESSMODE = .*|ACCESSMODE = perf_event|' config.mk && "
            "sed -i 's|^PREFIX = .*|PREFIX = /usr/local|' config.mk && make -j$(nproc) && make install",

            vtune_install,

            # --- upload profile: assume the cross-account genome-idx upload role
            #     via the instance role (Ec2InstanceMetadata) -- no permanent creds.
            "mkdir -p /root/.aws",
            "cat > /root/.aws/config << 'EOL'",
            f"[profile {upload_profile}]",
            f"region = {config['region']}",
            f"role_arn = {upload_role_arn}",
            "credential_source = Ec2InstanceMetadata",
            "EOL",
            "mkdir -p /home/ec2-user/.aws && cp /root/.aws/config /home/ec2-user/.aws/config",
            "chown -R ec2-user:ec2-user /home/ec2-user/.aws",

            # --- layout ---
            "BENCH=/home/ec2-user/bench",
            "mkdir -p $BENCH/index $BENCH/reads",

            # --- inputs from S3 (public genome-idx objects -> unsigned, no creds) ---
            f"aws s3 cp --no-sign-request {config['src_s3_uri']} $BENCH/movi_src.tar.gz",
            f"aws s3 cp --no-sign-request {config['index_s3_uri']} $BENCH/index/index.movi",
            ftab_dl,
            reads_dl,

            # --- build movi-co AND movi-regular-thresholds (RelWithDebInfo =>
            #     -O2 -g, so perf maps to source lines) ---
            "mkdir -p $BENCH/Movi && tar xzf $BENCH/movi_src.tar.gz -C $BENCH/Movi",
            "SRC=$(dirname $(find $BENCH/Movi -maxdepth 3 -name CMakeLists.txt | head -1))",
            "mkdir -p $SRC/build-release && cd $SRC/build-release && "
            "cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo .. && "
            "cmake --build . --target movi-co --target movi-regular-thresholds -j$(nproc)",
            "CO=$(find $SRC -name movi-co -type f | head -1)",
            "PROD=$(find $SRC -name movi-regular-thresholds -type f | head -1)",

            # --- write & launch the benchmark (detached; uploads results to S3) ---
            f"echo {run_bench_b64} | base64 -d > $BENCH/run_bench.sh",
            "chmod +x $BENCH/run_bench.sh",
            "chown -R ec2-user:ec2-user $BENCH",
            f"export BENCH=$BENCH CO=$CO PROD=$PROD IDX=$BENCH/index READS_DIR=$BENCH/reads",
            f"export RESULTS_S3={results_s3} UPLOAD_PROFILE={upload_profile}",
            "setsid bash $BENCH/run_bench.sh > $BENCH/bench.out 2>&1 < /dev/null &",
            "echo USERDATA_DONE",
        ]) + '\n'

        selected_subnet = next(
            s for s in vpc.public_subnets if s.availability_zone in [az, 'dummy1a']
        )

        instance = ec2.CfnInstance(
            self, "MoviBenchInstance",
            launch_template=ec2.CfnInstance.LaunchTemplateSpecificationProperty(
                launch_template_id=launch_template.launch_template_id,
                version=launch_template.latest_version_number
            ),
            availability_zone=az,
            subnet_id=selected_subnet.subnet_id,
            user_data=base64.b64encode(user_data_script.encode()).decode(),
            tags=[CfnTag(key="application", value="movi-mem-bench")]
        )

        CfnOutput(self, "KeyPairId", value=cfn_key_pair.attr_key_pair_id,
                  description="id of the key pair", export_name="movi-mem-bench-keypair-id")
        CfnOutput(self, "PublicIp", value=instance.attr_public_ip,
                  description="public ip of the instance", export_name="movi-mem-bench-public-ip")
        CfnOutput(self, "ResultsLocation", value=results_s3,
                  description="genome-idx S3 prefix where PMU results land")
        CfnOutput(self, "InstanceRoleArn", value=instance_role.role_arn,
                  description="instance role ARN -- must be trusted by S3UploadFromComputeRole")
