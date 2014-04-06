#!/usr/bin/env python
import json
import requests
import textwrap
from getpass import getpass

import milestone
import issue

import argparse

def load_json(filename):
    with open(filename) as stream:
        return json.load(stream)

usage = textwrap.dedent("""
    %(prog)s [options] <sfexport>.json <repoowner>/<repo>
    \tIf the -u option is not specified, repoowner will be used as
    \tusername.
    \tYou might want to edit %(prog)s with a text editor and set
    \tup the userdict = {...} accordingly, for mapping user names.
    """).lstrip()
parser = argparse.ArgumentParser(usage=usage)
parser.add_argument('input_file', help="JSON export from Sourceforge")
parser.add_argument('repo', help="Repo name as <owner>/<project>")
parser.add_argument('-s', '--start', dest='start_id', action='store',
    help='id of first issue to import; useful for aborted runs')
parser.add_argument('-u', '--user', dest='github_user')
parser.add_argument("-T", "--no-id-in-title", action="store_true",
    dest="no_id_in_title", help="do not append '[sf#12345]' to issue titles")
parser.add_argument('-U', '--user-map',
    help="A json file mapping SF username to GitHub username", default={},
    type=load_json)
args = parser.parse_args()

username = args.github_user or args.repo.split('/')[0]

issue.userdict.update(args.user_map)

with open(args.input_file) as export_stream:
    export = json.load(export_stream)

# Get password
password = getpass('%s\'s GitHub password: ' % username)
auth = (username, password)

def getCollaborators(auth, repo):
    collaborators = []
    url = 'https://api.github.com/repos/' + repo + '/collaborators'
    response = requests.get(url, auth=auth)
    if response.status_code == requests.codes.ok:
        detailed_collaborators = response.json()
        for user in detailed_collaborators:
            print("Login: {0}".format(user['login']))
            collaborators.append(user['login'])
    else:
        print(str(response.status_code) + ": " + response.json()['message'])
    return collaborators
    
def createGitHubArtifact(sfArtifacts, githubName, conversionFunction):
    print("-----------------")
    print(githubName.upper())
    print("-----------------")

    successes = 0
    failures = 0

    for sfArtifact in sfArtifacts:
        ghArtifact = conversionFunction(sfArtifact)

        print("Adding " + githubName + " " + ghArtifact['title'] + "...")
        response = requests.post(
            'https://api.github.com/repos/' + args.repo + '/' + githubName,
            data=json.dumps(ghArtifact),
            auth=auth)

        if response.status_code == 201:
            successes += 1
        else:
            print(str(response.status_code) + ": " + response.json()['message'])
            failures += 1

    total = successes + failures
    print(githubName + ": " + str(total) + " Success: " + str(successes)
        + " Failure: " + str(failures))

collaborators = getCollaborators(auth, args.repo)

createGitHubArtifact(export['milestones'], "milestones", milestone.sf2github)
tickets = sorted(export['tickets'], key=lambda t: t['ticket_num'])
createGitHubArtifact(tickets, "issues", issue.sf2github)
issue.updateAllIssues(auth, args.repo, export, not args.no_id_in_title, collaborators)
