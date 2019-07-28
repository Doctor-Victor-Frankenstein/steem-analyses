import sys
import shelve
from collections import Counter
import numpy as np
import matplotlib as mpl
mpl.use("agg")
import matplotlib.pyplot as plt

TOP = 8
MAX_WITNESS_VOTES = int(sys.argv[2])

s = shelve.open(sys.argv[1])
accounts = s['accounts']
s.close()

top_vests = Counter()
top_voting_vests = Counter()
witnesses = Counter()

for a in accounts:
    ctrld = a['vesting_shares'] + int(sum([int(v) for v in a['proxied_vsf_votes']])/1e6)
    top_vests.update({a['name']: ctrld})
    if len(a['witness_votes']):
        top_voting_vests.update({a['name']: ctrld})
    idx = 0
    for w in a['witness_votes']:
        if idx >= MAX_WITNESS_VOTES:
            ctrld = 0
        idx += 1
        witnesses.update({w: ctrld})

print("Top vests controlled")
for k, v in top_vests.most_common(20):
    print("%16s" % k, "%.3f MV" % (v/1e6))

print("Top vests controlled and voting for witnesses")
vests_map = {}
idx_to_name_map = {}
idx = 0
for k, v in top_voting_vests.most_common():
    vests_map[k] = idx
    idx_to_name_map[idx] = k
    idx += 1
    if idx <= 20:
        print("%16s" % k, "%.3f MV" % (v/1e6))

print("Witness ranks")
rank_map = {}
idx = 1
for k, v, in witnesses.most_common():
    rank_map[k] = idx
    idx += 1
    if idx <= 20:
        print("%16s" % k, "%.3f MV" % (v/1e6))


wvests = {}
for a in accounts:
    name = a['name']
    ctrld = a['vesting_shares'] + int(sum([int(v) for v in a['proxied_vsf_votes']])/1e6)
    idx = 0
    for w in a['witness_votes']:
        if idx >= MAX_WITNESS_VOTES:
            ctrld = 0
        idx += 1
        witnesses.update({w: ctrld})
        if w not in wvests:
            wvests[w] = {'others': 0}
            for i in range(TOP):
                wvests[w][idx_to_name_map[i]] = 0
        if name in vests_map and vests_map[name] < TOP:
            wvests[w][name] = int(ctrld/1e6)
        else:
            wvests[w]['others'] += int(ctrld/1e6)

labels = []
data = {'others': []}
#temp = [idx_to_name_map[i] for i in range(TOP)]
#temp.append('others')
for i in range(TOP):
    data[idx_to_name_map[i]] = []
for w in sorted(wvests, key=lambda k: rank_map[k])[:40]:
    print(rank_map[w], w, wvests[w])
    labels.append("%s (%d)" % (w, rank_map[w]))
    for key in data:
        data[key].append(wvests[w][key])

plt.figure(figsize=(12, 6))
x = np.arange(len(data['others']))
total = np.array([0]*len(x))
for l in data:
    print(l, data[l])
    if max(data[l]) == 0:
        continue
    plt.bar(x, data[l], bottom=total, label=l)
    total += np.array(data[l])
# plt.grid()
plt.legend()
plt.xticks(x, labels)
plt.gcf().autofmt_xdate(rotation=45)
plt.gca().set_ylim([0, max(total)*1.1])
plt.ylabel("MVests")
plt.title("Witness ranks and distribution of the voting VESTs\n"
          "based on up to %d witness votes per account" % (MAX_WITNESS_VOTES))
plt.savefig("witness%d.png" % (MAX_WITNESS_VOTES))
