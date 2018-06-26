#!/usr/bin/python
import shelve
from beem import Steem
from beem.utils import addTzInfo
from datetime import datetime
from nltk import edit_distance

LIMIT = 100
MAX_EDIT_DISTANCE = 2
MIN_LAST_VOTE_TIME = addTzInfo(datetime(2018, 6, 20))

stm = Steem(offline=True)

s = shelve.open("accounts.active.shelve")
accounts = s['accounts']
s.close()

all_names = set([a for a in accounts.keys() if len(a) > (MAX_EDIT_DISTANCE + 2)])
top_accounts = set()
print("By effective VESTS")
idx = 0
for name in sorted(accounts, key=lambda k:
                   accounts[k]['effective_vests'], reverse=True)[:LIMIT]:
    if len(name) <= MAX_EDIT_DISTANCE + 2:
        continue
    print("%d: %16s %.2f MVEST" % (idx, name,
                                   accounts[name]['effective_vests']/1e6))
    top_accounts |= set([name])
    idx += 1

print("By STEEM balance")
idx = 0
for name in sorted(accounts, key=lambda k: accounts[k]['balance'],
                   reverse=True)[:LIMIT]:
    if len(name) <= MAX_EDIT_DISTANCE + 2:
        continue
    print("%d: %16s %s" % (idx, name, accounts[name]['balance']))
    top_accounts |= set([name])
    idx += 1

print(len(top_accounts), sorted(top_accounts))

alike_names = set()
for ref in sorted(top_accounts):
    if len(ref) <= MAX_EDIT_DISTANCE + 2:
        continue  # Skip short names wrt to edit distance
    alikes = set()
    for alike in all_names:
        if alike == ref:
            continue
        if abs(len(alike) - len(ref)) > MAX_EDIT_DISTANCE:
            continue
        if edit_distance(ref, alike) <= MAX_EDIT_DISTANCE and \
           accounts[alike]['last_vote_time'] >= MIN_LAST_VOTE_TIME:
            alikes |= set([alike])
    alike_names |= alikes
    print(ref, alikes)

with open("alike_names.txt", "w") as f:
    f.write("\n".join(alike_names))
    f.write("\n")
