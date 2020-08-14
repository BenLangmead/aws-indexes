#!/usr/bin/env python3

with open('shortname_map.csv', 'rt') as fh:
    for ln in fh:
        if ',' not in ln:
            continue
        if ln.startswith('#'):
            continue
        toks = ln.rstrip().split(',')
        short, long, species, _, assembly, source = toks[0], toks[1], toks[2], toks[3], toks[4], toks[5]
        line = '%s / %s | [%s][bt2_%s_source] | [full zip][bt2_%s_full], [.1.bt2][bt2_%s_1], [.2.bt2][bt2_%s_2], [.3.bt2][bt2_%s_3], [.4.bt2][bt2_%s_4], [.rev.1.bt2][bt2_%s_r1], [.rev.2.bt2][bt2_%s_r2] | [full zip][bt2_%s_full_s3], [.1.bt2][bt2_%s_1_s3], [.2.bt2][bt2_%s_2_s3], [.3.bt2][bt2_%s_3_s3], [.4.bt2][bt2_%s_4_s3], [.rev.1.bt2][bt2_%s_r1_s3], [.rev.2.bt2][bt2_%s_r2_s3]' % (species, assembly, source, short, short, short, short, short, short, short, short, short, short, short, short, short, short, short)
        print(line)
