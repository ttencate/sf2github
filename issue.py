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
