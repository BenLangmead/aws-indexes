#!/usr/bin/env python3

import subprocess
import sys


verbose = any(map(lambda x: x == '--verbose', sys.argv[1:]))


dbs = ['viral',    'minusb',
       'standard', 'standard_08gb', 'standard_16gb',
       'pluspf',   'pluspf_08gb',   'pluspf_16gb',
       'pluspfp',  'pluspfp_08gb',  'pluspfp_16gb',
       'core_nt']

dates = ['20250402', '20250402',
         '20250402', '20250402', '20250402',
         '20250402', '20250402', '20250402',
         '20250402', '20250402', '20250402',
         '20241228']


def get_size(url, verbose=False):
    cmd = ['curl', '-I', url, '2>/dev/null',
           '|', 'grep', 'Content-Length',
           '|', 'awk', '\'{print $2/1024/1024/1024}\'']
    cmd = ' '.join(cmd)
    if verbose:
        print(cmd)
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    return '%0.1f' % float(result.stdout.decode('utf-8'))


for db, date in zip(dbs, dates):
    db_url = 'https://genome-idx.s3.amazonaws.com/kraken/k2_%s_%s.tar.gz' % (db, date)
    ar_sz = get_size(db_url, verbose)
    hash_url = 'https://genome-idx.s3.amazonaws.com/kraken/%s_%s/hash.k2d' % (db, date)
    hash_sz = get_size(hash_url, verbose)
    print(db)
    print(ar_sz + ' ' + hash_sz)
