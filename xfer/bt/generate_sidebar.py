#!/usr/bin/env python3

"""
      <!-- H. sapiens, NCBI GRCh38 no_alt -->
      <tr><td>
        <a href="ftp://ftp.ccb.jhu.edu/pub/data/bowtie_indexes/GRCh38_no_alt.zip"><i>H. sapiens</i>, NCBI GRCh38</a>
        </td><td align="right">
          <b>2.7 GB</b>
      </td></tr>

"""


url_pre = 'https://genome-idx.s3.amazonaws.com/bt/'

with open('shortname_map.csv', 'rt') as fh:
    for ln in fh:
        if ',' not in ln:
            continue
        if ln.startswith('#'):
            continue
        if len(ln.strip()) == 0:
            continue
        toks = ln.rstrip().split(',')
        short, long, species, scientific_name, assembly, source = toks[0], toks[1], toks[2], toks[3], toks[4], toks[5]
        url = '%s%s.zip' % (url_pre, long)
        indent1 = ' ' * 6
        indent2 = ' ' * 8
        indent3 = ' ' * 12
        entry = '%s<tr>\n' % indent1
        entry += '%s<td>\n' % indent2
        entry += '%s<a href="%s"><i>%s</i>, %s</a>\n' % (indent3, url, scientific_name, assembly)
        entry += '%s</td>\n' % indent2
        entry += '%s<td align="right">\n' % indent2
        entry += '%s%s\n' % (indent3, source)
        entry += '%s</td>\n' % indent2
        entry += '%s</tr>\n' % indent1
        print(entry)
