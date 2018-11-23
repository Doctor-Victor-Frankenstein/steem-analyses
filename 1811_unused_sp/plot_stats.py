import shelve
from datetime import datetime, timedelta
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

start_date = datetime(2018, 9, 1)
end_date = datetime(2018, 11, 22)

date = start_date

comment_author_dates = []
post_counts = []
comment_counts = []
author_counts = []
root_author_counts = []
comment_author_counts = []

voters = {}
rshares = {}

while date <= end_date:
    s = shelve.open("stats-%d-%02d-%02d.shelf" %
                    (date.year, date.month, date.day))
    stats = s['stats']
    s.close()
    comment_author_dates.append(date)
    post_counts.append(stats['post_count'])
    comment_counts.append(stats['comment_count'])
    author_counts.append(stats['authors'])
    root_author_counts.append(stats['root_authors'])
    comment_author_counts.append(stats['comment_authors'])
    for d in stats['votes']:
        if d not in voters:
            voters[d] = set()
            rshares[d] = 0
        voters[d] |= set(stats['votes'][d]['voters'])
        rshares[d] += stats['votes'][d]['rshares']

    date += timedelta(days=1)


fig = plt.figure(figsize=(12,6))
p1 = fig.add_subplot(121, title="Number of posts and comments per day",
                     xlabel="Date", ylabel="Number of posts/comments")
args = {'linestyle': '-', 'marker': '.'}
p1.plot_date(comment_author_dates, post_counts, label="Root posts",
             **args)
p1.plot_date(comment_author_dates, comment_counts, label="Comments",
             **args)
p1.grid()
p1.legend()

p2 = fig.add_subplot(122, title="Number of authors per day",
                     xlabel="Date", ylabel="Number of authors")
p2.plot_date(comment_author_dates, root_author_counts,
             label="Root post authors", **args)
p2.plot_date(comment_author_dates, comment_author_counts,
             label="Comment authors", **args)
p2.plot_date(comment_author_dates, author_counts,
             label="Total authors", **args)
p2.grid()
p2.legend()
fig.autofmt_xdate(rotation=45)
plt.savefig("posts_per_day.png")

fig = plt.figure(figsize=(12, 6))
p1 = fig.add_subplot(121, title="Number of voters per day",
                     xlabel="Date", ylabel="Number of voters")
xrange = sorted(voters.keys())[7:-1]
yrange = [len(voters[k]) for k in xrange]
p1.plot_date(xrange, yrange, label="Voters", **args)
p1.grid()
p1.legend()

p2 = fig.add_subplot(122, title="Sum of vote rshares per day",
                     xlabel="Date", ylabel="Sum of vote rshares")
xrange = sorted(rshares.keys())[7:-1]
yrange = [rshares[k] for k in xrange]
p2.plot_date(xrange, yrange, label="Rshares", **args)
p2.grid()
p2.legend()
fig.autofmt_xdate(rotation=45)
plt.savefig("votes_per_day.png")
