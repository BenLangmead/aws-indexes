#!/usr/bin/env python3

import os


def make_creds_file(profs, creds_file):
    credential_fn = os.path.expanduser(creds_file)
    if not os.path.exists(credential_fn):
        raise RuntimeError('No such credentials file "%s"' % credential_fn)
    with open('.creds.tmp', 'wt') as ofh:
        labels = ['default', 'secondary']
        if len(profs) == 1:
            labels = [labels[0]]
        for i, (label, prof) in enumerate(zip(labels, profs)):
            ofh.write('[%s]\n' % label)
            found = False
            with open(credential_fn, 'rt') as fh:
                while True:
                    ln = fh.readline()
                    if len(ln) == 0:
                        break
                    ln = ln.rstrip()
                    if ln[1:-1] == prof:
                        found = True

                        def _parse(key_to_parse):
                            tokens = fh.readline().rstrip().split('=')
                            ky, vl = tokens[0].strip(), tokens[1].strip()
                            assert ky == key_to_parse
                            ofh.write('%s = %s\n' % (key_to_parse, vl))
                        _parse('aws_access_key_id')
                        _parse('aws_secret_access_key')
            if not found:
                raise RuntimeError('Could not find credentials for profile "%s"' % prof)
