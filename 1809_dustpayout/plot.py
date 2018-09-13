import shelve
from datetime import datetime, timedelta, date
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from beem import Steem

# minimum rshares/VESTS/SP to get a payout over time
# absolute numbers of posts/comments with votes but without payout
# relative numbers

def datestr(date):
    return "%04d-%02d-%02d" % (date.year, date.month, date.day)

stats = {'dates': []}

keys = ['total_rshares', 'nposts', 'nposts_wo_votes',
        'nposts_w_votes_wo_payout', 'post_rshares', 'post_rshares_unpaid',
        'ncomments', 'ncomments_wo_votes', 'ncomments_w_votes_wo_payout',
        'comment_rshares', 'comment_rshares_unpaid', 'mean_sbd_per_rshares',
        'total_rewards', 'median_sbd_per_rshares']
for key in keys:
    stats[key] = []

start_date = datetime(2018, 7, 1)
while start_date < datetime(2018, 9, 1):
    print(start_date)
    s = shelve.open("stats-%s.shelf" % (datestr(start_date)))
    daystats = s['stats']
    s.close()
    stats['dates'].append(start_date.date())
    for key in keys:
        stats[key].append(daystats[key])

    start_date += timedelta(days=1)

args = {'linestyle': '-', 'marker': '.'}

###############################################################################
# Absolute numbers of posts/comments
###############################################################################
fig = plt.figure(figsize=(12, 6))
p1 = fig.add_subplot(121, title="Root posts - absolute numbers",
                     xlabel="Post creation date",
                     ylabel="Number of posts")
p1.plot_date(stats['dates'], stats['nposts'], **args,
             label="Number of posts created per day")
p1.plot_date(stats['dates'], stats['nposts_wo_votes'],
             **args, label="Number of posts without a vote")
p1.plot_date(stats['dates'], stats['nposts_w_votes_wo_payout'], **args,
             label="Number of posts w/ votes but w/o payout")
p1.grid()
p1.legend()
p1.set_ylim([0, max(stats['nposts']) * 1.5])

p2 = fig.add_subplot(122, title="Comments - absolute numbers",
                     xlabel="Comment creation date",
                     ylabel="Number of comments")
p2.plot_date(stats['dates'], stats['ncomments'], **args,
             label="Number of comments created per day")
p2.plot_date(stats['dates'], stats['ncomments_wo_votes'],
             **args, label="Number of comments without a vote")
p2.plot_date(stats['dates'], stats['ncomments_w_votes_wo_payout'], **args,
             label="Number of comments w/ votes but w/o payout")
p2.grid()
p2.legend()
p2.set_ylim([0, max(stats['ncomments']) * 1.5])

plt.xlabel("Post creation date")
plt.gcf().autofmt_xdate(rotation=30)
plt.savefig('nposts_absolute.png')


###############################################################################
# Relative numbers of posts/comments
###############################################################################
rel_posts_wo_votes = [stats['nposts_wo_votes'][i] * 100 /
                      stats['nposts'][i] for i in range(len(stats['dates']))]
rel_posts_wo_payout = [stats['nposts_w_votes_wo_payout'][i] * 100 /
                       stats['nposts'][i] for i in range(len(stats['dates']))]
rel_comments_wo_votes = [stats['ncomments_wo_votes'][i] * 100 /
                      stats['ncomments'][i] for i in range(len(stats['dates']))]
rel_comments_wo_payout = [stats['ncomments_w_votes_wo_payout'][i] * 100 /
                       stats['ncomments'][i] for i in range(len(stats['dates']))]

plt.figure(figsize=(12, 6))
plt.plot_date(stats['dates'], rel_posts_wo_votes,
              label="Posts w/o votes", **args)
plt.plot_date(stats['dates'], rel_posts_wo_payout,
              label="Posts w/ votes but w/o payout", **args)
plt.plot_date(stats['dates'], rel_comments_wo_votes,
              label="Comments w/o votes", **args)
plt.plot_date(stats['dates'], rel_comments_wo_payout,
              label="Comments w/ votes but w/o payout", **args)
plt.grid()
plt.legend()
plt.ylim([0, 100])
plt.title("Relative number of posts and comments\n"
          "without votes, or with votes but without payout")
plt.ylabel("Relative shares (%)")
plt.xlabel("Post creation date")
plt.gcf().autofmt_xdate(rotation=30)
plt.savefig('nposts_relative.png')


###############################################################################
# Absolute & relative number of "wasted" rshares
###############################################################################
fig = plt.figure(figsize=(12, 6))
all_rshares = [stats['post_rshares'][i] + stats['comment_rshares'][i]
               for i in range(len(stats['dates']))]
unpaid_rshares = [stats['post_rshares_unpaid'][i] +
                  stats['comment_rshares_unpaid'][i]
                  for i in range(len(stats['dates']))]

p1 = fig.add_subplot(121, title="Absolute number of\n"
                     "Post and Comment vote rshares",
                     xlabel="Post creation date",
                     ylabel="rshares")
p1.plot_date(stats['dates'], all_rshares, label="Total vote rshares", **args)
p1.plot_date(stats['dates'], stats['post_rshares'],
              label="Total post vote Rshares", **args)
p1.plot_date(stats['dates'], stats['comment_rshares'],
              label="Total comment vote Rshares", **args)
p1.plot_date(stats['dates'], unpaid_rshares, label="'Unpaid' vote rshares",
             **args)
p1.plot_date(stats['dates'], stats['post_rshares_unpaid'],
              label="'Unpaid' post vote Rshares", **args)
p1.plot_date(stats['dates'], stats['comment_rshares_unpaid'],
              label="'Unpaid' comment vote Rshares", **args)
p1.grid()
p1.legend()

rel_unpaid_rshares = [unpaid_rshares[i] * 100 / all_rshares[i]
                      for i in range(len(stats['dates']))]
rel_unpaid_post_rshares = [stats['post_rshares_unpaid'][i] * 100 /
                           stats['post_rshares'][i]
                           for i in range(len(stats['dates']))]
rel_unpaid_comment_rshares = [stats['comment_rshares_unpaid'][i] * 100 /
                              stats['comment_rshares'][i]
                              for i in range(len(stats['dates']))]
p2 = fig.add_subplot(122, title="Relative number of 'unpaid'\n"
                     "Post and Comment vote rshares",
                     xlabel="Post creation date",
                     ylabel="Relative Number (%)")
p2.plot_date(stats['dates'], rel_unpaid_rshares, **args,
             label="Relative number of all 'unpaid' vote rshares")
p2.plot_date(stats['dates'], rel_unpaid_post_rshares, **args,
             label="Relative number of 'unpaid' Post vote rshares")
p2.plot_date(stats['dates'], rel_unpaid_comment_rshares, **args,
             label="Relative number of 'unpaid' Comment vote rshares")
p2.grid()
p2.legend()

plt.gcf().autofmt_xdate(rotation=30)
plt.savefig("rshares.png")

###############################################################################
# Mean SBD/rshares
###############################################################################
s = Steem()
mean_rshares_for_min_payout = [(0.02 / x) for x in
                               stats['mean_sbd_per_rshares']]
median_rshares_for_min_payout = [(0.02 / x) for x in
                                 stats['median_sbd_per_rshares']]
plt.figure(figsize=(12, 6))
plt.plot_date(stats['dates'], mean_rshares_for_min_payout,
              label="Mean rshares req. for 0.02 STU", **args)
# plt.plot_date(stats['dates'], median_rshares_for_min_payout,
#               label="Median rshares req. for 0.02 STU", **args)
plt.axhline(s.sp_to_rshares(200), label="200 SP 100% upvote", color='red')
plt.axhline(s.sp_to_rshares(300), label="300 SP 100% upvote", color='orange')
plt.axhline(s.sp_to_rshares(400), label="400 SP 100% upvote", color='green')
plt.grid()
plt.legend()
plt.title("rshares (SP) required for a 0.02 STU payout")
plt.ylabel("rshares")
plt.xlabel("Post creation date")
plt.gcf().autofmt_xdate(rotation=30)
plt.ylim([0, max(mean_rshares_for_min_payout) * 1.5])
plt.savefig("sbd_per_rshares.png")



mean_total_rewards = sum(stats['total_rewards']) / len(stats['dates'])
mean_rel_unpaid_rshares = np.mean(rel_unpaid_rshares)

print("Mean rel. unpaid rshares", mean_rel_unpaid_rshares)
print("Mean total rewards per day", mean_total_rewards)
print("Mean total unpaid rewards per day", mean_total_rewards *
      (mean_rel_unpaid_rshares / 100))
