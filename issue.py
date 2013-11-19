import json
import requests
import re

def sf2github(sfTickets):
    return {
        'title' : sfTickets["summary"],
        'body' : sfTickets["description"],
    }

def getGitHubIssues(username, password, repo):
    auth = (username, password)
    githubIssues = []
    url = 'https://api.github.com/repos/' + username + '/' + repo + '/issues'
    links = dict([('next', url)])
    while "next" in links:
        response = requests.get(links['next'], auth=auth)
        if response.status_code == requests.codes.ok:
            githubIssues.extend(response.json())
        else:
            print(str(response.status_code) + ": " + response.json()['message'])

        links = dict((rel, url) for url, rel in re.findall('<(.*?)>; rel="(.*?)"', response.headers['link']))

    return githubIssues

def updateIssue(githubIssue, sfTicket, auth, milestoneNumbers, userdict, closedStatusNames):
    updateData = {
        'title' : githubIssue['title']
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

    response = requests.patch(githubIssue['url'], data=json.dumps(updateData), auth=auth)
    message = response.json()['message'] if 'message' in response.json() else None
    return (response.status_code, message)
