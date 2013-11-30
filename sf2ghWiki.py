#!/usr/bin/env python
import json
import requests
from getpass import getpass
from pprint import pprint

import milestone
import issue

import optparse
import sys

parser = optparse.OptionParser(usage='Usage: %prog [options] <sfexport>.json <local-repo>\n\tIf the -u option is not specified, repoowner will be used as\n\tusername.\n\tYou might want to edit %prog with a text editor and set\n\tup the userdict = {...} accordingly, for mapping user names.')
parser.add_option('-s', '--start', dest='start_id', action='store', help='id of first issue to import; useful for aborted runs')
parser.add_option('-u', '--user', dest='github_user')
parser.add_option("-T", "--no-id-in-title", action="store_true", dest="no_id_in_title", help="do not append '[sf#12345]' to issue titles")
opts, args = parser.parse_args()

try:
    json_file_name, path = args
except (ValueError, IndexError):
    parser.print_help()
    sys.exit(1)

json_file=open(json_file_name)
json_data = json.load(json_file)
json_file.close()

wikiPages = json_data['pages']

for wiki in wikiPages:
    print "Creating '" + wiki['title'] + "'..."
    filename = wiki['title'] + ".md"

    file = open(path + '/' + filename, 'w')
    file.write(wiki['text'])
    file.close()
