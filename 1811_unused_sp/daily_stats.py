import shelve
import sys
from beem.utils import parse_time, addTzInfo
from datetime import timedelta

s = shelve.open(sys.argv[1])
posts = s['posts']
s.close()

authors = set()
root_authors = set()
comment_authors = set()

votes = {}

post_count = 0
comment_count = 0

for post in posts:
    created = addTzInfo(post['created'])
    authors |= set([post['author']])
    if post['depth'] > 0:
        comment_authors |= set([post['author']])
        comment_count += 1
    else:
        root_authors |= set([post['author']])
        post_count += 1
    for v in post['active_votes']:
        time = parse_time(v['time'])
        date = time.date()
        if time - created > timedelta(days=7):
            date = created.date()
        if date not in votes:
            votes[date] = {'voters': set(), 'rshares': 0}
        votes[date]['voters'] |= set([v['voter']])
        votes[date]['rshares'] += abs(int(v['rshares']))


stats = {'authors': len(authors), 'root_authors': len(root_authors),
         'comment_authors': len(comment_authors), 'votes': votes,
         'post_count': post_count, 'comment_count': comment_count}
# print(stats)

s = shelve.open(sys.argv[1].replace("posts", "stats"))
s['stats'] = stats
s.close()
