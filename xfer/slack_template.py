#!/usr/bin/env python3

import os
import requests


def do_slack_report(slack_url, vagrant_log_fn):
    attachments = []
    with open(vagrant_log_fn, 'r') as fh:
        for ln in fh:
            if '===HAPPY' in ln:
                st = ln[ln.find('===HAPPY') + 9:].rstrip()
                attachments.append({'text': st, 'color': 'good'})
            elif '===SAD' in ln:
                st = ln[ln.find('===SAD') + 7:].rstrip()
                attachments.append({'text': st, 'color': 'danger'})
    name = 'no name'
    if os.path.exists('name.txt'):
        with open('name.txt', 'rt') as fh:
            name = fh.read().strip()
    requests.put(slack_url, json={
        'username': 'webhookbot',
        'text': '%s:' % name,
        'attachments': attachments})
