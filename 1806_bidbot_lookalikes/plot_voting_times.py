import shelve
from datetime import datetime, timedelta
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

dateFmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')

s = shelve.open("voting_timestamps.shelve")
voting_times = s['voting_timestamps']
follow_times = s['follow_timestamps']
s.close()

known_accs = set()
with open("alike_names_connected_filtered.txt") as f:
    for line in f.readlines():
        if line.endswith("\n"):
            line = line[:-1]
        known_accs |= set([line])

# s = shelve.open("accounts.active.shelve")
# accounts = s['accounts']
# s.close()

days = 7
ylabels = sorted(known_accs)
yticks = range(len(ylabels))

plt.figure(figsize=(20, 10))  # max(6, len(yticks)/5)))
args = {'marker':'.'}
yindex = 0
for acc_name in sorted(known_accs):
    xrange = voting_times[acc_name]
    yrange = [yindex] * len(xrange)
    plt.plot_date(xrange, yrange, **args)
    yindex += 1
# plt.gca().set_yticks(yticks)
# plt.gca().set_yticklabels(ylabels)
plt.gcf().autofmt_xdate(rotation=30)
plt.gca().xaxis.set_major_formatter(dateFmt)
plt.grid()
plt.title("Voting times of all votes from these accounts in the last %d days\n"
          "each horizontal line are all votes from one account" % (days))
plt.xlabel("Voting time")
plt.ylabel("Account number")
plt.tight_layout()
plt.savefig("voting_times.png")


plt.figure(figsize=(20, 10))  # max(6, len(yticks)/5)))
args = {'marker':'.'}
yindex = 0
for acc_name in sorted(known_accs):
    xrange = follow_times[acc_name]
    yrange = [yindex] * len(xrange)
    plt.plot_date(xrange, yrange, **args)
    yindex += 1
# plt.gca().set_yticks(yticks)
# plt.gca().set_yticklabels(ylabels)
plt.gcf().autofmt_xdate(rotation=30)
plt.gca().xaxis.set_major_formatter(dateFmt)
plt.grid()
plt.title("\"Follow\" operations from these accounts in the last %d days\n"
          "each horizontal line are all \"follow\" ops from one account" % (days))
plt.xlabel("Follow time")
plt.ylabel("Account number")
plt.tight_layout()
plt.savefig("follow_times.png")
