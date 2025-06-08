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


class CdkEc2Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load configuration
        with open('config.json', 'r') as f:
            config = json.load(f)

        az = config['availability_zone']

        vpc = ec2.Vpc(
            self,
            "CdkEC2Vpc",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="cdk-ec2-public-subnet-1",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
        )
        sec_group = ec2.SecurityGroup(
            self, "CdkEC2SecurityGroup", vpc=vpc, allow_all_outbound=True
        )
        sec_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH access"
        )

        cfn_key_pair = ec2.CfnKeyPair(
            self,
            "CdkEC2KeyPair",
            key_name="hprc-build",
            tags=[CfnTag(key="application", value="hprc-build")],
        )

        instance_config = config['instance_type']
        use_big_guy = config['use_large_instance']

        # Launch Template
        launch_template = ec2.LaunchTemplate(
            self,
            "CdkEC2LunchTemplate",
            instance_type=ec2.InstanceType(
                instance_config['large']['type'] if use_big_guy else instance_config['small']['type']
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=sec_group,
            key_name=cfn_key_pair.key_name,
            spot_options=ec2.LaunchTemplateSpotOptions(
                max_price=instance_config['large']['spot_price'] if use_big_guy else instance_config['small']['spot_price']
            )
        )
        config = configparser.ConfigParser()
        config.read(os.path.expanduser('~/.aws/credentials'))
        aws_access_key_id = config['data-langmead']['aws_access_key_id']
        aws_secret_access_key = config['data-langmead']['aws_secret_access_key']

        def _wrapped_named_command(cmd, name, interval=10):
            cmd = ["su - ec2-user -c 'bash -s' <<'EOF'",
                   'mkdir -p logs &&',
                   'psrecord',
                   f'--log "logs/{name}_resource_usage.log"',
                   f'--interval {interval}',
                   f'--plot "logs/{name}_resource_plot.png"',
                   '--include-children',
                   '--',
                   f'"/usr/bin/time -v {cmd}"',
                   f'> logs/{name}_stdout.log',
                   f'2> logs/{name}_stderr.log',
                   'EOF'
                   ]
            return ' '.join(cmd)
        
        # screen
        # mkdir -p logs && psrecord --log "logs/pfp_resource_usage.log" --interval 10 --plot "logs/pfp_resource_plot.png" --include-children -- "/usr/bin/time -v ~/pfp-thresholds/build/pfp_thresholds --skip-parsing -f ./hprc320.fa" > logs/pfp_stdout.log 2> logs/pfp_stderr.log

        user_data_script = '\n'.join([
            "#!/bin/bash",
            "yum update -y",
            "yum install -y docker git emacs gcc g++ cmake zlib-devel",
            "systemctl enable docker",
            "systemctl start docker",
            "mkdir -p /home/ec2-user/.aws",
            "cat > /home/ec2-user/.aws/credentials << 'EOL'",
            "[data-langmead]",
            f"aws_access_key_id = {aws_access_key_id}",
            f"aws_secret_access_key = {aws_secret_access_key}",
            "EOL",
            "chmod 600 /home/ec2-user/.aws/credentials",
            "chown -R ec2-user:ec2-user /home/ec2-user/.aws",
            "python3 -m ensurepip --upgrade",
            "python3 -m pip install psrecord matplotlib"]) + '\n'
        
        # big_bwt = [
        #     "su - ec2-user -c 'bash -s' <<'EOF'",
        #     'git clone https://gitlab.com/manzai/Big-BWT.git',
        #     'cd Big-BWT && make && cd ..',
        #     'EOF'
        # ]
        # user_data_script += '\n'.join(big_bwt)

        pfp_thresholds = [
            "su - ec2-user -c 'bash -s' <<'EOF'",
            'git clone -b build-options https://github.com/mohsenzakeri/pfp-thresholds.git',
            'mkdir -p pfp-thresholds/build && cd pfp-thresholds/build && cmake .. && make -j 16 && cd ../..',
            'EOF'
        ]
        user_data_script += '\n'.join(pfp_thresholds) + '\n'

        download_dict_parse = [
            "su - ec2-user -c 'bash -s' <<'EOF'",
            'cd /tmp',
            'aws s3 --profile data-langmead cp s3://genome-idx/movi/hprcv2_inputs/hprc466.fa.dict .',
            'aws s3 --profile data-langmead cp s3://genome-idx/movi/hprcv2_inputs/hprc466.fa.parse .',
            'EOF'
        ]
        user_data_script += '\n'.join(download_dict_parse) + '\n'

        # -r is important!  Otherwise you exhaust disk space
        run_pfp_thresholds = [
            'cd /tmp',
            _wrapped_named_command('~/pfp-thresholds/build/pfp_thresholds --skip-parsing -r -f ./hprc466.fa', 'pfp_thresholds', 15)
        ]
        user_data_script += '\n'.join(run_pfp_thresholds)

        # The first time you run cdk synth in a new region, it only sees dummy
        # versions of the availability zones
        selected_subnet = next(
            s for s in vpc.public_subnets if s.availability_zone in [az, 'dummy1a']
        )

        instance = ec2.CfnInstance(
            self, "CdkEC2Instance",
            launch_template=ec2.CfnInstance.LaunchTemplateSpecificationProperty(
                launch_template_id=launch_template.launch_template_id,
                version=launch_template.latest_version_number
            ),
            availability_zone=az,
            subnet_id=selected_subnet.subnet_id,
            user_data=base64.b64encode(user_data_script.encode()).decode(),
            tags=[CfnTag(key="application", value="hprc-build")]
        )

        CfnOutput(self, "KeyPairId", value=cfn_key_pair.attr_key_pair_id,
                  description="id of my key pair",
                  export_name="ec2-keypair-id")

        CfnOutput(self, "PublicIp", value=instance.attr_public_ip, 
                  description="public ip of my instance", 
                  export_name="ec2-public-ip")
