#!/usr/bin/env python

#######################################################################
userdict = {
    "codeguru" : "codeguru42"
    # provide your sourceforge -> github user name mappings here.
    # syntax:
    # "old_sf_user": "NewGitHubUser",
    # "another": "line",
    # "last": "line"
}
#######################################################################

import json
import requests
import re
from getpass import getpass
from pprint import pprint

import issue
import milestone

json_file=open('tickets.json')
json_data = json.load(json_file)

json_file.close()

# Get username and password
username  = "codeguru42"
password = getpass('%s\'s GitHub password: ' % username)
auth = (username, password)
repo = "BBCTImport"

print("Fetching milestones...")
milestoneNumbers = milestone.getMilestoneNumbers(username, password, repo)
print("Milestones: " + str(len(milestoneNumbers)))

###################
#  UPDATE ISSUES  #
###################
print("Fetching issues...")
githubIssues = issue.getGitHubIssues(username, password, repo)
print("Issues: " + str(len(githubIssues)))

sfTickets = json_data['tickets']
closedStatusNames = json_data['closed_status_names']

successes = 0
failures = 0
for issue in githubIssues:
    print("Updating issue: " + issue['title'] + "...")

    sfTicket = [ticket for ticket in sfTickets if ticket['summary'] == issue['title']][0]

    updateData = {
        'title' : issue['title']
    }
    milestone = sfTicket['custom_fields']['_milestone']
    if milestone in milestoneNumbers:
        updateData['milestone'] = milestoneNumbers[milestone]
    assignedTo = sfTicket['assigned_to']
    if assignedTo != "nobody":
        if assignedTo in userdict:
            updateData['assignee'] = userdict[assignedTo]
        else:
            updateData['assignee'] = assignedTo
    status = sfTicket['status']
    if status in closedStatusNames:
        updateData['state'] = "closed"

    response = requests.patch(issue['url'], data=json.dumps(updateData), auth=auth)
    if response.status_code == requests.codes.ok:
        successes += 1
    else:
        print(str(response.status_code) + ": " + response.json()['message'])
        failures += 1

issueCount = successes + failures
print("Issues: " + str(issueCount) + " Sucess: " + str(successes) + " Failure: " + str(failures))
