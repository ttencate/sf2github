#!/usr/bin/env python
import json
import requests
import re
from getpass import getpass
from pprint import pprint

import milestone

json_file=open('tickets.json')
json_data = json.load(json_file)
closedStatusNames = json_data['closed_status_names']
json_file.close()

# Get username and password
username  = "codeguru42"
password = getpass('%s\'s GitHub password: ' % username)
auth = (username, password)
repo = "BBCTImport"

milestoneNumbers = milestone.getMilestoneNumbers(username, password, repo)

# Get first page of issues
issueCount = 0
url = 'https://api.github.com/repos/' + username + '/' + repo + '/issues'
links = dict([('next', url)])

while "next" in links:
    response = requests.get(links['next'], auth=auth)
    links = dict((rel, url) for url, rel in re.findall('<(.*?)>; rel="(.*?)"', response.headers['link']))
    print(links)

    githubIssues = response.json()
    for issue in githubIssues:
        pprint(issue['title'])
        issueCount += 1

print("Issues: " + str(issueCount))
