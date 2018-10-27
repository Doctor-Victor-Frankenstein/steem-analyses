import shelve
import os
from hist import hist
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from datetime import date
import sys
import numpy as np
import math

VOTE_DUST_THRESHOLD = int(50e6)


def inPlotRange(day):
    range_start = date(2018, 9, 8)
    range_stop = date(2018, 10, 23)
    return range_start <= day < range_stop


def isHF20HistoRange(day):
    range_start = date(2018, 10, 17)
    range_stop = date(2018, 10, 24)
    return range_start <= day < range_stop


def isHF19HistoRange(day):
    range_start = date(2018, 9, 8)
    range_stop = date(2018, 9, 15)
    return range_start <= day < range_stop


def get_var_log_bins(nbins, minval, maxval):
    logmin = math.log10(minval)
    logmax = math.log10(maxval)
    binwidth = (logmax - logmin) / nbins
    return [float(math.pow(10, logmin + i * binwidth)) for i in range(0, nbins+1)]


inputfiles = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.startswith("stats-") and file.endswith(".shelf"):
            inputfiles.append(file)

if len(sys.argv) > 1:
    inputfiles = sys.argv[1:]

total_votes = {}
dust_votes = {}
zero_votes = {}
vote_rshares_hf19 = []
vote_rshares_hf20 = []
vote_pct_hf19 = []
vote_pct_hf20 = []
zero_vote_pcts = []

zero_voters = hist()
zero_votees = hist()

for file in inputfiles:
    print("Processing %s" % (file))
    s = shelve.open(file)
    rshares_by_day = s['rshares']
    percent_by_day = s['percentages']
    zero_voters_by_day = s['zero_voters']
    zero_votees_by_day = s['zero_votees']
    s.close()

    for day in rshares_by_day:
        if day not in total_votes:
            total_votes[day] = 0
        if day not in dust_votes:
            dust_votes[day] = 0
        if day not in zero_votes:
            zero_votes[day] = 0
        for rs, pct in zip(rshares_by_day[day], percent_by_day[day]):
            total_votes[day] += 1
            if isHF20HistoRange(day):
                vote_pct_hf20.append(pct)
                vote_rshares_hf20.append(rs)
            if isHF19HistoRange(day):
                vote_pct_hf19.append(pct)
                vote_rshares_hf19.append(rs)
            if rs < VOTE_DUST_THRESHOLD:
                dust_votes[day] += 1
            if rs == 0:
                zero_votes[day] += 1
                if isHF20HistoRange(day):
                    zero_vote_pcts.append(pct)
                    for voter, votes in \
                        zip(zero_voters_by_day.xrange(),
                            zero_voters_by_day.yrange()):
                        zero_voters.fill(voter, votes)
                    for votee, votes in \
                        zip(zero_votees_by_day.xrange(),
                            zero_votees_by_day.yrange()):
                        zero_votees.fill(votee, votes)

xtotal = sorted([k for k in total_votes.keys() if inPlotRange(k)])
ytotal = [total_votes[k] for k in xtotal]
xdust = sorted([k for k in dust_votes.keys() if inPlotRange(k)])
ydust = [dust_votes[k] for k in xdust]
xzero = sorted([k for k in zero_votes.keys() if inPlotRange(k)])
yzero = [zero_votes[k] for k in xzero]

#####################################################################
# Total/dust/zero votes per day
#####################################################################
fig = plt.figure(figsize=(12, 10))
args = {'linestyle': '-', 'marker': '.'}
p1 = fig.add_subplot(211, title="Absolute number of votes per day",
                     xlabel="Voting date", ylabel="Number of votes")
p1.plot_date(xtotal, ytotal, **args, label="Total number of votes")
p1.plot_date(xdust, ydust, **args, label="Number of dust votes")
p1.plot_date(xzero, yzero, **args, label="Number of zero-value votes")
p1.grid()
p1.legend()

#####################################################################
# relative dust/zero votes per day
#####################################################################
ydust_rel = [dust_votes[d] * 100 / total_votes[d] for d in xdust]
yzero_rel = [zero_votes[d] * 100 / total_votes[d] for d in xzero]

p2 = fig.add_subplot(212, title="Relative number of dust/zero-value votes",
                     xlabel="Voting date", ylabel="Share of all votes (%)")
p2.plot_date(xdust, ydust_rel, **args, label="Relative number of dust votes",
             color='orange')
p2.plot_date(xzero, yzero_rel, **args, label="Relative number of zero-value votes",
             color='green')
p2.grid()
p2.legend()
plt.tight_layout()
plt.savefig("votes_per_day.png")


#####################################################################
# histogram of vote percentages/rshares - HF19/HF20
#####################################################################
def get_pie_data(hist_data):
    pcts = {}
    for pct in hist_data:
        for i in [0.1, 1, 10, 50, 99.99, 100]:
            if i not in pcts:
                pcts[i] = 0
            if pct <= i:
                pcts[i] += 1
                break
    keys = sorted(pcts)
    labels = ["<=0.1%", "0.1-1%", "1-10%", "10-50%", "50-99.99%",
              "100%"]
    shares = [pcts[x] for x in keys]
    return shares, labels

fig = plt.figure(figsize=(12, 12))

p3 = fig.add_subplot(221, title="Distribution of vote percentages - HF19")
shares, labels = get_pie_data(vote_pct_hf19)
p3.pie(shares, labels=labels, autopct="%.1f%%")

p4 = fig.add_subplot(222, title="Distribution of vote percentages - HF20")
shares, labels = get_pie_data(vote_pct_hf20)
p4.pie(shares, labels=labels, autopct="%.1f%%")

bins = get_var_log_bins(100, 1e6, 1e13)
args = {'linestyle': 'dashed', 'linewidth': 1.5}

p5 = fig.add_subplot(223, title="Distribution of vote rshares - HF19",
                     xlabel="Rshares", ylabel="Occurrences")
p5.grid()
p5.hist(vote_rshares_hf19, bins=bins)
mean = np.mean(vote_rshares_hf19)
median = np.median(vote_rshares_hf19)
stddev = np.std(vote_rshares_hf19)
print("HF19 stddev: %.2f bn" % (stddev/1e9))
print("HF19 nVotes: %d" % (len(vote_rshares_hf19)))
p5.axvline(mean, **args, color="green",
           label="Mean vote rshares: %.2f bn" % (mean/1e9))
p5.axvline(median, **args, color="orange",
           label="Median vote rshares: %.2f bn" % (median/1e9))
p5.set_xscale("log")
p5.legend()

p6 = fig.add_subplot(224, title="Distribution of vote rshares - HF20",
                     xlabel="Rshares", ylabel="Occurrences")
p6.grid()
p6.hist(vote_rshares_hf20, bins=bins)
mean = np.mean(vote_rshares_hf20)
median = np.median(vote_rshares_hf20)
stddev = np.std(vote_rshares_hf20)
print("HF20 stddev: %.2f bn" % (stddev/1e9))
print("HF20 nVotes: %d" % (len(vote_rshares_hf20)))
p6.axvline(mean, **args, color="green",
           label="Mean vote rshares: %.2f bn" % (mean/1e9))
p6.axvline(median, **args, color="orange",
           label="Median vote rshares: %.2f bn" % (median/1e9))
p6.set_xscale("log")
p6.legend()

plt.savefig("vote_pct_hist.png")


#####################################################################
# Vote pct of zero-value votes
#####################################################################
fig = plt.figure(figsize=(12, 6))
p1 = fig.add_subplot(121, title="Vote percentages of zero-value votes",
                     xlabel="Vote percentage (%)", ylabel="Occurrences")
p1.hist(zero_vote_pcts, bins=50)
p1.grid()
p2 = fig.add_subplot(122, title="Distribution of zero-value vote percentages")
shares, labels = get_pie_data(zero_vote_pcts)
p2.pie(shares, labels=labels, autopct="%.1f%%")
plt.savefig("zero_value_hist.png")

print(zero_voters.prettytable(limit=30))
print(zero_votees.prettytable(limit=30))
