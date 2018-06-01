#1/usr/bin/python
import shelve
from datetime import datetime, timedelta
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from hist import hist
import sys

AUTO_FOLLOW_TIME = timedelta(seconds=120)
MAX_ACCS = 500
MIN_FOP_CUT = 5000
MAX_FOP_CUT = 12500
ACC_NUM_FOP_CUT = 180

# first week of March
start_date_early = datetime(2018, 5, 1)
stop_date_early = datetime(2018, 5, 8)

# ~third week of March
start_date_late = datetime(2018, 5, 18)
stop_date_late = datetime(2018, 5, 25)

year = 2018
month = 5
day = 1
posts = []
follows = []
last_created = None
next_load_on = None
post_idx = 0
fop_start = 0

while True:
    if last_created is None or last_created >= next_load_on:
        if day == 32:
            break
        # print(last_created, next_load_on)
        date = "%04d%02d%02d" % (year, month, day)
        print("\nloading", date)
        s = shelve.open("posts-%s.shelf" % (date))
        posts.extend(sorted(s['posts'], key=lambda k: k['created']))
        follows.extend(sorted(s['follows'], key=lambda k:
                              k['timestamp']))
        s.close()
        next_load_on = datetime(year, month, day) + \
                       timedelta(days=1) - 2 * AUTO_FOLLOW_TIME
        day += 1
        # add daily stats here

    p = posts[post_idx]
    posts[post_idx]['fops'] = []
    fop_idx = fop_start
    f = follows[fop_idx]
    sys.stdout.write("\rposts: %d/%d, fops: %d/%d" % (post_idx,
                                                      len(posts),
                                                      fop_start,
                                                      len(follows)))
    while f['timestamp'] - p['created'] < AUTO_FOLLOW_TIME:
        if p['created'] > f['timestamp']:
            fop_start = fop_idx
        elif f['following'] == p['author']:
            # print(p['created'], p['author'], f)
            posts[post_idx]['fops'].append(f)

        fop_idx += 1
        f = follows[fop_idx]

    last_created = p['created']
    post_idx += 1

total_fops_per_day = hist()
for fop in follows:
    total_fops_per_day.fill(fop['timestamp'].date())

auto_fops_per_day = []
post_dates = []
mean_fops = []
median_fops = []
max_fops = []
last_date = None
posts_per_day = hist()
foplist = []
authorset = set()
unique_authors_per_day = []
all_authors = set()
unique_authors = []


for p in posts:
    if 'fops' not in p:
        continue
    date = p['created'].date()
    posts_per_day.fill(date)

    if not last_date:
        last_date = date
    if date > last_date:
        post_dates.append(last_date)
        mean_fops.append(np.mean(foplist))
        median_fops.append(np.median(foplist))
        max_fops.append(max(foplist))
        auto_fops_per_day.append(sum(foplist))
        unique_authors_per_day.append(len(authorset))
        unique_authors.append(len(all_authors))
        foplist = []
        authorset = set()

    nfops = len(p['fops'])
    foplist.append(nfops)
    authorset |= set([p['author']])
    all_authors |= set([p['author']])
    last_date = date

post_dates.append(last_date)
mean_fops.append(np.mean(foplist))
median_fops.append(np.median(foplist))
max_fops.append(max(foplist))
auto_fops_per_day.append(sum(foplist))
unique_authors_per_day.append(len(authorset))
unique_authors.append(len(all_authors))

print("posts: %d" % (len(posts)))
print("mean:", mean_fops)
print("median:", median_fops)
print("max:", max_fops)
print("auto:", auto_fops_per_day)
print("dates:", post_dates)
print("total-x:", total_fops_per_day.xrange('key', False))
print("total-y:", total_fops_per_day.yrange('key', False))


###############################################################################
# Number of Follow Operations per day
###############################################################################
args = {'linestyle': '-', 'marker':'.'}
plt.figure(figsize=(12, 6))
label = "Follow-ops on the same day"
plt.plot_date(total_fops_per_day.xrange('key', False),
              total_fops_per_day.yrange('key', False), label=label,
              **args)
label = "Follow-ops within 2 minutes"
plt.plot_date(post_dates, auto_fops_per_day, label=label, **args)
plt.title("Number of follow-operations on authors per day")
plt.grid()
maxy = total_fops_per_day.yrange()[0] * 1.2
plt.ylim([0, maxy])
plt.legend()
width = stop_date_early - start_date_early
plt.gca().add_patch(Rectangle((start_date_early, 0), width, maxy,
                              facecolor="orange", alpha=0.2))
width = stop_date_late - start_date_late
plt.gca().add_patch(Rectangle((start_date_late, 0), width, maxy,
                              facecolor="orange", alpha=0.2))

plt.xlabel("Date")
plt.ylabel("Number of follow-operations")
plt.savefig("num_follow_ops.png")


###############################################################################
# Auto-Follow stats
###############################################################################
plt.figure(figsize=(12, 6))
plt.title("New followers per post within 2 minutes after creation")
label = "Mean number of new followers"
plt.plot_date(post_dates, mean_fops, label=label, **args)
label = "Median number of new followers"
plt.plot_date(post_dates, median_fops, label=label, **args)
label = "Maximum number of new followers"
plt.plot_date(post_dates, max_fops, label=label, **args)
plt.grid()
plt.ylim([0, max(max_fops) * 1.2])
plt.legend()
plt.xlabel("Date")
plt.ylabel("Number of followers")
plt.savefig("new_follower_stats.png")


###############################################################################
# Unique authors
###############################################################################
plt.figure(figsize=(12, 6))
plt.title("Number of posts and authors per day")
label = "Unique authors per day"
plt.plot_date(post_dates, unique_authors_per_day, label=label, **args)
label = "Unique authors wrt to all previous days"
plt.plot_date(post_dates, unique_authors, label=label, **args)
label = "Number of posts created"
plt.plot_date(posts_per_day.xrange('key', False),
              posts_per_day.yrange('key', False), label=label, **args)
plt.grid()
plt.legend()
plt.xlabel("Date")
plt.ylim([0, max(unique_authors)*1.2])
plt.ylabel("Number of authors")
plt.savefig("unique_authors.png")


###############################################################################
# Apply cuts
###############################################################################

fops_per_acc_early = hist()
fops_per_acc_late = hist()
for p in posts:
    if 'fops' not in p:
        continue
    if start_date_early <= p['created'] < stop_date_early:
        for fop in p['fops']:
            fops_per_acc_early.fill(fop['follower'])

    if start_date_late <= p['created'] < stop_date_late:
        for fop in p['fops']:
            fops_per_acc_late.fill(fop['follower'])



print(fops_per_acc_early.xrange()[:100])
print(fops_per_acc_early.yrange()[:100])

print(fops_per_acc_late.xrange()[:100])
print(fops_per_acc_late.yrange()[:100])

hlineargs = {'linestyle':"dashed", 'color':"orange"}

fig = plt.figure(figsize=(12, 6))

title = "First week of May 2018:\nAccounts ordered by number of " \
        "follow-operations"
xlabel = "Account number"
ylabel = "Number of follow-ops"
p1 = fig.add_subplot(121, title=title, xlabel=xlabel, ylabel=ylabel)
xrange = range(len(fops_per_acc_early.xrange()[:MAX_ACCS]))
label = "Number of follow operations"
p1.plot(xrange, fops_per_acc_early.yrange()[:MAX_ACCS], label=label)
p1.axhline(MIN_FOP_CUT, **hlineargs)
p1.axhline(MAX_FOP_CUT, **hlineargs)
p1.grid()

title = "Third week of May 2018:\nAccounts ordered by number of " \
        "follow-operations"
xlabel = "Account number"
ylabel = "Number of follow-ops"
xrange = range(len(fops_per_acc_late.xrange()[:MAX_ACCS]))
p2 = fig.add_subplot(122, title=title, xlabel=xlabel, ylabel=ylabel)
label = "Number of follow operations"
p2.plot(xrange, fops_per_acc_late.yrange()[:MAX_ACCS], label=label)
p2.axhline(MIN_FOP_CUT, **hlineargs)
p2.axhline(MAX_FOP_CUT, **hlineargs)
p2.grid()

plt.savefig("fops_per_acc.png")


early_accs = set(fops_per_acc_early.xrange()[:ACC_NUM_FOP_CUT])
late_accs = set(fops_per_acc_late.xrange()[:ACC_NUM_FOP_CUT])
overlap = early_accs and late_accs
only_in_late = late_accs - early_accs

print("Accs in both (%d): %s" % (len(overlap), overlap))
print("Accs only late: (%d): %s" % (len(only_in_late), only_in_late))


accs_in_fop_cut = set()
for follower, ops in zip(fops_per_acc_late.xrange(),
                         fops_per_acc_late.yrange()):
    if MIN_FOP_CUT <= ops < MAX_FOP_CUT:
        accs_in_fop_cut |= set([follower])

print("Accs in fop cut (%d): %s" % (len(accs_in_fop_cut),
                                    accs_in_fop_cut))

with open("follower-bots.txt", "w") as f:
    for acc in accs_in_fop_cut:
        f.write("%s\n" % acc)
