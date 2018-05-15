#!/usr/bin/python
from MongoStorage import MongoStorage
from beem import Steem
from beem.account import Account
from beem.amount import Amount
from beem.utils import resolve_authorperm
from datetime import datetime, timedelta
import sys
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

year = int(sys.argv[1])
month = int(sys.argv[2])
day = int(sys.argv[3])

db = MongoStorage()

tx_start = datetime(year, month, day)
tx_end = tx_start + timedelta(days=1)

tx_time = {"$gt": tx_start, "$lte": tx_end}
tx_conds = {'type': 'transfer', 'timestamp': tx_time}
tx_proj = {'_id': 0, 'to': 1, 'memo': 1, 'timestamp': 1}

botlist = set()
bot_votes = {}

bottracker_list = []
with open("bots.txt") as f:
    for line in f.readlines():
        bottracker_list.append(line[:-1])

uniq = {}
for tx in db.Operations.find(tx_conds, projection=tx_proj):
    try:
        author, permlink = resolve_authorperm(tx['memo'])
    except ValueError:
        continue
    bot = tx['to']
    identifier = author+permlink
    if bot in uniq and identifier in uniq[bot]:
        continue
    min_time = tx['timestamp']
    max_time = min_time + timedelta(hours=5)
    time_contraints = {"$gt": min_time, "$lte": max_time}
    op_conds = {'type': 'vote', 'author': author, 'permlink':
                permlink, 'voter': bot, 'timestamp': time_contraints}
    op_proj = {'_id': 1}
    if db.Operations.find_one(op_conds, projection=op_proj):
        botlist |= set([bot])
        if not bot in bot_votes:
            bot_votes[bot] = 0
        bot_votes[bot] += 1
        if bot not in uniq:
            uniq[bot] = set()
        uniq[bot] |= set([identifier])


print("Number of bots: %d" % (len(botlist)))

botcount = 0
accounts = []
total_sp = 0
tracked_sp = 0
untracked_sp = 0
tracked_count = 0
untracked_count = 0

for bot in sorted(bot_votes, key=lambda k: bot_votes[k], reverse=True):
    sp = 0
    if year == 2018 and month == 5 and day == 14:
        a = Account(bot)
        sp = a.get_steem_power()
    if bot_votes[bot] >= 5:
        print("\t%7s%17s (%8d SP): %6d" % ((bot in bottracker_list),
                                           bot, sp, bot_votes[bot]))
        botcount += 1
        total_sp += sp
        accounts.append(bot)

        if bot in bottracker_list:
            tracked_sp += sp
            tracked_count += 1
        else:
            untracked_sp += sp
            untracked_count += 1

print("%4d%2d%2d: Number of bots with 5 or more served bids: %d, %d SP" %
      (year, month, day, botcount, total_sp))


if year != 2018 or month != 5 or day != 14:
    exit()


fig = plt.figure(figsize=(12, 6))
title = "Bots by number\n%s bots in total" % (botcount)
p1 = fig.add_subplot(121, title=title)
labels = ['On steembottracker', 'Not on steembottracker']
p1.pie([tracked_count, untracked_count], labels=labels, autopct="%.1f%%")


title = "Bots by SP\n%d SP in total" % (total_sp)
p2 = fig.add_subplot(122, title=title)
labels = ['On steembottracker', 'Not on steembottracker']
p2.pie([tracked_sp, untracked_sp], labels=labels, autopct="%.1f%%")

plt.savefig("tracked_vs_untracked.png")
