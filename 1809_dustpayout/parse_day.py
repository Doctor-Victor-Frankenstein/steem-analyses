import shelve
from datetime import datetime, timedelta, date
import sys
import numpy as np

if len(sys.argv) != 2:
    print("ERROR: invalid command line argument count")
    print("Usage: %s [filename.shelf]" % (sys.argv[0]))
    exit(-1)

s = shelve.open(sys.argv[1])
posts = s['posts']
s.close()

stats = {}
stats['total_rshares'] = 0
stats['total_rewards'] = 0

stats['nposts'] = 0
stats['nposts_wo_votes'] = 0
stats['nposts_w_votes_wo_payout'] = 0
stats['post_rshares'] = 0
stats['post_rshares_unpaid'] = 0

stats['ncomments'] = 0
stats['ncomments_wo_votes'] = 0
stats['ncomments_w_votes_wo_payout'] = 0
stats['comment_rshares'] = 0
stats['comment_rshares_unpaid'] = 0

sbd_per_rshares = []

def get_beneficiary_rewards(post):
    if not len(post['beneficiaries']):
        return 0
    bene_weight = sum(int(bene['weight']) for bene in
                       post['beneficiaries']) / 100
    author_weight = 100 - bene_weight
    if author_weight == 0:
        return 0
    return float(post['total_payout_value']) / author_weight * bene_weight


for post in posts:
    rshares = sum([int(v['rshares']) for v in post['active_votes']])
    stats['total_rshares'] += rshares

    if post['depth'] == 0:
        # Posts
        stats['nposts'] += 1
        stats['post_rshares'] += rshares
        if len(post['active_votes']) == 0:
            stats['nposts_wo_votes'] += 1
        elif rshares > 0 and post['max_accepted_payout'] > 0 \
             and post['total_payout_value'] == 0:
            stats['nposts_w_votes_wo_payout'] += 1
            stats['post_rshares_unpaid'] += rshares

    else:
        # Comments
        stats['ncomments'] += 1
        stats['comment_rshares'] += rshares
        if len(post['active_votes']) == 0:
            stats['ncomments_wo_votes'] += 1
        elif rshares > 0 and post['total_payout_value'] == 0:
            stats['ncomments_w_votes_wo_payout'] += 1
            stats['comment_rshares_unpaid'] += rshares

    # rshares per SBD
    rewards = float(post['total_payout_value']) + \
              float(post['curator_payout_value']) + \
              get_beneficiary_rewards(post)

    stats['total_rewards'] += rewards
    if rewards < 1:
        continue
    sbd_per_rshares.append(rewards / rshares)

stats['mean_sbd_per_rshares'] = float(np.mean(sbd_per_rshares))
stats['median_sbd_per_rshares'] = float(np.median(sbd_per_rshares))

target_filename = sys.argv[1].replace('posts', 'stats')
t = shelve.open(target_filename)
t['stats'] = stats
t.close()

print(stats)
