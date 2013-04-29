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

from bs4 import BeautifulSoup

print 'Parsing XML export...'
soup = BeautifulSoup(open(xml_file_name, 'r'), ['lxml'])
#convertEntities=BeautifulStoneSoup.ALL_ENTITIES)

trackers = soup.find_all('artifact')

from time import sleep
from getpass import getpass
import requests
import json
import re

def __rest_call_unchecked(method, request, data=None):
    global github_repo, github_user, github_password
    url = 'https://api.github.com/repos/%s/%s' % (github_repo, request)
    if method == 'PATCH':
        response = requests.patch(url, data=json.dumps(data), auth=(github_user, github_password))
    else:
        response = requests.post(url, data=json.dumps(data), auth=(github_user, github_password))
    # GitHub limits API calls to 60 per minute
    sleep(1)
    return response

def rest_call(method, request, data=None):
    count500err = 0
    while True:
        try:
            return __rest_call_unchecked(method, request, data)
        except requests.HTTPError, e:
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
    status = tracker.find('field',attrs={'name':'status'})
    status_id = status.parent.find('field',attrs={'name':'artifact_id'}).string
    status_name = status.string
    if status_name in ['Closed', 'Deleted']:
        closed_status_ids.add(status_id)
print "closed_status_ids:", closed_status_ids

groups = set()
for tracker in trackers:
    group = tracker.find('field',attrs={'name':'artifact_type'})
    groups.add(group.string)
print "groups:", groups

categories = set()
for tracker in trackers:
    category = tracker.find('field',attrs={'name':'category'})
    categories.add(category.string)
print "categories:", categories

def handle_tracker_item(item, issue_title_prefix):
    if len(issue_title_prefix) > 0:
        issue_title_prefix = issue_title_prefix.strip() + " "

    title = issue_title_prefix + item.find('field',attrs={'name':'summary'}).string
    item_id = item.find('field',attrs={'name':'artifact_id'}).string
    item_submitter = item.find('field',attrs={'name':'submitted_by'}).string
    item_details = item.find('field',attrs={'name':'details'}).string
    body = '\n\n'.join([
        'Converted from [SourceForge issue %s], submitted by %s' % (item_id, item_submitter),
        item_details,
    ])
    closed = item_id in closed_status_ids
    labels = []
    try:
        labels.append(labelify(item.find('field',attrs={'name':'artifact_id'}).string))
    except KeyError:
        pass
    try:
        category = labelify(item.find('field',attrs={'name':'category'}).string)
        if category != "none":
          labels.append(category)
    except KeyError:
        pass

    comments = []
    messages = item.findAll('message',recursive=True)
    for followup in messages:
        # workaround BeautifulSoup parsing error (?)
        if len(followup.findAll('field')) == 0:
          continue
        comments.insert(0,'\n\n'.join([
            'Submitted by %s' % followup.find('field',attrs={'name':'user_name'}).string,
            followup.find('field',attrs={'name':'body'}).string,
        ]))

    print 'Creating: %s [%s] (%d comments)%s for SF #%s' % (title, ','.join(labels), len(comments), ' (closed)' if closed else '', item_id)
    response = rest_call('POST', 'issues', {'title': title, 'body': body})
    if response.status_code == 500:
        print "ISSUE CAUSED SERVER SIDE ERROR AND WAS NOT SAVED!!! Import will continue."
    else:
        issue = json.loads(response.content)
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
        "Bugs": "",
        "Feature Request": "[Feature]",
        "Patch": "[Patch]",
        "Tech Support": "[Support]"
        }
    if trackername in prefixes:
        return prefixes[trackername]
    
    prefix = "[" + trackername + "]"
    if not userVerify("Tracker '" + trackername + "' is unknown, "
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
    trackername = tracker.find('field',attrs={'name':'artifact_type'}).string
    trackername = trackername.replace("Tracking System", "")
    trackername = trackername.strip()
    
    issue_title_prefix = None
    if not started:
        if tracker.find('field',attrs={'name':'artifact_id'}).string == opts.start_id:
            started = True
        else:
            skipped_count += 1
            continue

    if issue_title_prefix is None:
        issue_title_prefix = getIssueTitlePrefix(trackername)
    items.append((tracker, issue_title_prefix))

print "Found", len(items), "items (" + str(skipped_count) + " skipped) in", len(trackers), "trackers."

userVerify("Everything ok, should I really start?")
github_password = getpass('%s\'s GitHub password: ' % github_user)
for item, issue_title_prefix in items:
    handle_tracker_item(item, issue_title_prefix)
    
