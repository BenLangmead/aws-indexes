#!/usr/bin/env python3

import os
import sys


check = '--no-check' not in sys.argv

url_pre = 'https://genome-idx.s3.amazonaws.com/bt/'
s3_pre = 's3://genome-idx/bt/'

short_suf = ['full', '1', '2', '3', '4', 'r1', 'r2']


def index_ext(toks):
    ext = toks[6].strip() if len(toks) > 6 and toks[6].strip() else 'bt2'
    if ext not in ('bt2', 'bt2l'):
        raise ValueError('expected index extension "bt2" or "bt2l", got "%s"' % ext)
    return ext

with open('shortname_map.csv', 'rt') as fh:
    for ln in fh:
        if ',' not in ln:
            continue
        if ln.startswith('#'):
            continue
        toks = ln.rstrip().split(',')
        short, long = toks[0], toks[1]
        ext = index_ext(toks)
        long_suf = ['zip', f'1.{ext}', f'2.{ext}', f'3.{ext}', f'4.{ext}', f'rev.1.{ext}', f'rev.2.{ext}']
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
