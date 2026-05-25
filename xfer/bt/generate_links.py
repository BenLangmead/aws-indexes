#!/usr/bin/env python3

import os
import sys


check = '--no-check' not in sys.argv

url_pre = 'https://genome-idx.s3.amazonaws.com/bt/'
s3_pre = 's3://genome-idx/bt/'

short_suf = ['full', '1', '2', '3', '4', 'r1', 'r2']
metadata_suf = ['md5', 'dict', 'manifest']
metadata_long_suf = {
    'md5': 'md5',
    'dict': 'dict',
    'manifest': 'manifest.json',
}


def index_ext(toks):
    ext = toks[6].strip() if len(toks) > 6 and toks[6].strip() else 'bt2'
    if ext not in ('bt2', 'bt2l'):
        raise ValueError('expected index extension "bt2" or "bt2l", got "%s"' % ext)
    return ext


def metadata_types(toks):
    types = ['md5']
    if len(toks) > 7 and toks[7].strip():
        types.extend(t.strip() for t in toks[7].split(';') if t.strip())
    invalid = sorted(set(types) - set(metadata_suf))
    if invalid:
        raise ValueError('unknown metadata type(s): %s' % ', '.join(invalid))
    return [typ for typ in metadata_suf if typ in types]


with open('shortname_map.csv', 'rt') as fh:
    for ln in fh:
        if ',' not in ln:
            continue
        if ln.startswith('#'):
            continue
        toks = ln.rstrip().split(',')
        short, long = toks[0], toks[1]
        ext = index_ext(toks)
        metadata = metadata_types(toks)
        long_suf = ['zip', f'1.{ext}', f'2.{ext}', f'3.{ext}', f'4.{ext}', f'rev.1.{ext}', f'rev.2.{ext}']
        # generate https links
        for sh, lo in zip(short_suf, long_suf):
            url = '%s%s.%s' % (url_pre, long, lo)
            if check:
                cmd = ['curl', '--output', '/dev/null', '--silent', '--head', '--fail', url]
                if os.system(' '.join(cmd)) != 0:
                    raise RuntimeError('URL "%s" does not exist' % url)
            print('[bt2_%s_%s]: %s' % (short, sh, url))
        for typ in metadata:
            print('[bt2_%s_%s]: %s%s.%s' % (short, typ, url_pre, long, metadata_long_suf[typ]))
        # generate s3 links
        for sh, lo in zip(short_suf, long_suf):
            print('[bt2_%s_%s_s3]: %s%s.%s' % (short, sh, s3_pre, long, lo))
        for typ in metadata:
            print('[bt2_%s_%s_s3]: %s%s.%s' % (short, typ, s3_pre, long, metadata_long_suf[typ]))
