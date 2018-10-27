import shelve
import sys
from datetime import timedelta
from beem.utils import parse_time, addTzInfo
from hist import hist

s = shelve.open(sys.argv[1])
posts = s['posts']
s.close()

rshares_by_day = {}
percent_by_day = {}
zero_voters = hist()
zero_votees = hist()

for post in posts:
    for vote in post['active_votes']:
        time = parse_time(vote['time'])
        if time - addTzInfo(post['created']) > \
           timedelta(days=6.99):
            continue
        rshares = int(vote['rshares'])
        percent = int(vote['percent']) / 100
        date = time.date()
        if rshares < 0:
            continue  # skip flags
        if percent <= 0:
            continue  # skip unvotes & zero-value flags
        if date not in rshares_by_day:
            rshares_by_day[date] = []
            percent_by_day[date] = []
        rshares_by_day[date].append(rshares)
        percent_by_day[date].append(percent)

        if percent > 0 and rshares == 0:
            zero_voters.fill(vote['voter'])
            zero_votees.fill(post['author'])


s = shelve.open(sys.argv[1].replace("posts", "stats"))
s['rshares'] = rshares_by_day
s['percentages'] = percent_by_day
s['zero_voters'] = zero_voters
s['zero_votees'] = zero_votees
s.close()
