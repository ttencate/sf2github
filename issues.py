#!/usr/bin/env python

import sys
import optparse

parser = optparse.OptionParser(usage='Usage: %prog [options] sfexport.xml githubuser/repo')
parser.add_option('-s', '--start', dest='start_id', action='store', help='id of first issue to import; useful for aborted runs')
opts, args = parser.parse_args()

try:
    xml_file_name, github_repo = args
    github_user = github_repo.split('/')[0]
except (ValueError, IndexError):
    parser.print_help()
    sys.exit(1)

from BeautifulSoup import BeautifulStoneSoup

print 'Parsing XML export...'
soup = BeautifulStoneSoup(open(xml_file_name, 'r'), convertEntities=BeautifulStoneSoup.ALL_ENTITIES)

trackers = soup.document.find('trackers', recursive=False).findAll('tracker', recursive=False)
assert len(trackers) == 1, 'Multiple trackers not yet supported, sorry'
tracker = trackers[0]

from urllib import urlencode
from urllib2 import Request, urlopen
from base64 import b64encode
from time import sleep
from getpass import getpass
import re

github_password = getpass('%s\'s GitHub password: ' % github_user)

def rest_call(before, after, data_dict=None):
    url = 'https://github.com/api/v2/xml/%s/%s/%s' % (before, github_repo, after)
    if data_dict is None:
        data = None
    else:
        data = urlencode([(unicode(key).encode('utf-8'), unicode(value).encode('utf-8')) for key, value in data_dict.iteritems()])
    headers = {
        'Authorization': 'Basic %s' % b64encode('%s:%s' % (github_user, github_password)),
    }
    request = Request(url, data, headers)
    response = urlopen(request)
    # GitHub limits API calls to 60 per minute
    sleep(1)
    return response

def labelify(string):
    return re.sub(r'[^a-z0-9._-]+', '-', string.lower())

closed_status_ids = []
for status in tracker.statuses('status', recursive=False):
    status_id = status.id.string
    status_name = status.nameTag.string
    if status_name in ['Closed', 'Deleted']:
        closed_status_ids.append(status_id)

groups = {}
for group in tracker.groups('group', recursive=False):
    groups[group.id.string] = group.group_name.string

categories = {}
for category in tracker.categories('category', recursive=False):
    categories[category.id.string] = category.category_name.string

started = opts.start_id is None
for item in tracker.tracker_items('tracker_item', recursive=False):
    if not started:
        if item.id.string == opts.start_id:
            started = True
        else:
            continue
    title = item.summary.string
    body = '\n\n'.join([
        'Converted from [SourceForge issue %s](%s), submitted by %s' % (item.id.string, item.url.string, item.submitter.string),
        item.details.string,
    ])
    closed = item.status_id.string in closed_status_ids
    labels = []
    try:
        labels.append(labelify(groups[item.group_id.string]))
    except KeyError:
        pass
    try:
        labels.append(labelify(categories[item.category_id.string]))
    except KeyError:
        pass

    comments = []
    for followup in item.followups('followup', recursive=False):
        comments.append('\n\n'.join([
            'Submitted by %s' % followup.submitter.string,
            followup.details.string,
        ]))

    print 'Creating: %s [%s] (%d comments)%s' % (title, ','.join(labels), len(comments), ' (closed)' if closed else '')
    response = rest_call('issues/open', '', {'title': title, 'body': body})
    issue = BeautifulStoneSoup(response, convertEntities=BeautifulStoneSoup.ALL_ENTITIES)
    number = issue.number.string
    for label in labels:
        print 'Attaching label: %s' % label
        rest_call('issues/label/add', '%s/%s' % (label, number))
    for comment in comments:
        print 'Creating comment: %s' % comment[:50].replace('\n', ' ')
        rest_call('issues/comment', number, {'comment': comment})
    if closed:
        print 'Closing...'
        rest_call('issues/close', number)

