#!/usr/bin/env python3

short_suf = ['full', '1', '2', '3', '4', 'r1', 'r2']


def index_ext(toks):
    ext = toks[6].strip() if len(toks) > 6 and toks[6].strip() else 'bt2'
    if ext not in ('bt2', 'bt2l'):
        raise ValueError('expected index extension "bt2" or "bt2l", got "%s"' % ext)
    return ext


def file_labels(ext):
    return ['full zip', f'.1.{ext}', f'.2.{ext}', f'.3.{ext}', f'.4.{ext}', f'.rev.1.{ext}', f'.rev.2.{ext}']


with open('shortname_map.csv', 'rt') as fh:
    for ln in fh:
        if ',' not in ln:
            continue
        if ln.startswith('#'):
            continue
        toks = ln.rstrip().split(',')
        short, long, species, _, assembly, source = toks[0], toks[1], toks[2], toks[3], toks[4], toks[5]
        labels = file_labels(index_ext(toks))
        https_links = ', '.join('[%s][bt2_%s_%s]' % (label, short, suf) for label, suf in zip(labels, short_suf))
        s3_links = ', '.join('[%s][bt2_%s_%s_s3]' % (label, short, suf) for label, suf in zip(labels, short_suf))
        line = '%s / %s | [%s][bt2_%s_source] | %s | %s' % (species, assembly, source, short, https_links, s3_links)
        print(line)
