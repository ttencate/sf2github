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
from requests import codes
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
for githubIssue in githubIssues:
    print("Updating issue: " + githubIssue['title'] + "...")

    sfTicket = [ticket for ticket in sfTickets if ticket['summary'] == githubIssue['title']][0]
    (statusCode, message) = issue.updateIssue(githubIssue, sfTicket, auth, milestoneNumbers, userdict, closedStatusNames)
    if statusCode == codes.ok:
        successes += 1
    else:
        print(str(statusCode) + ": " + message)
        failures += 1

issueCount = successes + failures
print("Issues: " + str(issueCount) + " Sucess: " + str(successes) + " Failure: " + str(failures))
