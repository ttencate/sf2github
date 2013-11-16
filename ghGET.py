#!/usr/bin/env python
import requests
from getpass import getpass

username  = "codeguru42"
password = getpass('%s\'s GitHub password: ' % username)

response = requests.get('https://api.github.com/issues', auth=(username, password))

print(response)
print(response.json())
