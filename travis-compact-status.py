#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Copyright 2018 SZEDER Gábor

import argparse
import os
import requests
import subprocess
import sys
import yaml

if sys.version_info < (3, 0) and \
   not sys.stdout.isatty() and \
   'PYTHONIOENCODING' not in os.environ:
    import codecs
    UTF8Writer = codecs.getwriter('utf8')
    sys.stdout = UTF8Writer(sys.stdout)


def die(msg):
    print(msg)
    exit(1)

def get_travis_access_token():
    errmsg = "error: couldn't read Travis CI API access token: "
    try:
        with open(os.environ['HOME'] + '/.travis/config.yml', 'r') as f:
            return yaml.safe_load(f)['endpoints']['https://api.travis-ci.org/']['access_token']
    except KeyError as e:
        die(errmsg + 'No such key: ' + str(e))
    except Exception as e:
        die(errmsg + str(e))


parser = argparse.ArgumentParser()
parser.add_argument('resource', choices=['branches', 'builds'],
    help="list branches or builds")
parser.add_argument('reposlug', metavar='repo-slug', nargs='?', default='',
    help="<username>/<reponame>")

parser.add_argument('-n', '--count', dest='count',
    type=int, default=20, choices=range(1, 101),
    metavar='1..100', help="number of builds to show")

color_args = parser.add_argument_group()
color_args.add_argument('-c', '--color', dest='use_color',
    action='store_const', const=1, default=sys.stdout.isatty(),
    help="use colors (even when stdout is not a TTY)")
color_args.add_argument('--no-color', dest='use_color',
    action='store_const', const=0,
    help="don't use colors (even when stdout is a TTY)")

args = parser.parse_args()

if args.reposlug == '':
    try:
        # The output of 'git config' includes a trailing newline
        # character, strip it.
        reposlug = subprocess.check_output(['git', 'config', 'travis.slug']) \
            .decode().rstrip()
    except Exception:
        # It doesn't matter, why it failed (no 'git' command in $PATH or no
        # such config variable)
        die("error: couldn't find 'travis.slug' config variable")
else:
    reposlug = args.reposlug

access_token = get_travis_access_token()

url = 'https://api.travis-ci.org/repo/'
url += reposlug.replace("/", "%2F")
url += '/'
url += args.resource
url += '?limit=' + str(args.count)
url += '&offset=0'
url += '&include=build.jobs'
url += '&sort_by=last_build:desc'

req_headers = {
    'Travis-API-Version': '3',
    'Authorization': 'token ' + get_travis_access_token(),
    'User-Agent': 'travis-compact-status.py/0.0.1'
}

response = requests.get(url, headers=req_headers)
response.raise_for_status()

if args.use_color:
    states_to_letters = {
        'created':  '\033[033mc\033[0m',
        'queued':   '\033[033mq\033[0m',
        'received': '\033[034mb\033[0m',   # web says "booting"
        'started':  '\033[034ms\033[0m',
        'passed':   '\033[032mP\033[0m',
        'errored':  '\033[031m!\033[0m',
        'failed':   '\033[031mX\033[0m',
        'canceled': '_'
    }
else:
    states_to_letters = {
        'created':  'c',
        'queued':   'q',
        'received': 'b',   # web says "booting"
        'started':  's',
        'passed':   'P',
        'errored':  '!',
        'failed':   'X',
        'canceled': '_'
    }

if args.resource == 'branches':
    max_jobs = len(max(response.json()['branches'], key=lambda b:len(b['last_build']['jobs']))['last_build']['jobs'])
    for branch in response.json()['branches']:
        states = ''
        for job in branch['last_build']['jobs']:
            states += states_to_letters[job['state']]
        for i in range(0, max_jobs - len(branch['last_build']['jobs'])):
            states += ' '
        print(states + ' ' + branch['last_build']['number'] + '  ' + branch['name'])
elif args.resource == 'builds':
    max_jobs = len(max(response.json()['builds'], key=lambda b:len(b['jobs']))['jobs'])
    for build in response.json()['builds']:
        states = ''
        for job in build['jobs']:
            states += states_to_letters[job['state']]
        for i in range(0, max_jobs - len(build['jobs'])):
            states += ' '
        print(states + ' ' + build['number'] + '  ' + build['branch']['name'])
