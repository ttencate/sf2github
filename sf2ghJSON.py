#!/usr/bin/env python
import json
import requests
from getpass import getpass

import milestone
import issue

json_data=open('tickets.json')
data = json.load(json_data)
json_data.close()

# Get username and password
username  = "codeguru42"
password = getpass('%s\'s GitHub password: ' % username)
repo = "BBCTImport"

##############
# MILESTONES #
##############
print("-----------------")
print("MILESTONES")
print("-----------------")

successes = 0
failures = 0
milestoneNums = {}

for sfMilestone in data["milestones"]:
    ghMilestone = milestone.sf2github(sfMilestone)
    response = requests.post(
        'https://api.github.com/repos/' + username + '/' + repo + '/milestones',
        data=json.dumps(ghMilestone),
        auth=(username, password))

    print("Adding milestone " + ghMilestone['title'] + "...")

    if response.status_code == 201:
        successes += 1
        milestoneNums[ghMilestone['title']] = response.json()['number']
    else:
        print(str(response.status_code) + ": " + response.json()['message'])
        print(ghMilestone)
        failures += 1

total = successes + failures
print("Milestones: " + str(total) + " Success: " + str(successes) + " Failure: " + str(failures))

print(milestoneNums)
response = requests.get(
    'https://api.github.com/repos/' + username + '/' + repo + '/milestones/' + str(milestoneNums['lite 0.5.3.1']),
    data=json.dumps(ghMilestone),
    auth=(username, password))
print(response.json())

##############
# TICKETS    #
##############
print("-----------------")
print("TICKETS")
print("-----------------")

sfTickets = data["tickets"]
ghIssues = map(issue.sf2github, sfTickets)
