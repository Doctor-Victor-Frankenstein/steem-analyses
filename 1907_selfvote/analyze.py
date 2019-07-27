import shelve
import sys
from collections import Counter
from prettytable import PrettyTable
from datetime import date

dapps = ['utopian-io', 'steemhunt', 'steempress-io', 'dtube',
         'dsound', 'busy.pay', 'partiko', 'actifit', 'oracle-d',
         'fundition', 'tasteem', 'threespeak', 'esteemapp', 'ntopaz',
         'dlive', 'dmania']

bots = ['minnowbooster', 'smartmarket', 'postpromoter', 'tipu',
        'upme', 'bro-rando', 'randowhale', 'ocdb', 'steemmonsters',
        'minnowsupport', 'sct.voter', 'triplea.bot', 'leo.voter',
        'neoxiancityvb', 'stembot', 'buildawhale', 'booster',
        'boomerang', 'minnowhelper', 'lovejuice', 'sneaky-ninja',
        'appreciator', 'smartsteem', 'mercurybot', 'upmewhale',
        'steembloggers', 'voterunner', 'bid4joy', 'nado.bot',
        'redlambo', 'inciter', 'therising', 'luckyvotes',
        'postdoctor', 'brupvoter', 'isotonic', 'spydo',
        'onlyprofitbot', 'mitsuko', 'sunrawhale', 'honestbot',
        'promobot', 'dailyupvotes', 'thebot', 'minnowvotes', 'rocky1',
        'redwhale', 'brandonfrye', 'emperorofnaps', 'profitvote',
        'siditech', 'automation', 'profitbot', 'whalecreator',
        'oceanwhale', 'edensgarden', 'sureshot', 'joeparys',
        'bdvoter', 'whalepromobot', 'alfanso', 'pwrup', 'upmyvote',
        'jerrybanfield', 'pushup', 'fuzzyvest']

posts = []
for fname in sys.argv[1:]:
    print("Reading %s" % (fname))
    s = shelve.open(fname)
    posts.extend(s['posts'])
    s.close()

voter_author_map_rshares = {}
voter_author_map_nvotes = {}
sv_map = {}

total_rshares = 0
sv_rshares = 0
flag_rshares = 0
dapp_rshares = 0
bot_rshares = 0
mindate = date(9999, 1, 1)
maxdate = date(1970, 1, 1)
voters = {}
authors = {}

for p in posts:  # [:10000]:
    # print(p['author'], p['active_votes'])
    author = p['author']
    date = p['created'].date()
    mindate = min([mindate, date])
    maxdate = max([maxdate, date])
    if date not in authors:
        authors[date] = set()
    if date not in voters:
        voters[date] = set()
    authors[date] |= set([author])
    for v in p['active_votes']:
        rshares = int(v['rshares'])
        voter = v['voter']
        voters[date] |= set([voter])
        if rshares < 0:
            flag_rshares += abs(rshares)
            continue
        total_rshares += rshares
        if voter in dapps:
            dapp_rshares += rshares
        if voter in bots:
            bot_rshares += rshares
        if voter not in voter_author_map_rshares:
            voter_author_map_rshares[voter] = Counter()
            voter_author_map_nvotes[voter] = Counter()
            sv_map[voter] = 0
        if voter == author:
            sv_rshares += rshares
            sv_map[voter] += rshares
        voter_author_map_rshares[voter].update({author: rshares})
        voter_author_map_nvotes[voter].update([author])

def sum_counter(counter):
    return sum(counter.values())

def topn_counter(counter, n):
    return sum([v for k, v in counter.most_common(n)])

def fmt(rshares):
    return "%1.f bn" % (rshares / 1e9)

top1_rshares = 0
top3_rshares = 0
top5_rshares = 0
top10_rshares = 0

for voter in voter_author_map_nvotes:
    total_voter_rshares = sum_counter(voter_author_map_rshares[voter])
    if total_voter_rshares == 0:
        continue
    top1_voter_rshares = topn_counter(voter_author_map_rshares[voter], 1)
    if top1_voter_rshares == total_voter_rshares:
        top1_rshares += rshares
    top3_voter_rshares = topn_counter(voter_author_map_rshares[voter], 3)
    if top3_voter_rshares / total_voter_rshares >= 0.8:
        top3_rshares += top3_voter_rshares
    top5_voter_rshares = topn_counter(voter_author_map_rshares[voter], 5)
    if top5_voter_rshares / total_voter_rshares >= 0.8:
        top5_rshares += top5_voter_rshares
    top10_voter_rshares = topn_counter(voter_author_map_rshares[voter], 10)
    if top10_voter_rshares / total_voter_rshares >= 0.8:
        top10_rshares += top10_voter_rshares

for date in voters:
    voters[date] = len(voters[date])

for date in authors:
    authors[date] = len(authors[date])

results = {
    'mindate': mindate,
    'maxdate': maxdate,
    'total_rshares': total_rshares,
    'sv_rshares': sv_rshares,
    'dapp_rshares': dapp_rshares,
    'bot_rshares': bot_rshares,
    'flag_rshares': flag_rshares,
    'top1_rshares': top1_rshares,
    'top3_rshares': top3_rshares,
    'top5_rshares': top5_rshares,
    'top10_rshares': top10_rshares,
    'authors': authors,
    'voters': voters,
}

s = shelve.open("results-%d-%02d-%02d.shelf" % (mindate.year, mindate.month, mindate.day))
s['data'] = results
s.close()
