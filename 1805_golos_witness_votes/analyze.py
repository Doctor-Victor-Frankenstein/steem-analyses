#!/usr/bin/python
import shelve
from datetime import datetime
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta
from hist import hist
import sys
from beem.amount import Amount

s = shelve.open("accounts.shelf")
accounts = s['accounts']
s.close()

dolphin = 10e6
orca = 100e6
whale = 1000e6

accs_with_votes = 0
accs_with_proxy = 0
accs_without = 0

gests_with_votes = 0
gests_with_proxy = 0
gests_without = 0

no_vote_gests_hist = []
top_gests_holders = hist()
top_gests_holders_novote = hist()

minnow_gests = 0
dolphin_gests = 0
orca_gests = 0
whale_gests = 0

minnow_accs = 0
dolphin_accs = 0
orca_accs = 0
whale_accs = 0

excludes = ['golosio', 'golos', 'steemit', 'ned'] #, 'ned', 'dan', 'smooth', 'val-a', 'dantheman']

for a in accounts:
    if a['name'] in excludes:
        continue
    gests = float(a['vesting_shares'].split(' ')[0])
    top_gests_holders.fill(a['name'], gests)

    if len(a['witness_votes']) and a['proxy'] == '':
        accs_with_votes += 1
        gests_with_votes += gests
    elif a['proxy'] != '':
        accs_with_proxy += 1
        gests_with_proxy += gests
    else:
        accs_without += 1
        gests_without += gests
        no_vote_gests_hist.append(gests/1e6)
        top_gests_holders_novote.fill(a['name'], gests)
        if gests > whale:
            whale_gests += gests
            whale_accs += 1
        elif gests > orca:
            orca_gests += gests
            orca_accs += 1
        elif gests > dolphin:
            dolphin_gests += gests
            dolphin_accs += 1
        else:
            minnow_gests += gests
            minnow_accs += 1


fig = plt.figure(figsize=(12, 6.5))
p1 = fig.add_subplot(121, title="Witness votes by number of accounts")
labels = ['Accounts\nwith votes', 'Accounts\nwith proxy', 'no vote']
p1.pie([accs_with_votes, accs_with_proxy, accs_without],
       labels=labels, autopct="%.1f%%")

p2 = fig.add_subplot(122, title="Witness votes by account GESTs")
labels = ['GESTS\nwith votes', 'GESTS\nwith proxy', 'no vote']
p2.pie([gests_with_votes, gests_with_proxy, gests_without],
       labels=labels, autopct="%.1f%%")
plt.tight_layout()
plt.savefig("witness_votes.png")

plt.figure(figsize=(6, 6))
labels=['Whales', 'Orcas', 'Dolpins', 'Minnow or\nsmaller']
#p1 = fig.add_subplot(121, title='Distribution of non-voting accounts by GESTS')
plt.pie([whale_gests, orca_gests, dolphin_gests, minnow_gests],
        labels=labels, autopct="%.1f%%")
plt.title('Distribution of non-voting accounts by GESTS')

# p2 = fig.add_subplot(122, title='Distribution of non-voting accounts by number')
# p2.pie([whale_accs, orca_accs, dolphin_accs, minnow_accs],
#         labels=labels, autopct="%.1f%%")
plt.savefig('non_voting_classification.png')

plt.figure(figsize=(12, 6))
plt.hist(no_vote_gests_hist, bins=100)
plt.grid()
plt.gca().set_yscale("log")
plt.title("Distribution of account GESTS not voting for witnesses")
plt.xlabel("Account MGESTS")
plt.ylabel("Number of accounts")
plt.savefig("no_vote_gests_hist.png")

print("top_gests_holders", top_gests_holders.xrange()[:20])
print(top_gests_holders.yrange()[:20])

print("top_gests_holders_novote", top_gests_holders_novote.xrange()[:20])
print(top_gests_holders_novote.yrange()[:20])

print("| Status | # accounts | Total MGESTS |")
print("|---|---|---|")
print("| Minnow or smaller | %d | %d |" % (minnow_accs, minnow_gests/1e6))
print("| Dolpin | %d | %d |" % (dolphin_accs, dolphin_gests/1e6))
print("| Orca | %d | %d |" % (orca_accs, orca_gests/1e6))
print("| Whale | %d | %d |" % (whale_accs, whale_gests/1e6))

top120_not_voting_gests = sum(top_gests_holders_novote.yrange()[:120])
others_not_voting_gests = sum(top_gests_holders_novote.yrange()[120:])

labels = ['Top 120 not voting', 'everyone else\nnot voting']
plt.figure(figsize=(6, 6))
plt.title("%GESTS not voting for witnesses")
plt.pie([top120_not_voting_gests, others_not_voting_gests],
        labels=labels, autopct="%.1f%%")
plt.savefig("top120_not_voting_gests.png")
