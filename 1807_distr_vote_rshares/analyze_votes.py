import shelve
from datetime import datetime
from mongostorage import MongoStorage
import sys
import numpy as np

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

qstart = datetime(2018, int(sys.argv[1]), int(sys.argv[2]))

s = shelve.open("posts-%d%02d%02d.shelf" % (qstart.year,
                                            qstart.month,
                                            qstart.day))
posts = s['posts']
s.close()

recovery_accounts = {}
m = MongoStorage()

all_rshares = 0
bot_rshares = 0
dapp_rshares = 0
cleaner_rshares = 0
com_rshares = 0
self_rshares = 0
self_rshares_ext = 0
special_rshares = 0
other_rshares = 0
sbd_per_rshare = []
abs_rshares = 0
flag_rshares = 0
nposts = 0
ncomments = 0
nvotes = 0
authors = set()
voters = set()
root_authors = set()

# votes = {}
for post in posts:
    if post['depth'] > 0:
        ncomments += 1
    else:
        nposts += 1
        root_authors |= set([post['author']])

    post_rshares = 0
    authors |= set([post['author']])
    # created = post['created'].date()
    for vote in post['active_votes']:
        nvotes += 1
        voter = vote['voter']
        rshares = vote['rshares']
        post_rshares += rshares
        voters |= set([voter])

        if voter not in recovery_accounts and \
           voter not in bots and voter not in dapps:
            cond = {'name': voter}
            projection = {'_id': 0, 'recovery_account': 1}
            acc = m.Accounts.find_one(cond, projection=projection)
            if not acc:
                acc = {'recovery_account': voter}
            recovery_accounts[voter] = acc['recovery_account']

        all_rshares += rshares
        abs_rshares += abs(rshares)
        if rshares < 0:
            flag_rshares += abs(rshares)

        if voter in bots:
            bot_rshares += rshares
        elif voter in dapps:
            dapp_rshares += rshares
        elif voter == post['author']:
            self_rshares += rshares
        elif recovery_accounts[voter] == post['author']:
            self_rshares_ext += rshares
        elif voter in cleaners:
            cleaner_rshares += rshares
        elif voter in communities:
            com_rshares += rshares
        elif voter in special:
            special_rshares += rshares
        else:
            # if rshares > 1e13:
            #     if voter not in votes:
            #         votes[voter] = 0
            #     votes[voter] += rshares
            other_rshares += vote['rshares']

    if post['beneficiaries'] == '[]' and post_rshares > 0 and \
       post['total_payout_value'] > 1:
        payout = float(post['total_payout_value'] +
                       post['curator_payout_value'])
        # print(payout, post_rshares, payout / post_rshares)
        sbd_per_rshare.append(payout / (post_rshares))


median_sbd_per_rshare = np.median(sbd_per_rshare)

print("%s - bot: %.1f%%, dapp: %.1f%%, self: %.1f%%, p: %d, c: %d, "
      "a: %d, sbd/tvest: %.1f" % (qstart, (bot_rshares * 100 / all_rshares),
                                  (dapp_rshares * 100 / all_rshares),
                                  (self_rshares * 100 / all_rshares),
                                  nposts, ncomments, len(authors),
                                  median_sbd_per_rshare * 1e12))

s = shelve.open("rshares-%d%02d%02d.shelf" % (qstart.year,
                                              qstart.month,
                                              qstart.day))
s['date'] = qstart
s['all_rshares'] = all_rshares
s['bot_rshares'] = bot_rshares
s['dapp_rshares'] = dapp_rshares
s['cleaner_rshares'] = cleaner_rshares
s['com_rshares'] = com_rshares
s['self_rshares'] = self_rshares
s['self_rshares_ext'] = self_rshares + self_rshares_ext
s['special_rshares'] = special_rshares
s['other_rshares'] = other_rshares
s['median_sbd_per_rshare'] = median_sbd_per_rshare
s['nposts'] = nposts
s['ncomments'] = ncomments
s['nvotes'] = nvotes
s['abs_rshares'] = abs_rshares
s['flag_rshares'] = flag_rshares
s['nauthors'] = len(authors)
s['nvoters'] = len(voters)
s['nrootauthors'] = len(root_authors)
s.close()
