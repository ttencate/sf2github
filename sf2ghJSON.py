#!/usr/bin/env python
import json
import milestone
import issue

json_data=open('tickets.json')
data = json.load(json_data)
json_data.close()

for d in data.keys():
    print(d)

##############
# MILESTONES #
##############
print("-----------------")
print("MILESTONES")
print("-----------------")

sfMilestones = data["milestones"]
ghMilestones = map(milestone.sf2github, sfMilestones)

for m in ghMilestones:
    print(m)

##############
# TICKETS    #
##############
print("-----------------")
print("TICKETS")
print("-----------------")

sfTickets = data["tickets"]
ghIssues = map(issue.sf2github, sfTickets)
print(ghIssues)
