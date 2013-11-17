#!/usr/bin/env python
import json
import requests
from getpass import getpass

json_file=open('tickets.json')
json_data = json.load(json_file)
json_file.close()

# Get username and password
username  = "codeguru42"
password = getpass('%s\'s GitHub password: ' % username)
repo = "BBCTImport"

#####################
# MILESTONE NUMBERS #
#####################
milestoneNumbers = {}

for state in ['open', 'closed']:
    print("***" + state)
    stateJSON = {'state' : state}
    print(json.dumps(stateJSON))
    response = requests.get(
        'https://api.github.com/repos/' + username + '/' + repo + '/milestones',
        params=stateJSON,
        auth=(username, password))

    milestones = response.json()
    for milestone in milestones:
        print(milestone['title'] + " " + str(milestone['number']))
        milestoneNumbers[milestone['title']] = milestone['number']
