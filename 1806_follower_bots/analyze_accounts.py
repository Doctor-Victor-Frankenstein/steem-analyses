#!/usr/bin/python
from hist import hist
from beem.account import Account, Accounts
from beem.utils import parse_time, addTzInfo
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
import shelve
from datetime import datetime

created = []
reputation = []
effective_sp = []
own_sp = []
posts = []
creator = hist()
posting_rewards = []
curation_rewards = []

sp_limit = 50
post_limit = 200
created_limit = addTzInfo(datetime(2018, 1, 1))
reward_limit = 2

s = shelve.open("accounts.shelf")
accounts = s['accounts']
s.close()

print(len(accounts))

for a in accounts:
    created.append(max(parse_time(a['created']), created_limit))
    reputation.append(a['reputation'])
    effective_sp.append(min(a['steem_power'], sp_limit))
    own_sp.append(min(a['own_steem_power'], sp_limit))
    print(a['name'], a['own_steem_power'], a['steem_power'])
    posts.append(min(a['post_count'], post_limit))
    creator.fill(a['creator'])
    posting_rewards.append(min(a['posting_rewards']/1000, reward_limit))
    curation_rewards.append(min(a['curation_rewards']/1000, reward_limit))

fig = plt.figure(figsize=(8, 12))
fig.autofmt_xdate()

title = "Account creation date"
xlabel = "Date"
ylabel = "Number of accounts"
p = fig.add_subplot(321, title=title, xlabel=xlabel, ylabel=ylabel)
timestamps = [mdates.date2num(d) for d in created]
p.hist(timestamps, bins=50)
xFmt = mdates.DateFormatter('%m/%y')
p.xaxis.set_major_formatter(xFmt)
p.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
p.grid()

title = "Account reputation"
xlabel = "Reputation"
ylabel = "Number of accounts"
p = fig.add_subplot(322, title=title, xlabel=xlabel, ylabel=ylabel)
p.hist(reputation, bins=50)
p.grid()

title = "Account SP"
xlabel = "SP"
ylabel = "Number of accounts"
p = fig.add_subplot(323, title=title, xlabel=xlabel, ylabel=ylabel)
p.hist(effective_sp, bins=sp_limit + 1, range=[0, sp_limit],
        label="Effective SP")
p.hist(own_sp, bins=sp_limit + 1, range=[0, sp_limit], label="Own SP")
p.legend()
p.grid()

title = "Number of Posts/Comments"
xlabel = "Posts/Comments"
ylabel = "Number of accounts"
p = fig.add_subplot(324, title=title, xlabel=xlabel, ylabel=ylabel)
p.hist(posts, bins=50)
p.grid()


title = "Account creator"
p = fig.add_subplot(325, title=title)
p.pie(creator.yrange(), labels=creator.xrange(), autopct="%.1f%%",
      startangle=180-45)
p.grid()

title = "Posting/Curation rewards"
xlabel = "Rewards [STEEM]"
ylabel = "Number of accounts"
p = fig.add_subplot(326, title=title, xlabel=xlabel, ylabel=ylabel)
range = [0, reward_limit]
p.hist(posting_rewards, bins=50, label="Posting rewards", range=range)
p.hist(curation_rewards, bins=50, label="Curation rewards", range=range)
p.grid()
p.legend()

plt.tight_layout()
plt.savefig("follower_bot_stats.png")
