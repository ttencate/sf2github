#!/usr/bin/env python

import better_exchook
better_exchook.install()

import sys
import optparse

parser = optparse.OptionParser(usage='Usage: %prog [options] sfexport.xml githubuser/repo')
parser.add_option('-s', '--start', dest='start_id', action='store', help='id of first issue to import; useful for aborted runs')
parser.add_option('-u', '--user', dest='github_user')
opts, args = parser.parse_args()

try:
    xml_file_name, github_repo = args
    github_user = github_repo.split('/')[0]
except (ValueError, IndexError):
    parser.print_help()
    sys.exit(1)

if opts.github_user:
    github_user = opts.github_user

from BeautifulSoup import BeautifulStoneSoup

print 'Parsing XML export...'
soup = BeautifulStoneSoup(open(xml_file_name, 'r'), convertEntities=BeautifulStoneSoup.ALL_ENTITIES)

trackers = soup.document.find('trackers', recursive=False).findAll('tracker', recursive=False)

from urllib import urlencode
from urllib2 import HTTPError
from base64 import b64encode
from time import sleep
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
import json
import re

def __rest_call_unchecked(method, request, data=None):
    global github_repo, github_user, github_password
    url = 'https://api.github.com/repos/%s/%s' % (github_repo, request)
    if method == 'PATCH':
        response = requests.patch(url, data=json.dumps(data), auth=HTTPBasicAuth(github_user, github_password))
    else:
        response = requests.post(url, data=json.dumps(data), auth=HTTPBasicAuth(github_user, github_password))
    # GitHub limits API calls to 60 per minute
    sleep(1)
    return response

def rest_call(method, request, data=None):
    count500err = 0
    while True:
        try:
            return __rest_call_unchecked(method, request, data)
        except HTTPError, e:
            print "Got HTTPError:", e
            l = data_dict and max(map(len, data_dict.itervalues())) or 0
            if e.code == 413 or l >= 100000: # Request Entity Too Large
                assert l > 0
                print "Longest value has len", l, "; now we are trying with half of that"
                l /= 2
                data_dict = dict(map(lambda (k,v): (k,v[0:l]), data_dict.iteritems()))
                continue
            elif e.code == 500:
                N = 5
                if count500err >= N: raise e
                print "Waiting 10 seconds, will try", (N - count500err), "more times"
                sleep(10)
                count500err += 1
                continue
            raise e # reraise, we cannot handle it

def labelify(string):
    return re.sub(r'[^a-z0-9._-]+', '-', string.lower())

closed_status_ids = set()
for tracker in trackers:
    for status in tracker.statuses('status', recursive=False):
        status_id = status.id.string
        status_name = status.nameTag.string
        if status_name in ['Closed', 'Deleted']:
            closed_status_ids.add(status_id)
print "closed_status_ids:", closed_status_ids

groups = {}
for tracker in trackers:
    for group in tracker.groups('group', recursive=False):
        groups[group.id.string] = group.group_name.string
print "groups:", groups

categories = {}
for category in tracker.categories('category', recursive=False):
    categories[category.id.string] = category.category_name.string
print "categories:", categories

def handle_tracker_item(item, issue_title_prefix):
    if len(issue_title_prefix) > 0:
        issue_title_prefix = issue_title_prefix.strip() + " "
        
    title = issue_title_prefix + item.summary.string
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

    print 'Creating: %s [%s] (%d comments)%s for SF #%s' % (title, ','.join(labels), len(comments), ' (closed)' if closed else '', item.id.string)
    response = rest_call('POST', 'issues', {'title': title, 'body': body})
    if response.status_code == 500:
        print "ISSUE CAUSED SERVER SIDE ERROR AND WAS NOT SAVED!!! Import will continue."
    else:
        issue = response.json
        if 'number' not in issue:
            raise RuntimeError("No 'number' in issue; response %d invalid" % response.status_code)
        number = issue['number']
        print 'Attaching labels: %s' % labels
        rest_call('POST', 'issues/%s/labels' % (number), labels)
        for comment in comments:
            print 'Creating comment: %s' % comment[:50].replace('\n', ' ').replace(chr(13), '')
            rest_call('POST', 'issues/%s/comments' % (number), {'body': comment})
        if closed:
            print 'Closing...'
            rest_call('PATCH', 'issues/%s' % (number), {'state': 'closed'})


import signal
def signal_handler(signal, frame):
	print 'You pressed Ctrl+C!'
	import sys
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

import readline
readline.parse_and_bind("tab: complete")
readline.parse_and_bind("set show-all-if-ambiguous on")

class Completer:
    def __init__(self, words):
        self.words = words
        self.prefix = None

    def complete(self, prefix, index):
        if prefix != self.prefix:
            self.matching_words = [w for w in self.words if w.startswith(prefix)]
            self.prefix = prefix
        else:
            pass                
        try:
            return self.matching_words[index]
        except IndexError:
            return None

def userRawInput(prompt):
    readline.set_completer(None)
    s = raw_input(prompt)
    return s

def userInput(words, prompt=""):
	readline.set_completer(Completer(words).complete)
	while True:
		s = raw_input((prompt + " ").lstrip() + "Choice of [" + ", ".join(words) + "] ? ")
		if s in words: return s
		print "Error: '" + s + "' unknown, please try again"

def userVerify(txt, abortOnFail=True):
    if userInput(["yes","no"], txt) != 'yes':
        if abortOnFail:
            print "Aborted."
            sys.exit(1)
        return False
    return True

def getIssueTitlePrefix(trackername):
    prefixes = {
        "Bug": "",
        "Feature Request": "[Feature]",
        "Patch": "[Patch]",
        "Tech Support": "[Support]"
        }
    if trackername in prefixes:
        return prefixes[trackername]
    
    prefix = "[" + trackername + "]"
    if not userVerify("Tracker '" + trackername + "' is unknown,"
        + "I would use the prefix '" + prefix + "', ok?", False):
        
        while True:
            prefix = userRawInput("Please enter a prefix: ")
            if userVerify("Is prefix '" + prefix + "' ok?"):
                break
    return prefix

skipped_count = 0
started = opts.start_id is None
items = []
for tracker in trackers:
    trackeritems = tracker.tracker_items('tracker_item', recursive=False)
    trackername = tracker.description.string
    print "Found tracker:", trackername, ",", len(trackeritems), "items"
    trackername = trackername.replace("Tracking System", "")
    trackername = trackername.strip()
    
    issue_title_prefix = None
    for item in trackeritems:
        if not started:
            if item.id.string == opts.start_id:
                started = True
            else:
                skipped_count += 1
                continue

        if issue_title_prefix is None:
            issue_title_prefix = getIssueTitlePrefix(trackername)
        items.append((item, issue_title_prefix))

print "Found", len(items), "items (" + str(skipped_count) + " skipped) in", len(trackers), "trackers."

userVerify("Everything ok, should I really start?")
github_password = getpass('%s\'s GitHub password: ' % github_user)
for item, issue_title_prefix in items:
    handle_tracker_item(item, issue_title_prefix)
    
