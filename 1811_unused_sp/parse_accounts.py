import sys
import shelve
from beem import Steem
from beem.amount import Amount
from datetime import datetime, timedelta
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

# 200,401,648 STEEM
# 403,671,878,952 VESTS
# 0.0004964   S/V

s = shelve.open("accounts.shelf")
accounts = s['accounts']
s.close()

stm = Steem()
steem_per_mvests = stm.get_steem_per_mvest()
exclude = ['steem', 'steemit']

cur_date = datetime(2018, 11, 23)

intervals = [3, 7, 14, 28, 26*7, 52*7, 5*52*7, 100*52*7]
labels = ['<3 days ago', '3-7 days ago', '1-2 weeks ago', '2-4 weeks ago',
          '4-26 weeks ago', '0.5-1 year ago', 'more than\na year ago', 'never']
sp_dist = {}
acc_dist = {}

top_idle = []

for i in intervals:
    sp_dist[i] = 0
    acc_dist[i] = 0

sp_excluded = 0

for acc in accounts:

    sys.stdout.write("%s\r" % acc['name'])
    sp = (Amount(acc['vesting_shares']) +
          Amount(acc['received_vesting_shares']) -
          Amount(acc['delegated_vesting_shares'])).amount / \
          1e6 * steem_per_mvests

    if len(sys.argv) > 1 and acc['name'] in exclude:
        sp_excluded += sp
        continue

    lv_date = acc['last_vote_time']
    days = (cur_date - lv_date).days
    if days > 365 and sp > 1000:
        top_idle.append({'name': acc['name'], 'sp': sp})
    for i in intervals:
        if days < i:
            sp_dist[i] += sp/1e6
            acc_dist[i] += 1e-3
            break

print("SP Distribution:", sp_dist)
print("Account distribution:", acc_dist)
print("SP Excluded:", sp_excluded)

idle_vals = []
idle_labels = []
for idle in sorted(top_idle, key=lambda k: k['sp'], reverse=True)[:20]:
    idle_labels.append(idle['name'])
    idle_vals.append(idle['sp']/1e6)


fig = plt.figure(figsize=(12, 6))
xticks = list(range(len(acc_dist)))

exclude_str = ""
file_suffix = ""
if len(sys.argv) > 1:
    exclude_str = "\n(excluding Steemit/exchange-related accounts)"
    file_suffix = "_exl"
p1 = fig.add_subplot(121, xlabel="Last vote", ylabel="Number of accounts [1k]",
                     title="Distribution of accounts based on their last vote%s" % (exclude_str))
p1.grid()
p1.bar(xticks, [acc_dist[k] for k in acc_dist])
p1.set_xticks(xticks)
p1.set_xticklabels(labels)

p2 = fig.add_subplot(122, xlabel="Last vote", ylabel="Sum of account SP [Million SP]",
                     title="Distribution of SP based on their last vote%s" % (exclude_str))
p2.grid()
p2.bar(xticks, [sp_dist[k] for k in sp_dist])
p2.set_xticks(xticks)
p2.set_xticklabels(labels)

fig.autofmt_xdate(rotation=45)
plt.savefig('acc_distribution%s.png' % (file_suffix))

xticks = list(range(len(idle_labels)))
fig = plt.figure(figsize=(12, 6))
plt.grid()
plt.bar(xticks, idle_vals)
plt.title("Top %d accounts by SP that haven't voted for at least a year" %
          (len(idle_labels)))
plt.ylabel("SteemPower [Million SP]")
plt.xticks(xticks, idle_labels, rotation=45)
plt.savefig('idle_accounts%s.png' % (file_suffix))
