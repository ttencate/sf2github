#!/usr/bin/env python
import json
from pprint import pprint

json_data=open('tickets.json')

data = json.load(json_data)
pprint(data)
json_data.close()
