#!/usr/bin/env python3

import subprocess


dbs = ['viral', 'minusb',
       'standard', 'standard_8gb', 'standard_16gb',
       'pluspf', 'pluspf_8gb', 'pluspf_16gb',
       'pluspfp', 'pluspfp_8gb', 'pluspfp_16gb']

date = '20201202'


def get_size(url):
    cmd = ['curl', '-I', url, '2>/dev/null',
           '|', 'grep', 'Content-Length',
           '|', 'awk', '\'{print $2/1024/1024/1024}\'']
    cmd = ' '.join(cmd)
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    return '%0.1f' % float(result.stdout.decode('utf-8'))


for db in dbs:
    db_url = 'https://genome-idx.s3.amazonaws.com/kraken/k2_%s_%s.tar.gz' % (db, date)
    ar_sz = get_size(db_url)
    hash_url = 'https://genome-idx.s3.amazonaws.com/kraken/%s_%s/hash.k2d' % (db, date)
    hash_sz = get_size(hash_url)
    print(db)
    print(ar_sz + ' ' + hash_sz)
