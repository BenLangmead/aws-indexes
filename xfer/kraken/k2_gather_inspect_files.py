#!/usr/bin/env python3

import os


dbs = ['viral', 'minusb',
       'standard', 'standard_8gb', 'standard_16gb',
       'pluspf', 'pluspf_8gb', 'pluspf_16gb',
       'pluspfp_8gb', 'pluspfp_16gb']
#       'pluspfp', 'pluspfp_8gb', 'pluspfp_16gb']

dates = ['20201202', '20201202',
         '20201202', '20201202', '20201202',
         '20210127', '20210127', '20210127',
         '20210127', '20210127']


for db, date in zip(dbs, dates):
    url = 'https://genome-idx.s3.amazonaws.com/kraken/%s_%s/inspect.txt' % (db, date)
    cmd = ['curl', url, '2>/dev/null', '>', 'inspect_%s_%s.txt' % (db, date)]
    result = os.system(' '.join(cmd))
grep