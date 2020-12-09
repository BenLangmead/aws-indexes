#!/usr/bin/env python3

"""
E.g.:
python k2_s3_xfer_manifest.py 20200919
"""

import sys


date = sys.argv[1]
bracken_lengths = [50, 75, 100, 150, 200, 250, 300]
files = ['hash.k2d', 'opts.k2d', 'taxo.k2d', 'seqid2taxid.map', 'inspect.txt']

for ln in bracken_lengths:
    files.append('database%dmers.kmer_distrib' % ln)

dbs = ['viral', 'minusb',
       'standard', 'standard_8gb', 'standard_16gb',
       'pluspf', 'pluspf_8gb', 'pluspf_16gb',
       'pluspfp', 'pluspfp_8gb', 'pluspfp_16gb']

source_url = 's3://k2-dbs/dbs'
dest_path = 'kraken'

sources = list(map(lambda x: source_url + '/mkidx_' + x, dbs))
dests = list(map(lambda x: dest_path + '/' + x + '_' + date, dbs))
archive_fns = list(map(lambda x: dest_path + '/k2_' + x + '_' + date, dbs))

for src, dst, archive_fn in zip(sources, dests, archive_fns):
    for file in files:
        print('%s/%s %s/%s' % (src, file, dst, file))
    print('%s/db.tar.gz %s.tar.gz' % (src, archive_fn))
