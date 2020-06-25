#!/usr/bin/env python3

import os
import sys


check = '--no-check' not in sys.argv

url_pre = 'https://genome-idx.s3.amazonaws.com/bt/'
s3_pre = 's3://genome-idx/bt/'

short_suf = ['full', '1', '2', '3', '4', 'r1', 'r2']
long_suf = ['zip', '1.bt2', '2.bt2', '3.bt2', '4.bt2', 'rev.1.bt2', 'rev.2.bt2']

with open('shortname_map.csv', 'rt') as fh:
    for ln in fh:
        if ',' not in ln:
            continue
        if ln.startswith('#'):
            continue
        toks = ln.rstrip().split(',')
        short, long = toks[0], toks[1]
        # generate https links
        for sh, lo in zip(short_suf, long_suf):
            url = '%s%s.%s' % (url_pre, long, lo)
            if check:
                cmd = ['curl', '--output', '/dev/null', '--silent', '--head', '--fail', url]
                if os.system(' '.join(cmd)) != 0:
                    raise RuntimeError('URL "%s" does not exist' % url)
            print('[bt2_%s_%s]: %s' % (short, sh, url))
        # generate s3 links
        for sh, lo in zip(short_suf, long_suf):
            print('[bt2_%s_%s_s3]: %s%s.%s' % (short, sh, s3_pre, long, lo))
