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

import milestone

def sf2github(sfTicket):
    return {
        'title' : sfTicket['summary'],
        'body' : sfTicket['description'],
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
        'title' : githubIssue['title'] + " [sf#" + str(sfTicket['ticket_num']) + "]"
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

def updateAllIssues(username, password, repo, json_data):
    auth = (username, password)

    print("Fetching milestones...")
    milestoneNumbers = milestone.getMilestoneNumbers(username, password, repo)
    print("Milestones: " + str(len(milestoneNumbers)))

    print("Fetching issues...")
    githubIssues = getGitHubIssues(username, password, repo)
    print("Issues: " + str(len(githubIssues)))

    sfTickets = json_data['tickets']
    closedStatusNames = json_data['closed_status_names']

    successes = 0
    failures = 0
    for githubIssue in githubIssues:
        print("Updating issue: " + githubIssue['title'] + "...")

        sfTicket = [ticket for ticket in sfTickets if ticket['summary'] == githubIssue['title']][0]
        (statusCode, message) = updateIssue(githubIssue, sfTicket, auth, milestoneNumbers, userdict, closedStatusNames)
        if statusCode == requests.codes.ok:
            successes += 1
        else:
            print(str(statusCode) + ": " + message)
            failures += 1

        addAllComments(auth, githubIssue['url'], sfTicket['discussion_thread']['posts'])

    issueCount = successes + failures
    print("Issues: " + str(issueCount) + " Sucess: " + str(successes) + " Failure: " + str(failures))

def addAllComments(auth, issueURL, sfPosts):
    print("  Adding comments...")
    successes = 0
    failures = 0
    for sfPost in sfPosts:
        (statusCode, message) = addComment(auth, issueURL, sfPost['text'])
        if statusCode == 201:
            successes += 1
        else:
            print(str(statusCode) + ": " + message)
            failures += 1

    commentCount = successes + failures
    print("  Comments: " + str(commentCount) + " Sucess: " + str(successes) + " Failure: " + str(failures))

def addComment(auth, issueURL, body):
    response = requests.post(issueURL + "/comments", data=json.dumps({'body' : body}), auth=auth)
    message = response.json()['message'] if 'message' in response.json() else None
    return (response.status_code, message)
