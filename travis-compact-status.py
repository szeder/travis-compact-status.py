#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Copyright 2018 SZEDER Gábor

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('resource', choices=['branches', 'builds'],
    help="list branches or builds")
parser.add_argument('reposlug', metavar='repo-slug',
    help="<username>/<reponame>")

args = parser.parse_args()

print('Will show ' + args.resource + ' on repo ' + args.reposlug + '...')
