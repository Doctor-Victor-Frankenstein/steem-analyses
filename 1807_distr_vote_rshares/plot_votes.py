import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

import shelve
from datetime import datetime, timedelta

start = datetime(2018, 4, 1)
stop = datetime(2018, 7, 1)

dates = []
all_rshares = []
bot_rshares = []
dapp_rshares = []
median_sbd_per_rshare = []
nposts = []
ncomments = []
nvotes = []
nauthors = []
nrootauthors = []
nvoters = []
self_rshares = []
self_rshares_ext = []
com_rshares = []
while start < stop:
    try:
        s = shelve.open("rshares-%04d%02d%02d.shelf" % \
                        (start.year, start.month, start.day))
        all_rshares.append(s['all_rshares'])
        bot_rshares.append(s['bot_rshares'])
        dapp_rshares.append(s['dapp_rshares'])
        dates.append(s['date'])
        median_sbd_per_rshare.append(s['median_sbd_per_rshare'])
        nposts.append(s['nposts'])
        ncomments.append(s['ncomments'])
        nvotes.append(s['nvotes'])
        nvoters.append(s['nvoters'])
        nauthors.append(s['nauthors'])
        nrootauthors.append(s['nrootauthors'])
        self_rshares.append(s['self_rshares'])
        self_rshares_ext.append(s['self_rshares_ext'])
        com_rshares.append(s['com_rshares'])
        s.close()
    except:
        start += timedelta(days=1)
        continue

    start += timedelta(days=1)


###############################################################################
# Number of posts/comments/authors
###############################################################################
plt.figure(figsize=(12, 6))
args = {'linestyle': '-', 'marker': '.'}
plt.plot_date(dates, nposts, label="Posts per day", **args)
plt.plot_date(dates, ncomments, label="Comments per day", **args)
plt.plot_date(dates, nauthors, label="Distinct authors per day", **args)
plt.plot_date(dates, nvoters, label="Distinct voters per day", **args)
plt.grid()
plt.xlabel("Date")
plt.ylabel("Number posts/comments/authors/voters per day")
plt.ylim([0, max(ncomments)*1.2])
plt.legend()
plt.title("General Blockchain Activity")
plt.savefig("general.png")

args = {'linestyle': '-', 'marker': '.'}

###############################################################################
# Bot & Dapp votes
###############################################################################
fig = plt.figure(figsize=(12, 6))
title = "Vote rshares - absolute values"
xlabel = "Date"
ylabel = "sum of rshares"
p1 = fig.add_subplot(121, title=title, xlabel=xlabel, ylabel=ylabel)
p1.plot_date(dates, all_rshares, label="all vote rshares", **args)
p1.plot_date(dates, bot_rshares, label="bot vote rshares", **args)
p1.plot_date(dates, dapp_rshares, label="dapp vote rshares", **args)
p1.grid()
p1.legend()
p1.set_ylim([0, max(all_rshares)*1.2])

rel_all = [100] * len(all_rshares)
rel_bots = [bot_rshares[i] * 100 / all_rshares[i] for i in
            range(len(all_rshares))]
rel_dapps = [dapp_rshares[i] * 100 / all_rshares[i] for i in
            range(len(all_rshares))]
title = "Vote rshares - relative values"
xlabel = "Date"
ylabel = "Relative share (% from all vote rshares)"
p2 = fig.add_subplot(122, title=title, xlabel=xlabel, ylabel=ylabel)
p2.plot_date(dates, rel_all, label="all vote rshares", **args)
p2.plot_date(dates, rel_bots, label="bot vote rshares", **args)
p2.plot_date(dates, rel_dapps, label="dapp vote rshares", **args)
p2.grid()
p2.legend()
p2.set_ylim([0, max(rel_bots)*1.2])

plt.gcf().autofmt_xdate(rotation=30)
plt.tight_layout()
plt.savefig("rshares_bots_dapps.png")

###############################################################################
# Self- & Community votes
###############################################################################
fig = plt.figure(figsize=(12, 6))
args = {'linestyle': '-', 'marker': '.'}
title = "Self- & Community Vote rshares\nabsolute values"
xlabel = "Date"
ylabel = "Sum of rshares"
p1 = fig.add_subplot(121, title=title, xlabel=xlabel, ylabel=ylabel)
p1.plot_date(dates, self_rshares, label="Self vote rshares", **args)
# p1.plot_date(dates, self_rshares_ext, label="Self + alt account vote rshares", **args)
p1.plot_date(dates, com_rshares, label="Community vote rshares", **args)
p1.grid()
p1.legend()
p1.set_ylim([0, max(self_rshares_ext)*1.2])

rel_all = [100] * len(all_rshares)
rel_self = [self_rshares[i] * 100 / all_rshares[i] for i in
            range(len(all_rshares))]
rel_self_ext = [self_rshares_ext[i] * 100 / all_rshares[i] for i in
                range(len(all_rshares))]
rel_com = [com_rshares[i] * 100 / all_rshares[i] for i in
           range(len(all_rshares))]
title = "Self- & Community Vote rshares\nrelative values"
xlabel = "Date"
ylabel = "Relative share (% from all vote rshares)"
p2 = fig.add_subplot(122, title=title, xlabel=xlabel, ylabel=ylabel)
args = {'linestyle': '-', 'marker': '.'}
p2.plot_date(dates, rel_self, label="Self vote rshares", **args)
# p2.plot_date(dates, rel_self_ext, label="Self + alt account vote rshares", **args)
p2.plot_date(dates, rel_com, label="Community vote rshares", **args)
p2.grid()
p2.legend()
p2.set_ylim([0, max(rel_self_ext)*1.2])

plt.gcf().autofmt_xdate(rotation=30)
plt.tight_layout()
plt.savefig("rshares_self_com.png")
