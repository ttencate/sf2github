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

def createGitHubArtifact(sfName, githubName, conversionFunction):
    print("-----------------")
    print(githubName.upper())
    print("-----------------")

    successes = 0
    failures = 0

    for sfArtifact in data[sfName]:
        ghArtifact = conversionFunction(sfArtifact)

        print("Adding " + githubName + " " + ghArtifact['title'] + "...")
        response = requests.post(
            'https://api.github.com/repos/' + username + '/' + repo + '/' + githubName,
            data=json.dumps(ghArtifact),
            auth=(username, password))

        if response.status_code == 201:
            successes += 1
        else:
            print(str(response.status_code) + ": " + response.json()['message'])
            failures += 1

    total = successes + failures
    print(githubName + ": " + str(total) + " Success: " + str(successes) + " Failure: " + str(failures))

createGitHubArtifact("milestones", "milestones", milestone.sf2github)
createGitHubArtifact("tickets", "issues", issue.sf2github)
