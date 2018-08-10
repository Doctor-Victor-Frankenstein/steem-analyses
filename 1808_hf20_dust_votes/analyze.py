import shelve
import sys
import json
from datetime import datetime, timedelta
from beem.utils import parse_time, addTzInfo
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from hist import hist
import math
import numpy as np

VOTE_DUST_THRESHOLD = int(50e6)

def get_var_log_bins(nbins, minval, maxval):
    logmin = math.log10(minval)
    logmax = math.log10(maxval)
    binwidth = (logmax - logmin) / nbins
    return [float(math.pow(10, logmin + i * binwidth)) for i in range(0, nbins+1)]

vote_start = addTzInfo(datetime(2018, 8, 1))
vote_end = addTzInfo(datetime(2018, 8, 8))
date = datetime(2018, 7, 25)

rshare_distribution_hf19 = []
rshares_per_day_hf19 = hist()
rshare_distribution_hf20 = []
rshares_per_day_hf20 = hist()

while date < datetime(2018, 8, 8):
    try:
        print("processing ", date)
        s = shelve.open('posts-2018-%02d-%02d.shelf' % (date.month,
                                                        date.day))
        posts = s['posts']
        s.close()
    except:
        posts = []
        pass
    date += timedelta(days=1)

    for post in posts:
        for vote in post['active_votes']:
            ts = parse_time(vote['time'])
            if ts < vote_start or ts >= vote_end:
                continue
            rshares_hf19 = int(vote['rshares'])
            if rshares_hf19 == 0:
                continue
            rshares_hf20 = int(math.copysign(max(0, abs(rshares_hf19)
                                                 - VOTE_DUST_THRESHOLD), rshares_hf19))
            rshares_per_day_hf19.fill(ts.date(), rshares_hf19)
            rshares_per_day_hf20.fill(ts.date(), rshares_hf20)
            rshare_distribution_hf19.append(abs(rshares_hf19))
            rshare_distribution_hf20.append(abs(rshares_hf20))

limit_args = {'label': "Vote dust threshold: 50 M", 'linestyle': 'dashed',
              'linewidth': 1.5, 'color': 'red'}

median_rshares_hf19 = np.median(rshare_distribution_hf19)
median_args = {'linestyle': 'dashed', 'linewidth': 1.5, 'color': 'orange'}
median_label = "Median rshares: %d M" % (median_rshares_hf19/1e6)

mean_rshares_hf19 = np.mean(rshare_distribution_hf19)
mean_args = {'linestyle': 'dashed', 'linewidth': 1.5, 'color': 'green'}
mean_label = "Mean rshares: %d M" % (mean_rshares_hf19/1e6)

plt.figure(figsize=(12, 6))
bins = get_var_log_bins(100, 1e5, max(rshare_distribution_hf19)*1.2)
plt.hist(rshare_distribution_hf19, bins=bins)
plt.grid()
plt.xlabel("Rshares per vote")
plt.ylabel("Occurences")
plt.xscale('log')
plt.axvline(VOTE_DUST_THRESHOLD, **limit_args)
plt.axvline(median_rshares_hf19, **median_args, label=median_label)
plt.axvline(mean_rshares_hf19, **mean_args, label=mean_label)
plt.legend()
plt.title("Distribution of vote values (HF19)")
plt.savefig("rshares_hist_hf19.png")


median_rshares_hf20 = np.median(rshare_distribution_hf20)
median_args = {'linestyle': 'dashed', 'linewidth': 1.5, 'color': 'orange'}
median_label = "Median rshares: %d M" % (median_rshares_hf20/1e6)

mean_rshares_hf20 = np.mean(rshare_distribution_hf20)
mean_args = {'linestyle': 'dashed', 'linewidth': 1.5, 'color': 'green'}
mean_label = "Mean rshares: %d M" % (mean_rshares_hf20/1e6)

plt.figure(figsize=(12, 6))
plt.hist(rshare_distribution_hf20, bins=bins)
plt.grid()
plt.xlabel("Rshares per vote")
plt.ylabel("Occurences")
plt.xscale('log')
plt.axvline(VOTE_DUST_THRESHOLD, **limit_args)
plt.axvline(median_rshares_hf20, **median_args, label=median_label)
plt.axvline(mean_rshares_hf20, **mean_args, label=mean_label)
plt.legend()
plt.title("Distribution of vote values (HF20)")
plt.savefig("rshares_hist_hf20.png")

total_rshares_hf19 = sum(rshare_distribution_hf19)
total_rshares_hf20 = sum(rshare_distribution_hf20)
print("%e" % total_rshares_hf19, "%e" % total_rshares_hf20)
print("%.3f%%" % (total_rshares_hf20 * 100 / (total_rshares_hf19)))

# Rshares per day

plt.figure(figsize=(12, 6))
args = {'linestyle': '-', 'marker': '.'}
plt.plot_date(rshares_per_day_hf19.xrange('key'),
              rshares_per_day_hf19.yrange('key'),
              label="HF19 (measured)", **args)
plt.plot_date(rshares_per_day_hf20.xrange('key'),
              rshares_per_day_hf20.yrange('key'),
              label="HF20 (calculated)", **args)
plt.grid()
plt.legend()
plt.title("Sum of daily vote rshares for HF19 and HF20")
plt.xlabel("Date")
plt.ylabel("Rshares")
plt.savefig("rshares_per_day.png")

loss_hist = hist()
lim = 15
for hf19, hf20 in zip(rshare_distribution_hf19,
                      rshare_distribution_hf20):
    rel_loss = (hf19 - hf20) * 100 / hf19
    for loss in range(0, lim):
        if int(rel_loss) <= loss:
            loss_hist.fill(loss)
    if int(rel_loss) >= lim:
        loss_hist.fill(lim)

plt.figure(figsize=(12, 6))
y = [(x * 100 / len(rshare_distribution_hf19)) for x in loss_hist.yrange('key')]
ticks = range(0, lim+1)
labels = ["less than %s%%" % (t+1) for t in ticks[:-1]]
labels.append("%d%% or more" % (lim))
plt.bar(loss_hist.xrange('key'), y)
plt.title("Distribution of the relative rshare loss due to HF20")
plt.xlabel("Relative loss in rshares (%)")
plt.ylabel("Relative number of votes")
plt.gca().set_xticks(ticks)
plt.gca().set_xticklabels(labels)
plt.gcf().autofmt_xdate(rotation=30)
plt.ylim([0, 100])
plt.grid()
plt.savefig("rel_loss_distribution.png")
