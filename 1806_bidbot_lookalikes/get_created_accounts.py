from beem.account import Account
from beem.comment import Comment
from beem.utils import addTzInfo, construct_authorperm, parse_time
from datetime import datetime
import sys
import shelve

start = addTzInfo(datetime(2018, 6, 10))
stop = addTzInfo(datetime(2018, 6, 12))
hist_start = addTzInfo(datetime(2018, 6, 18))

a = Account("steem")
created_accounts = set()
for op in a.history(start=start, stop=stop,
                    only_ops=['account_create_with_delegation']):
    sys.stdout.write("%s\r" % (op['timestamp']))
    name = op['new_account_name']
    created_accounts |= set([name])

print("\n", len(created_accounts))

known_accs = set()
with open("alike_names_zoomed.txt") as f:
    for line in f.readlines():
        if line.endswith("\n"):
            line = line[:-1]
        known_accs |= set([line])

created_accounts = created_accounts - known_accs
print(len(created_accounts))

connected_accounts = set()
authorperms = set()
idx = 0
voting_timestamps = {}
follow_timestamps = {}
for acc in known_accs:
    print("%d/%d - parsing %s (%d connected)" % (idx, len(known_accs),
                                                 acc,
                                                 len(connected_accounts)))
    if acc not in voting_timestamps:
        voting_timestamps[acc] = []
    if acc not in follow_timestamps:
        follow_timestamps[acc] = []
    try:
        a = Account(acc)
    except:
        continue
    for op in a.history(start=hist_start, only_ops=['vote', 'custom_json']):
        if op['type'] == 'custom_json':
            follow_timestamps[acc].append(parse_time(op['timestamp']))
            continue
        if op['voter'] != acc:
            continue
        voting_timestamps[acc].append(parse_time(op['timestamp']))
        authorperm = construct_authorperm(op)
        if authorperm in authorperms:
            continue
        c = Comment(authorperm)
        voters = set([v['voter'] for v in c['active_votes']])
        connected_accounts |= (voters & created_accounts)
    idx += 1

print(connected_accounts)
print(len(connected_accounts))

with open("alike_names_connected.txt", "w") as f:
    f.write("\n".join(sorted(known_accs | connected_accounts)))


for acc in connected_accounts:
    print("%d/%d - parsing %s" % (idx, len(connected_accounts),
                                  acc))
    if acc not in voting_timestamps:
        voting_timestamps[acc] = []
    if acc not in follow_timestamps:
        follow_timestamps[acc] = []
    try:
        a = Account(acc)
    except:
        continue
    for op in a.history(start=hist_start,
                                   only_ops=['vote', 'custom_json']):
        if op['type'] == 'custom_json':
            follow_timestamps[acc].append(parse_time(op['timestamp']))
            continue
        if op['voter'] != acc:
            continue
        voting_timestamps[acc].append(parse_time(op['timestamp']))
    idx += 1

s = shelve.open("voting_timestamps.shelve")
s['voting_timestamps'] = voting_timestamps
s['follow_timestamps'] = follow_timestamps
s.close()
