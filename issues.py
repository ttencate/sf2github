#!/usr/bin/env python

import better_exchook
better_exchook.install()

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

from urllib import urlencode
from urllib2 import Request, urlopen
from base64 import b64encode
from time import sleep
from getpass import getpass
import re

def rest_call(before, after, data_dict=None):
    global github_user, github_password
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

started = opts.start_id is None
def handle_tracker_item(item, issue_title_prefix):
    global started
    if not started:
        if item.id.string == opts.start_id:
            started = True
        else:
            return

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

items = []
for tracker in trackers:
    trackeritems = tracker.tracker_items('tracker_item', recursive=False)
    trackername = tracker.description.string
    print "Found tracker:", trackername, ",", len(trackeritems), "items"
    trackername = trackername.replace("Tracking System", "")
    trackername = trackername.strip()
    
    issue_title_prefix = None
    for item in trackeritems:
        if issue_title_prefix is None:
            issue_title_prefix = getIssueTitlePrefix(trackername)
        items.append((item, issue_title_prefix))

print "Found", len(items), "items in", len(trackers), "trackers."

userVerify("Everything ok, should I really start?")
github_password = getpass('%s\'s GitHub password: ' % github_user)
for item, issue_title_prefix in items:
    handle_tracker_item(item, issue_title_prefix)
    
