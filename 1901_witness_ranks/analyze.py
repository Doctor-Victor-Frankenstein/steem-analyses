import shelve
from beem.utils import parse_time
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from datetime import timedelta
import numpy as np

s = shelve.open("ops.shelf")
ops = s['ops']
s.close()

lists = []
last_list = []
last_list10 = []
last_list20 = []
all_witnesses = set()
change_ts = []
change_ts20 = []
change_ts10 = []
for op in ops:
    meta = json.loads(op['json_metadata'])
    if 'witnesses' not in meta:
        continue
    witnesses = meta['witnesses']
    ts = parse_time(op['timestamp'])
    if witnesses != last_list:
        lists.append(witnesses)
        change_ts.append(ts)
    if witnesses[:20] != last_list20:
        change_ts20.append(ts)
    if witnesses[:10] != last_list10:
        change_ts10.append(ts)
    last_list = witnesses
    last_list20 = witnesses[:20]
    last_list10 = witnesses[:10]
    all_witnesses |= set(witnesses)

all_witnesses = list(last_list)
# print(all_witnesses)
# print(len(all_witnesses))

change_ts = change_ts[1:]
change_ts20 = change_ts20[1:]
change_ts10 = change_ts10[1:]
lists = lists[1:]

start_day = min(change_ts).date()
stop_day = max(change_ts).date()
day = start_day
changes_per_day = {}
changes_per_day10 = {}
changes_per_day20 = {}
while day <= stop_day:
    changes_per_day[day] = 0
    changes_per_day20[day] = 0
    changes_per_day10[day] = 0
    day += timedelta(days=1)

ranks = {}
for w in all_witnesses:
    ranks[w] = []
for l in lists:
    for w in all_witnesses:
        try:
            ranks[w].append(l.index(w) + 1)
        except ValueError:
            ranks[w].append(None)

# print(ranks)

for ts in change_ts10:
    changes_per_day10[ts.date()] += 1
for ts in change_ts20:
    changes_per_day20[ts.date()] += 1
for ts in change_ts:
    changes_per_day[ts.date()] += 1

deltas40 = []
deltas20 = []
deltas10 = []
for i in range(1, len(change_ts)):
    deltas40.append((change_ts[i] - change_ts[i-1]).total_seconds()/60/60)
for i in range(1, len(change_ts20)):
    deltas20.append((change_ts20[i] - change_ts20[i-1]).total_seconds()/60/60)
for i in range(1, len(change_ts10)):
    deltas10.append((change_ts10[i] - change_ts10[i-1]).total_seconds()/60/60)

# print(deltas)
print("| Time between changes | Top40 witnesses | Top20 witnesses | Top10 witnesses |")
print("| --- | --- | --- | --- |")
print("| mean | %.2fh | %.2fh | %.2fh |" % (np.mean(deltas40), np.mean(deltas20), np.mean(deltas10)))
print("| median | %.2fh | %.2fh | %.2fh |" % (np.median(deltas40), np.median(deltas20), np.median(deltas10)))
print("| max | %.2fh | %.2fh | %.2fh |" % (max(deltas40), max(deltas20), max(deltas10)))
print("| min | %.2fh | %.2fh | %.2fh |" % (min(deltas40), min(deltas20), min(deltas10)))

plt.figure(figsize=(12, 6))
yrange = [1 for ts in change_ts]
plt.plot_date(change_ts, yrange)
plt.grid()
plt.savefig("change_ts.png")

xrange = sorted(changes_per_day.keys())
yrange = [changes_per_day[k] for k in xrange]
yrange20 = [changes_per_day20[k] for k in xrange]
yrange10 = [changes_per_day10[k] for k in xrange]
plt.figure(figsize=(12, 6))
plt.bar(xrange, yrange, label="Top40 witness rank changes")
plt.bar(xrange, yrange20, label="Top20 witness rank changes")
plt.bar(xrange, yrange10, label="Top10 witness rank changes")
plt.grid()
plt.legend()
plt.title("Witness rank changes per day")
plt.xlabel("Date")
plt.ylabel("Number of changes per day")
plt.savefig("changes_per_day.png")


xrange = sorted(timeofday.keys())
yrange = [timeofday[k] for k in xrange]
plt.figure(figsize=(12, 6))
plt.bar(xrange, yrange)
plt.grid()
plt.savefig("timeofday.png")

xrange = max(change_ts) - min(change_ts)
plt.figure(figsize=(12, 6))
for w in all_witnesses:
    plt.plot_date(change_ts, ranks[w], label=w, marker="", linestyle="-")
    plt.text(max(change_ts)+xrange*0.01, all_witnesses.index(w) + 1, w, fontsize=7, verticalalignment='center')
plt.xlim([min(change_ts), max(change_ts) + xrange*0.15])
plt.ylim([0, 41])
plt.grid()
plt.title("Ranks of individual witnesses over time")
plt.xlabel("Date")
plt.ylabel("Witness rank")
# plt.legend()
plt.savefig("ranks.png")
