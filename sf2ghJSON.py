#!/usr/bin/env python
import json
from pprint import pprint

json_data=open('tickets.json')

data = json.load(json_data)

for d in data.keys():
    pprint(d)

print("-----------------------------------------")
print("MILESTONES")
print("-----------------------------------------")
print(data["milestones"][0])

print("-----------------------------------------")
print("TICKETS")
print("-----------------------------------------")
pprint(data["tickets"][0])

json_data.close()
