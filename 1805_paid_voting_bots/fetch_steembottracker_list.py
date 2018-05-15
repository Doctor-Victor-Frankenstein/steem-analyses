#!/usr/bin/python
import requests

bid_bots_url = 'https://steembottracker.net/bid_bots'
other_bots_url = 'https://steembottracker.net/other_bots'

r = requests.get(bid_bots_url)
data = r.json()
botlist = "minnowbooster\n"
for entry in data:
    #if 'is_disabled' not in entry or entry['is_disabled'] == False:
    botlist += entry['name'] + "\n"

r = requests.get(other_bots_url)
data = r.json()
for entry in data:
    #if 'is_disabled' in entry and entry['is_disabled'] == False:
    botlist += entry['name'] + "\n"

with open("bots.txt", "w") as f:
    f.write(botlist)
