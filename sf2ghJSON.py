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
for key in data["milestones"][0]:
    print(key)

print("-----------------------------------------")
print("TICKETS")
print("-----------------------------------------")
for key in data["tickets"][0]:
    print(key)

json_data.close()
