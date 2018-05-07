#!/usr/bin/python

import shelve
from datetime import datetime
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta
from hist import hist
import sys

STEEM_DUST_VOTE_THRESHOLD = 50000000
HF19_REVERSE_AUCTION_TIME = 30 * 60
HF20_REVERSE_AUCTION_TIME = 15 * 60


def parse_time(block_time):
    return datetime.strptime(block_time, '%Y-%m-%dT%H:%M:%S')


def approx_sqrt(x):
    if x <= 1:
        return x
    # mantissa_bits, leading_1, mantissa_mask are independent of x
    msb_x = x.bit_length() - 1
    msb_z = msb_x >> 1
    msb_x_bit = 1 << msb_x
    msb_z_bit = 1 << msb_z
    mantissa_mask = msb_x_bit-1

    mantissa_x = x & mantissa_mask
    if (msb_x & 1) != 0:
        mantissa_z_hi = msb_z_bit
    else:
        mantissa_z_hi = 0
    mantissa_z_lo = mantissa_x >> (msb_x - msb_z)
    mantissa_z = (mantissa_z_hi | mantissa_z_lo) >> 1
    result = msb_z_bit | mantissa_z
    return result


def pay_curators(max_rewards, total_weight, weights):
    unclaimed_rewards = max_rewards
    #print(total_weight, sum(weights))
    if total_weight > 0:
        for weight in weights:
            claim = int((max_rewards * weight) / total_weight)
            if claim > 0:
                unclaimed_rewards -= claim
            # print(int(max_rewards/1e6), weight, int(claim/1e6),
            #       int(unclaimed_rewards/1e6))

    return unclaimed_rewards


def get_weights(rshares, previous_rshares, age, reverse_auction_time):
    old_weight = approx_sqrt(previous_rshares)
    new_weight = approx_sqrt(previous_rshares + rshares)
    weight = new_weight - old_weight
    max_weight = weight

    # apply reverse auction
    delta_t = min(age, reverse_auction_time)
    weight = int(max_weight * delta_t / reverse_auction_time)
    return weight, max_weight

def get_rshare_reward(rshares, reward_fund_steem, recent_claims):
    rf = reward_fund_steem
    total_claims = recent_claims
    claim = rshares
    payout = rf * claim / total_claims
    return payout

def cashout_comment_helper(reward_tokens, total_weight, weights,
                           HF=19):
    curation_tokens = int(reward_tokens * 2500 / 10000)
    author_tokens = reward_tokens - curation_tokens
    total_vote_weight = sum(weights)
    unclaimed_tokens = pay_curators(curation_tokens, total_weight,
                                    weights)
    curation_tokens -= unclaimed_tokens

    if HF == 19:
        author_tokens += unclaimed_tokens
        unclaimed_tokens = 0

    return {'author': author_tokens, 'curators': curation_tokens,
            'unclaimed': unclaimed_tokens}


def reconstruct_tokens(post):
    author_reward = post['total_payout_value']
    curator_reward = post['curator_payout_value']
    author_tokens = post['author_rewards']
    reward_tokens = author_tokens / author_reward * \
                        (author_reward + curator_reward)
    return int(reward_tokens)


posts = []

month = 4
for day in range(1, 27):
    filename = "posts-2018%02d%02d.shelf" % (month, day)
    print("Processing %s" % (filename))
    s = shelve.open(filename)
    posts.extend(s['posts'])
    s.close()

hf19_author_curator_shares = []
hf20_author_curator_shares = []
hf20v2_author_curator_shares = []
hf20v3_author_curator_shares = []
total_payouts = []
hf19_voting_times = []
hf19_rshares_age_hist = hist()

mismatches = 0
postcount = 0
hf19_total_author_tokens = 0
hf19_total_curator_tokens = 0
hf20_total_author_tokens = 0
hf20_total_curator_tokens = 0
hf20v2_total_author_tokens = 0
hf20v2_total_curator_tokens = 0
hf20v2_total_unclaimed_tokens = 0
hf20v3_total_author_tokens = 0
hf20v3_total_curator_tokens = 0

calc_ref_diffs = []

for post in posts:
    if 'beneficiaries' in post and post['beneficiaries']:
        continue
    #if post['curator_payout_value'] < 0.01:
    #    continue
    created_time = post['created']
    if 'last_payout' in post:
        payout_time = post['last_payout']
    else:
        payout_time = created_time + timedelta(days=7)

    # print("\n", created_time,
    #       post['total_payout_value'], post['curator_payout_value'])

    skip = False
    voters = []

    calc_weight_sum = 0
    rep_weight_sum = 0

    ###########################################################################
    # HF19 cross-checks to filter suitable posts
    ###########################################################################
    hf19_weights = []
    hf19_previous_shares = 0
    hf19_total_weight = 0

    # print(post['total_payout_value'], post['curator_payout_value'])
    for v in sorted(post['active_votes'], key=lambda k: k['time']):
        vote_time = parse_time(v['time'])
        vote_weight = int(v['weight'])
        rshares = int(v['rshares'])
        age = (vote_time - created_time).total_seconds()
        if vote_time > payout_time and rshares != 0:
            # revoted after payout -> no reliable vote time information
            skip = True
            break

        if rshares < 0:
            hf19_weights.append(0)
            continue

        rshares = abs(rshares)

        weight, max_weight = get_weights(rshares,
                                         hf19_previous_shares, age,
                                         HF19_REVERSE_AUCTION_TIME)

        # print("%16s (%3d%%) age: %6d, rshares: %5.1f bn, weight: " \
        #       "%8d (%8d), maxweight: %8d, prev_rhares: %.2f bn" %
        #       (v['voter'], int(v['percent'])/100, age, rshares/1e9,
        #       weight, vote_weight, max_weight,
        #       hf19_previous_shares/1e9))

        calc_weight_sum += weight
        rep_weight_sum += vote_weight

        hf19_previous_shares += rshares
        hf19_total_weight += max_weight

        hf19_weights.append(weight)


        # if hf19_weight > weight + 1 or hf19_weight < weight - 1:
        #     print("***Mismatch*** skipping...")
        #     skip = True


    if abs(calc_weight_sum - rep_weight_sum) > len(hf19_weights):
        mismatches += 1
        skip = True

    if skip:
        continue


    ###########################################################################
    # HF19 processing
    ###########################################################################
    reward_tokens = reconstruct_tokens(post)
    hf19_rewards = cashout_comment_helper(reward_tokens,
                                          hf19_total_weight,
                                          hf19_weights)
    hf19_author_curator_ratio = 100 * hf19_rewards['curators'] / \
                                (hf19_rewards['author'] +
                                 hf19_rewards['curators'])

    assert(reward_tokens == (hf19_rewards['author'] +
                             hf19_rewards['curators']))

    # print("HF19 pay_curators: author: %.3f STEEM, curators %.3f STEEM"
    #       % (hf19_rewards['author']/1000, hf19_rewards['curators']/1000))

    # compare with payout value ratios
    author_payout = float(post['total_payout_value'])
    curator_payout = float(post['curator_payout_value'])
    hf19author_curator_ratio_ref = 100 * curator_payout / \
                                   (author_payout + curator_payout)

    diff = hf19author_curator_ratio_ref - hf19_author_curator_ratio
    calc_ref_diffs.append(diff)

    # skip posts where the calculated ratio and the ratio from the reported
    # values differs by more than 0.5%
    if abs(diff) > 0.5:
        continue

    postcount += 1
    hf19_total_author_tokens += hf19_rewards['author']
    hf19_total_curator_tokens += hf19_rewards['curators']
    hf19_author_curator_shares.append(hf19_author_curator_ratio)
    total_payouts.append(author_payout + curator_payout)

    # print("ref: %5.2f%%, calc: %5.2f%%, diff: %6.2f" %
    #       (hf19author_curator_ratio_ref, hf19_author_curator_ratio,
    #        (hf19author_curator_ratio_ref - hf19_author_curator_ratio)))

    ###########################################################################
    # HF 20 calculations
    ###########################################################################
    hf20_weights = []
    hf20_previous_shares = 0
    hf20_total_weight = 0
    hf20_all_rshares = []
    for v in sorted(post['active_votes'], key=lambda k: k['time']):
        vote_time = parse_time(v['time'])
        age = (vote_time - created_time).total_seconds()
        rshares = int(v['rshares'])
        if rshares < 0:
            hf20_weights.append(0)
            continue
        rshares = abs(rshares)

        # HF 19 iterations
        if age < 60 * 60:
            hf19_voting_times.append(age / 60)
            hf19_rshares_age_hist.fill(int(age / 60), rshares)

        # apply dust vote threshold
        rshares = max(0, rshares - STEEM_DUST_VOTE_THRESHOLD)

        hf20_all_rshares.append(rshares)

        weight, max_weight = get_weights(rshares,
                                         hf20_previous_shares, age,
                                         HF20_REVERSE_AUCTION_TIME)

        hf20_weights.append(weight)
        hf20_previous_shares += rshares
        hf20_total_weight += max_weight

    ###########################################################################
    # HF20 processing
    ###########################################################################
    hf20_rewards = cashout_comment_helper(reward_tokens,
                                          hf20_total_weight,
                                          hf20_weights, HF=20)

    assert(reward_tokens == (hf20_rewards['author'] +
                             hf20_rewards['curators'] +
                             hf20_rewards['unclaimed']))

    hf20_author_curator_ratio = 100 * hf20_rewards['curators'] / \
                                (hf20_rewards['author'] +
                                 hf20_rewards['curators'])

    hf20_total_author_tokens += hf20_rewards['author']
    hf20_total_curator_tokens += hf20_rewards['curators']
    hf20_author_curator_shares.append(hf20_author_curator_ratio)

    ###########################################################################
    # HF 20 v2 calculations
    ###########################################################################
    hf20v2_weights = []
    hf20v2_previous_shares = 0
    hf20v2_total_weight = 0
    hf20v2_all_rshares = []
    for v in sorted(post['active_votes'], key=lambda k: k['time']):
        vote_time = parse_time(v['time'])
        # divide time by two: 30 min -> 15 min
        age = (vote_time - created_time).total_seconds() / 2
        rshares = int(v['rshares'])
        if rshares < 0:
            hf20v2_weights.append(0)
            continue
        rshares = abs(rshares)

        # apply dust vote threshold
        rshares = max(0, rshares - STEEM_DUST_VOTE_THRESHOLD)

        hf20v2_all_rshares.append(rshares)

        weight, max_weight = get_weights(rshares,
                                         hf20v2_previous_shares, age,
                                         HF20_REVERSE_AUCTION_TIME)
        hf20v2_weights.append(weight)

        hf20v2_previous_shares += rshares
        hf20v2_total_weight += max_weight

    ###########################################################################
    # HF20V2v2 processing
    ###########################################################################
    hf20v2_rewards = cashout_comment_helper(reward_tokens,
                                          hf20v2_total_weight,
                                          hf20v2_weights, HF=20)
    assert(reward_tokens == (hf20v2_rewards['author'] +
                             hf20v2_rewards['curators'] +
                             hf20v2_rewards['unclaimed']))

    hf20v2_author_curator_ratio = 100 * hf20v2_rewards['curators'] / \
                                (hf20v2_rewards['author'] +
                                 hf20v2_rewards['curators'])

    hf20v2_total_author_tokens += hf20v2_rewards['author']
    hf20v2_total_curator_tokens += hf20v2_rewards['curators']
    hf20v2_total_unclaimed_tokens += hf20v2_rewards['unclaimed']
    hf20v2_author_curator_shares.append(hf20v2_author_curator_ratio)

    sys.stdout.write("post count: %d\r" % (postcount))


print(len(posts), postcount, mismatches)

###############################################################################
# HF19 differences between calc and reported ratios
###############################################################################
mean = np.mean(calc_ref_diffs)
fig = plt.figure(figsize=(12, 6.5))
plt.hist(calc_ref_diffs, bins=100, label="deviation (%)")
plt.axvline(mean, label="mean deviation: %.3f%%" % (mean))
plt.grid()
plt.legend()
plt.xlabel("ref - calc (%)")
plt.savefig("calc_ref_diffs.png")


###############################################################################
# HF19 voting times
###############################################################################
fig = plt.figure(figsize=(12, 6.5))

title = "Voting times"
xlabel = "Post age (min)"
ylabel = "Number of votes"
ax = fig.add_subplot(121, title=title, xlabel=xlabel, ylabel=ylabel)
ax.hist(hf19_voting_times, bins=60, range=(0, 59))
ax.grid()

title = "Vote value wrt. post age"
xlabel = "Post age (min)"
ylabel = "Total vote rshares"
ax = fig.add_subplot(122, title=title, xlabel=xlabel, ylabel=ylabel)
xrange = hf19_rshares_age_hist.xrange('key')
yrange = hf19_rshares_age_hist.yrange('key')
ax.bar(xrange, yrange)
ax.grid()
plt.tight_layout()
plt.savefig("hf19_voting_times.png")

###############################################################################
# HF19 author/curator share per post
###############################################################################
mean = np.mean(hf19_author_curator_shares)
median = np.median(hf19_author_curator_shares)
fig = plt.figure(figsize=(12, 6.5))
title = "Curator share of total post rewards per post\n" \
        "HF19"
xlabel = "Curator share (%)"
ylabel = "Posts"
ax = fig.add_subplot(121, title=title, xlabel=xlabel, ylabel=ylabel)
ax.hist(hf19_author_curator_shares, bins=25, range=[0, 25],
        label="Curator share of total post rewards")
meanlabel = "Mean curator share: %.1f%%" % (mean)
ax.axvline(mean, linestyle="dashed", linewidth=2, color='red',
           label=meanlabel)
medianlabel = "Median curator share: %.1f%%" % (median)
ax.axvline(median, linestyle="dashed", linewidth=2, color='orange',
           label=medianlabel)
ax.grid()
ax.legend()

title = "Author/curator share of post rewards by total value\n" \
        "HF19"
ax = fig.add_subplot(122, title=title)
ax.pie([hf19_total_author_tokens, hf19_total_curator_tokens],
       labels=['Author rewards', 'Curator rewards'],
       autopct="%.1f%%")

plt.tight_layout()
plt.savefig("hf19_author_curator_shares.png")


###############################################################################
# HF20 author/curator share per post
###############################################################################
mean = np.mean(hf20_author_curator_shares)
median = np.median(hf20_author_curator_shares)
fig = plt.figure(figsize=(12, 6.5))
title = "Curator share of total post rewards per post\n" \
        "HF20, original voting times"
xlabel = "Curator share (%)"
ylabel = "Posts"
ax = fig.add_subplot(121, title=title, xlabel=xlabel, ylabel=ylabel)
ax.hist(hf20_author_curator_shares, bins=25, range=[0, 25],
        label="Curator share of total post rewards")
meanlabel = "Mean curator share: %.1f%%" % (mean)
ax.axvline(mean, linestyle="dashed", linewidth=2, color='red',
           label=meanlabel)
medianlabel = "Median curator share: %.1f%%" % (median)
ax.axvline(median, linestyle="dashed", linewidth=2, color='orange',
           label=medianlabel)
ax.grid()
ax.legend()

title = "Author/curator share of post rewards by total value\n" \
        "HF20, original voting times"
ax = fig.add_subplot(122, title=title)
ax.pie([hf20_total_author_tokens, hf20_total_curator_tokens],
       labels=['Author rewards', 'Curator rewards'],
       autopct="%.1f%%")

plt.tight_layout()
plt.savefig("hf20_author_curator_shares.png")


###############################################################################
# HF20V2 author/curator share per post
###############################################################################
mean = np.mean(hf20v2_author_curator_shares)
median = np.median(hf20v2_author_curator_shares)
fig = plt.figure(figsize=(12, 6.5))
title = "Curator share of total post rewards per post\n" \
        "HF20, reduced voting times by factor 2"
xlabel = "Curator share (%)"
ylabel = "Posts"
ax = fig.add_subplot(121, title=title, xlabel=xlabel, ylabel=ylabel)
ax.hist(hf20v2_author_curator_shares, bins=25, range=[0, 25],
        label="Curator share of total post rewards")
meanlabel = "Mean curator share: %.1f%%" % (mean)
ax.axvline(mean, linestyle="dashed", linewidth=2, color='red',
           label=meanlabel)
medianlabel = "Median curator share: %.1f%%" % (median)
ax.axvline(median, linestyle="dashed", linewidth=2, color='orange',
           label=medianlabel)
ax.grid()
ax.legend()

title = "Author/curator share of post rewards by total value\n" \
        "HF20, reduced voting times by factor 2"
ax = fig.add_subplot(122, title=title)
ax.pie([hf20v2_total_author_tokens, hf20v2_total_curator_tokens],
       labels=['Author rewards', 'Curator rewards'],
       autopct="%.1f%%")

plt.tight_layout()
plt.savefig("hf20v2_author_curator_shares.png")


fig = plt.figure(figsize=(12, 5.5))
title = "Author/curator share of post rewards by total value\n" \
        "HF19"
ax = fig.add_subplot(121, title=title)
ax.pie([hf19_total_author_tokens, hf19_total_curator_tokens],
        labels=['Author tokens', 'Curator tokens'], autopct="%.1f%%")

title = "Author/curator share of post rewards by total value\n" \
        "HF20, reduced voting times by factor 2"
ax = fig.add_subplot(122, title=title)
labels = ['Author tokens', 'Curator tokens', 'Unclaimed tokens']
ax.pie([hf20v2_total_author_tokens, hf20v2_total_curator_tokens,
         hf20v2_total_unclaimed_tokens], labels=labels,
        autopct="%.1f%%")
plt.savefig("unclaimed_tokens.png")
