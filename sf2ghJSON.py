#!/usr/bin/env python
import json
import requests
from getpass import getpass

import milestone
import issue

import optparse
import sys

parser = optparse.OptionParser(usage='Usage: %prog [options] <sfexport>.json <repoowner>/<repo>\n\tIf the -u option is not specified, repoowner will be used as\n\tusername.\n\tYou might want to edit %prog with a text editor and set\n\tup the userdict = {...} accordingly, for mapping user names.')
parser.add_option('-s', '--start', dest='start_id', action='store', help='id of first issue to import; useful for aborted runs')
parser.add_option('-u', '--user', dest='github_user')
parser.add_option("-T", "--no-id-in-title", action="store_true", dest="no_id_in_title", help="do not append '[sf#12345]' to issue titles")
opts, args = parser.parse_args()

try:
    json_file_name, repo = args
    username = repo.split('/')[0]
except (ValueError, IndexError):
    parser.print_help()
    sys.exit(1)

if opts.github_user:
    username = opts.github_user

json_file=open(json_file_name)
json_data = json.load(json_file)
json_file.close()

# Get password
password = getpass('%s\'s GitHub password: ' % username)
auth = (username, password)

def createGitHubArtifact(sfName, githubName, conversionFunction):
    print("-----------------")
    print(githubName.upper())
    print("-----------------")

    successes = 0
    failures = 0

    for sfArtifact in json_data[sfName]:
        ghArtifact = conversionFunction(sfArtifact)

        print("Adding " + githubName + " " + ghArtifact['title'] + "...")
        response = requests.post(
            'https://api.github.com/repos/' + repo + '/' + githubName,
            data=json.dumps(ghArtifact),
            auth=auth)

        if response.status_code == 201:
            successes += 1
        else:
            print(str(response.status_code) + ": " + response.json()['message'])
            failures += 1

    total = successes + failures
    print(githubName + ": " + str(total) + " Success: " + str(successes) + " Failure: " + str(failures))

createGitHubArtifact("milestones", "milestones", milestone.sf2github)
createGitHubArtifact("tickets", "issues", issue.sf2github)
