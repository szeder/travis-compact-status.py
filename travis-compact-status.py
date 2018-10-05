#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Copyright 2018 SZEDER Gábor

import argparse
import os
import requests
import sys
import yaml

def die(msg):
    print(msg)
    exit(1)

def get_travis_access_token():
    errmsg = "error: couldn't read Travis CI API access token: "
    try:
        with open(os.environ['HOME'] + '/.travis/config.yml', 'r') as f:
            return yaml.load(f)['endpoints']['https://api.travis-ci.org/']['access_token']
    except KeyError as e:
        die(errmsg + 'No such key: ' + str(e))
    except Exception as e:
        die(errmsg + str(e))


parser = argparse.ArgumentParser()
parser.add_argument('resource', choices=['branches', 'builds'],
    help="list branches or builds")
parser.add_argument('reposlug', metavar='repo-slug',
    help="<username>/<reponame>")

args = parser.parse_args()

access_token = get_travis_access_token()

url = 'https://api.travis-ci.org/repo/'
url += args.reposlug.replace("/", "%2F")
url += '/'
url += args.resource
url += '?limit=20'
url += '&offset=0'
url += '&include=build.jobs'
url += '&sort_by=last_build:desc'

req_headers = {
    'Travis-API-Version': '3',
    'Authorization': 'token ' + get_travis_access_token()
}

response = requests.get(url, headers=req_headers)
response.raise_for_status()

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
    for branch in response.json()['branches']:
        states = ''
        for job in branch['last_build']['jobs']:
            states += states_to_letters[job['state']]
        print(states + '  ' + branch['name'])
elif args.resource == 'builds':
    for build in response.json()['builds']:
        states = ''
        for job in build['jobs']:
            states += states_to_letters[job['state']]
        print(states + '  ' + build['branch']['name'])
