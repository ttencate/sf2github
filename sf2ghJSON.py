#!/usr/bin/env python
import json
import milestone

json_data=open('tickets.json')

data = json.load(json_data)

for d in data.keys():
    print(d)

##############
# MILESTONES #
##############
print("-----------------")
print("MILESTONES")
print("-----------------")
sfMilestones = data["milestones"]
githubMilestones = map(milestone.sf2github, sfMilestones)

for m in githubMilestones:
    print(m["title"])

##############
# TICKETS    #
##############
print("-----------------------------------------")
print("TICKETS")
print("-----------------------------------------") 
for key in data["tickets"][0]:
    print(key)

json_data.close()
