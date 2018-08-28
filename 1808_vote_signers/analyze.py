from mongostorage import MongoStorage
from beem.wallet import Wallet
import sys
from hist import hist
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

signers = {
    'Smartsteem': 'STM7yk3tav5BFEyppNzHhKaXsMTPw8xYX1B1gWXq6bvtT34uVUKbQ',
    'Minnowbooster': 'STM6H8vJ6v9hd9qMbcyxbySu5HPeQdd4fy7tRsa6fuLczdy8cvRzv',
    'Steemauto': 'STM8WWUYHMdHLgEHidYCztswzfZCViA16EqGkAxt7RG4dWwDpFtCF',
    'Steemdunk': 'STM5TCyGwT3cvehmpuHBoyuWenAh3Sa79XN2Dm7TQEmbNp1NQSJry',
    'Steemconnect': 'STM5khoFYgEg8Mvh989JmXLhgEgwAF78nPRr2xppQgafzWCXe2krQ',
    'Upvotebank': 'STM6nVT8keLnoLoSfiAMTRE2oVqJArmQ1UwdrpqQFJX5j5DVJLxaT',
}

bots = []
with open("bots.txt") as f:
    for line in f.readlines():
        if line.endswith("\n"):
            line = line[:-1]
        bots.append(line)

m = MongoStorage(db_name="steem", host='172.18.0.3', port=27017, user='',
                 passwd='')

total_vote_count = m.Votes.count({'rshares': {"$exists": True}})
total_vote_rshares = 0
syv_count = {}
syv_rshares = {}
bot_count = 0
bot_rshares = 0
voters = {}
all_voters = set()

for signer in signers:
    syv_rshares[signer] = 0
    syv_count[signer] = 0
    voters[signer] = set()

keys = hist()
keys_val = hist()

for op in m.Votes.find({'rshares': {"$exists": True}}):
    # print(op)
    total_vote_rshares += op['rshares']
    all_voters |= set([op['voter']])
    if not op['signer']:
        continue
    for key in op['signer']:
        keys.fill(key)
        keys_val.fill(key, op['rshares'])
    if op['voter'] in bots:
        bot_count += 1
        bot_rshares += op['rshares']
        continue
    for signer in signers:
        if signers[signer] in op['signer']:
            syv_rshares[signer] += op['rshares']
            syv_count[signer] += 1
            voters[signer] |= set([op['voter']])

print("\nTotal number of votes: %d" % (total_vote_count))
print("| Signer | Relative Vote count | Relative vote value | ")
labels = []
by_number = []
by_value = []
for signer in signers:
    rel_number = syv_count[signer] * 100 / total_vote_count
    rel_value = syv_rshares[signer] * 100 / total_vote_rshares
    print("| %s | %.2f%% | %.2f%% |" % (signer, rel_number,
                                        rel_value))
    labels.append(signer)
    by_value.append(syv_rshares[signer])
    by_number.append(syv_count[signer])

print("| Bots | %.2f%% | %.2f%% |" % (bot_count * 100 /
                                      total_vote_count, bot_rshares *
                                      100 / total_vote_rshares))
labels.append("Bid bots")
by_value.append(bot_rshares)
by_number.append(bot_count)

labels.append("All others")
by_value.append(total_vote_rshares - sum(by_value))
by_number.append(total_vote_count - sum(by_number))

fig = plt.figure(figsize=(12, 6))
p1 = fig.add_subplot(121, title="Vote signers by number")
p1.pie(by_number, labels=labels, autopct="%.1f%%")
p2 = fig.add_subplot(122, title="Vote signers by value")
p2.pie(by_value, labels=labels, autopct="%.1f%%")
plt.savefig("share.png")

print("\nTotal number of voters: %d" % (len(all_voters)))
for signer in signers:
    print("| %s | %.2f%% |" % (signer, len(voters[signer]) * 100 /
                               len(all_voters)))

print("\nMost frequent vote signers")
i = 1
w = Wallet()
print("| Rank | #Votes | PublicKey | Account |")
for key, count in zip(keys.xrange()[:10], keys.yrange()[:10]):
    print("| %d | %d | %s | %s |" % (i, count, key,
                                     list(w.getAccountsFromPublicKey(key))))
    i += 1

print("\nMost frequent vote signers by value")
i = 1
w = Wallet()
print("| Rank | #Votes | PublicKey | Account |")
for key, count in zip(keys_val.xrange()[:10], keys_val.yrange()[:10]):
    print("| %d | %d | %s | %s |" % (i, count, key,
                                     list(w.getAccountsFromPublicKey(key))))
    i += 1
