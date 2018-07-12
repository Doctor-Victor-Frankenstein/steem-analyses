from mongostorage import MongoStorage
from datetime import datetime, timedelta
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def effective_vests(account):
    return account['vesting_shares'] + \
        account['received_vesting_shares'] - \
        account['delegated_vesting_shares']

def load_from_file(filename):
    accs = []
    with open(filename) as f:
        for line in f.readlines():
            if line.endswith("\n"):
                line = line[:-1]
            accs.append(line)
    return accs

bots = load_from_file("bots.txt")
dapps = load_from_file("dapps.txt")
cleaners = load_from_file("cleaners.txt")
communities = load_from_file("communities.txt")
special = load_from_file("special.txt")

all = bots + dapps + cleaners + communities + special

print(len(all))

m = MongoStorage()

all_vests = 0
active_vests = 0
dapp_vests = 0
bid_bot_vests = 0
cleaners_vests = 0
community_vests = 0
special_vests = 0
other_vests = 0
delegated_vests = 0

projection = {'_id': 0, 'vesting_shares': 1,
              'delegated_vesting_shares': 1,
              'received_vesting_shares': 1, 'last_vote_time': 1,
              'name': 1}
steem_delegated_vests = 0

for acc in m.Accounts.find(projection=projection):
    vests = effective_vests(acc)
    all_vests += vests
    delegated_vests += acc['delegated_vesting_shares']
    if acc['name'] == "steem":
        steem_delegated_vests += acc['delegated_vesting_shares']
    if acc['last_vote_time'] < datetime.utcnow() - timedelta(days=30):
        continue
    active_vests += vests
    if acc['name'] in bots:
        bid_bot_vests += vests
    elif acc['name'] in dapps:
        dapp_vests += vests
    elif acc['name'] in cleaners:
        cleaners_vests += vests
    elif acc['name'] in communities:
        community_vests += vests
    elif acc['name'] in special:
        special_vests += vests
    else:
        other_vests += vests


print("All vests: %d MVESTS" % (all_vests/1e6))
print("Active vests: %d MVESTS" % (active_vests/1e6))
print("Bid-bot vests: %d MVESTS" % (bid_bot_vests/1e6))
print("Dapp vests: %d MVESTS" % (dapp_vests/1e6))
print("Cleaners vests: %d MVESTS" % (cleaners_vests/1e6))

print("bid-bots from all: %.2f%%" % (bid_bot_vests * 100 / all_vests))
print("bid-bots from active: %.2f%%" % (bid_bot_vests * 100 / active_vests))
print("Dapps from active: %.2f%%" % (dapp_vests * 100 / active_vests))
print("Cleaners from active: %.2f%%" % (cleaners_vests * 100 / active_vests))

args = {'autopct':"%.1f%%", 'pctdistance': 0.9, 'rotatelabels': False,
        'labeldistance': 1.1, 'startangle': 90}

fig = plt.figure(figsize=(12, 5.5))
other = all_vests - active_vests + other_vests - steem_delegated_vests
data = [bid_bot_vests, dapp_vests, cleaners_vests, community_vests,
        special_vests, steem_delegated_vests, other]
labels = ['Bid-bots', 'Dapps', 'Cleaners', 'Communities',
          'Special accounts', '@steem\ndelegations', 'all others']
p1 = fig.add_subplot(121, title='Distribution of all account VESTS')
p1.pie(data, labels=labels, **args)

other = other_vests - steem_delegated_vests
data = [bid_bot_vests, dapp_vests, cleaners_vests, community_vests,
        special_vests, steem_delegated_vests, other]
labels = ['Bid-bots', 'Dapps', 'Cleaners', 'Communities',
          'Special accounts', '@steem\ndelegations', 'all others']

p2 = fig.add_subplot(122, title='Distribution of active account VESTS')
p2.pie(data, labels=labels, **args)
# plt.tight_layout()
plt.savefig("active_vests_distribution")


plt.figure(figsize=(6, 6))
data = [all_vests - delegated_vests, delegated_vests]
labels = ['VESTS with owner', 'VESTS delegated to\nother accounts']
plt.pie(data, labels=labels, **args)
plt.title("Distribution of held and delegated vesting shares")
plt.savefig("delegated_vests.png")
