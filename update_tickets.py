#!/usr/bin/env python
import json
from requests import codes
from getpass import getpass
from pprint import pprint

import issue

json_file=open('tickets.json')
json_data = json.load(json_file)
json_file.close()

# Get username and password
username  = "codeguru42"
password = getpass('%s\'s GitHub password: ' % username)
auth = (username, password)
repo = "BBCTImport"

issue.updateAllIssues(username, password, repo, json_data)
