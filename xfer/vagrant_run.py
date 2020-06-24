#!/usr/bin/env python

# Author: Ben Langmead <ben.langmead@gmail.com>
# License: MIT

"""vagrant_run

Usage:
  vagrant_run <profile> <task> <inst> <dest> [options]

Options:
  --no-destroy-on-error      Keep instance running on error.
  --creds <path>             AWS credentials file to be parsed for vagrant [default: ~/.aws/credentials].
  --no-creds-file            Don't pass AWS credentials file to EC2 host.
  --slack-ini <ini>          ini file for Slack webhooks [default: ~/.k2bench/slack.ini].
  --slack-section <section>  ini file section for log aggregator [default: slack].
  --second-profile <name>    also copy credentials for this profile to destination host.
  -a, --aggregate            Enable log aggregation.
  -h, --help                 Show this screen.
  --version                  Show version.
"""

import os
import sys
import json
import collections
import shutil

from docopt import docopt

try:
    from configparser import RawConfigParser
except ImportError:
    from ConfigParser import RawConfigParser
    sys.exc_clear()


""" ~/.k2bench/slack.ini file should look like this:
[slack]
tstring=TXXXXXXXX
bstring=BXXXXXXXX
secret=XXXXXXXXXXXXXXXXXXXXXXXX
"""


def slack_webhook_url(ini_fn, section='slack'):
    tstring, bstring, secret = read_slack_config(ini_fn, section=section)
    return 'https://hooks.slack.com/services/%s/%s/%s' % (tstring, bstring, secret)


def read_slack_config(ini_fn, section='slack'):
    cfg = RawConfigParser()
    cfg.read(ini_fn)
    if section not in cfg.sections():
        raise RuntimeError('No [%s] section in log ini file "%s"' % (section, ini_fn))
    tstring, bstring, secret = cfg.get(section, 'tstring'), cfg.get(section, 'bstring'), cfg.get(section, 'secret')
    return tstring, bstring, secret


def dict_merge(dct, merge_dct):
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def load_json(json_fn, json_dict, needs_key=None):
    if not os.path.exists(json_fn):
        raise RuntimeError('Could not find JSON file "%s"' % json_fn)
    js = json.loads(open(json_fn, 'rt').read())
    if needs_key is not None:
        if needs_key not in js:
            raise RuntimeError('JSON "%s" did not contain "%s" key at top level' % (json_fn, needs_key))
    dict_merge(json_dict, js)


def parse_app_json(js):
    app = js['app']['name']
    bucket = js['app']['bucket']
    return app, bucket, [('VAG_APPLICATION', app), ('VAG_BUCKET', bucket)]


def parse_profile_json(js, prof):
    region = js['profile'][prof]['region']
    security_group = js['profile'][prof]['security_group']
    aws_prof = js['profile'][prof]['name']
    return prof, aws_prof, region, security_group, \
           [('VAG_PROFILE', aws_prof),
            ('VAG_REGION', region),
            ('VAG_SECURITY_GROUP', security_group)]


def parse_instance_json(js, region, instance=None):
    if 'instance' in js:
        inst = js['instance']
    else:
        inst = instance
    if inst is None:
        raise RuntimeError('instance not specified, either as command-line param or in json')

    if inst not in js['ec2']['instance_type']:
        raise RuntimeError('No such instance type as "%s" in EC2 JSON' % inst)

    arch = js['ec2']['instance_type'][inst]['arch']
    ami = js['ec2']['ami'][region][arch]
    bid_price = None
    if 'bid_price' in js['ec2']['instance_type'][inst] and \
            region in js['ec2']['instance_type'][inst]['bid_price']:
        bid_price = js['ec2']['instance_type'][inst]['bid_price'][region]

    return inst, arch, ami, bid_price, \
           [('VAG_EC2_INSTANCE_TYPE', inst),
            ('VAG_EC2_ARCH', arch),
            ('VAG_AMI', ami),
            ('VAG_EC2_BID_PRICE', bid_price)]


def must_have(key, js, js_name):
    if key not in js:
        raise RuntimeError('Key "%s" not present in %s JSON' % (key, js_name))


def parse_task_json(js):
    must_have('task', js, 'task')
    must_have('volume_gb', js, 'task')
    task = js['task']
    volume_gb = js['volume_gb']
    return task, volume_gb, [('VAG_TASK', task),
                             ('VAG_VOLUME_GB', volume_gb)]


def choose_az_and_subnet(js, prof, region, inst):
    if 'azs' in js['ec2']['instance_type'][inst] and \
            region in js['ec2']['instance_type'][inst]['azs']:
        azs = js['ec2']['instance_type'][inst]['azs'][region]
    else:
        azs = js['ec2']['azs'][region]
    if len(azs) == 0:
        raise RuntimeError("Could not find any AZs for region/instance %s/%s" % (region, inst))
    az = azs[0]
    if az not in js['profile'][prof]['subnet']:
        raise RuntimeError('No subnet specified for region/az %s/%s in profile %s' % (region, az, prof))
    subnet = js['profile'][prof]['subnet'][az]
    return az, subnet, [('VAG_SUBNET_ID', subnet),
                        ('VAG_AZ', az)]


def load_aws_json(profile_json, app_json, task_json, inst_json, ec2_json,
                  profile=None, instance=None):
    js = {}
    load_json(profile_json, js, needs_key='profile')
    load_json(app_json, js, needs_key='app')
    load_json(ec2_json, js, needs_key='ec2')
    load_json(task_json, js, needs_key='task')
    if inst_json is not None:
        load_json(inst_json, js, needs_key='instance')

    app, bucket, app_param = parse_app_json(js)
    prof, aws_prof, region, security_group, profile_param = parse_profile_json(js, profile)
    inst, arch, ami, bid_price, instance_param = parse_instance_json(js, region, instance=instance)
    task, volume_gb, task_param = parse_task_json(js)
    keypair = app + '-' + region
    keypair_param = [('VAG_EC2_KEYPAIR', keypair)]
    subnet, az, subnet_param = choose_az_and_subnet(js, prof, region, inst)
    params = app_param + profile_param + instance_param + keypair_param + subnet_param + task_param + [('VAG_CREDS', '.creds.tmp')]
    return app, region, subnet, az, security_group, ami, keypair, bid_price, inst, arch, prof, aws_prof, params


def run(profile, task, inst, dest_dir, ini_fn, section, no_destroy,
        creds_file='~/.aws/credentials', second_profile=None):
    ec2_json, app_json, profile_json = 'ec2.json', 'app.json', 'profile.json'
    if not os.path.exists(task):
        raise RuntimeError('No such task directory: "%s"' % task)
    if not os.path.exists(os.path.join(task, inst)):
        raise RuntimeError('No such instance directory: "%s/%s"' % (task, inst))
    if os.path.exists(dest_dir):
        raise RuntimeError('Destination directory "%s" exists' % dest_dir)
    os.makedirs(dest_dir)
    task_json = os.path.join(task, 'task.json')
    inst_json = os.path.join(task, inst, 'inst.json')
    app, region, subnet, az, security_group, ami, keypair, bid_price, inst, arch, prof, aws_prof, params = \
        load_aws_json(profile_json, app_json, task_json, inst_json, ec2_json, profile=profile)
    vagrant_args = ''
    if no_destroy:
        vagrant_args += ' --no-destroy-on-error'
    for template_dir in ['scripts', 'vagrant_include']:
        for base_fn in os.listdir(template_dir):
            fn = os.path.join(template_dir, base_fn)
            if os.path.isfile(fn):
                shutil.copyfile(fn, os.path.join(dest_dir, base_fn))
    for base_fn in os.listdir(task):
        fn = os.path.join(task, base_fn)
        if os.path.isfile(fn):
            shutil.copyfile(fn, os.path.join(dest_dir, base_fn))

    def _write_exports(export_fh):
        # TODO: move the credentials file parsing to here; better to do it in the script
        export_fh.write('#!/bin/bash\n')
        for k, v in params:
            export_fh.write('export %s=%s\n' % (k, v))
    run_scr = os.path.join(dest_dir, 'run.sh')
    run_nd_scr = os.path.join(dest_dir, 'run_no_destroy.sh')
    destroy_scr = os.path.join(dest_dir, 'destroy.sh')
    ssh_scr = os.path.join(dest_dir, 'ssh.sh')
    slack_scr = os.path.join(dest_dir, 'slack.py')
    creds_scr = os.path.join(dest_dir, 'creds.py')
    with open(run_scr, 'wt') as fh:
        _write_exports(fh)
        fh.write('./creds.py && \\\n')
        fh.write('vagrant up %s 2>&1 | tee vagrant.log && \\\n' % vagrant_args)
        fh.write('vagrant destroy -f\n')
        fh.write('rm -f .creds.tmp\n')
    with open(run_nd_scr, 'wt') as fh:
        _write_exports(fh)
        fh.write('./creds.py && \\\n')
        fh.write('vagrant up %s 2>&1 | tee vagrant.log\n' % vagrant_args)
        fh.write('rm -f .creds.tmp\n')
    with open(destroy_scr, 'wt') as fh:
        _write_exports(fh)
        fh.write('touch .creds.tmp && vagrant destroy -f\n')
        fh.write('rm -f .creds.tmp\n')
    with open(ssh_scr, 'wt') as fh:
        _write_exports(fh)
        fh.write('touch .creds.tmp && vagrant ssh\n')
        fh.write('rm -f .creds.tmp\n')
    slack_scr_in = 'slack_template.py'
    if not os.path.exists(slack_scr_in):
        raise RuntimeError('Cannot find slack template script')
    with open(slack_scr, 'wt') as fh:
        with open(slack_scr_in, 'rt') as ifh:
            for ln in ifh:
                fh.write(ln)
        fh.write('\n\nif __name__ == "__main__":\n')
        fh.write('    do_slack_report("%s", "vagrant.log")\n' % slack_webhook_url(ini_fn, section=section))
    creds_scr_in = 'make_creds_template.py'
    if not os.path.exists(creds_scr_in):
        raise RuntimeError('Cannot find make_creds template script')
    with open(creds_scr, 'wt') as fh:
        with open(creds_scr_in, 'rt') as ifh:
            for ln in ifh:
                fh.write(ln)
        fh.write('\n\nif __name__ == "__main__":\n')
        profs = '"%s"' % aws_prof
        if second_profile is not None:
            profs += (', "%s"' % second_profile)
        fh.write('    make_creds_file([%s], "%s")\n' % (profs, creds_file))
    for scr in [run_scr, run_nd_scr, destroy_scr, ssh_scr, slack_scr, creds_scr]:
        os.chmod(scr, 0o700)


def go():
    args = docopt(__doc__)
    slack_ini = os.path.expanduser(args['--slack-ini'])
    prof, task, inst, dest = args['<profile>'], args['<task>'], args['<inst>'], args['<dest>']
    run(prof, task, inst, dest, slack_ini,
        args['--slack-section'], args['--no-destroy-on-error'],
        creds_file=args['--creds'],
        second_profile=args['--second-profile'])


if __name__ == '__main__':
    go()
