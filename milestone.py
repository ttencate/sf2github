import json
import requests
from datetime import datetime

def sf2github(sfMilestone):
    state = "closed" if sfMilestone["complete"] else "open"
    ghMilestone = {
        'title' : sfMilestone["name"],
        'state' : state,
    }

    if sfMilestone["description"] != "":
        ghMilestone["description"] = sfMilestone["description"]

    if sfMilestone["due_date"] != "":
        sfDate = datetime.strptime(sfMilestone["due_date"], "%m/%d/%Y")
        ghMilestone['due_on'] = sfDate.strftime("%Y-%m-%d") + "T00:00:00Z"

    return ghMilestone

def getMilestoneNumbers(username, password, repo):
    milestoneNumbers = {}

    for state in ['open', 'closed']:
        stateJSON = {'state' : state}
        url = 'https://api.github.com/repos/' + username + '/' + repo + '/milestones' 
        auth = (username, password)
        response = requests.get(url, params=stateJSON, auth=auth)

        if response.status_code == requests.codes.ok:
            milestones = response.json()
            for milestone in milestones:
                milestoneNumbers[milestone['title']] = milestone['number']
        else:
            print(str(response.status_code) + ": " + response.json()['message'])

    return milestoneNumbers
