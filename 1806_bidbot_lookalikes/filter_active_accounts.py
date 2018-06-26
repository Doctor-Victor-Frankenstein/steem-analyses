#!/usr/bin/python
import shelve
from datetime import datetime
from beem.utils import parse_time, addTzInfo
from beem.amount import Amount
from beem import Steem

stm = Steem(offline=True)

def effective_vests(a):
    return Amount(a['vesting_shares'], steem_instance=stm) + \
        Amount(a['received_vesting_shares'], steem_instance=stm) - \
        Amount(a['delegated_vesting_shares'], steem_instance=stm)

min_active_timestamp = addTzInfo(datetime(2018, 4, 1))

print("Reading")
s = shelve.open("accounts.shelve")
accounts = s['accounts']
s.close()

print("Processing")
results = {}
for a in accounts:
    if parse_time(a['last_bandwidth_update']) > min_active_timestamp:
        results[a['name']] = a
        results[a['name']]['effective_vests'] = effective_vests(a).amount
        for key in ['balance', 'savings_balance', 'sbd_balance']:
            results[a['name']][key] = Amount(a[key], steem_instance=stm).amount
        for key in ['created', 'last_bandwidth_update',
                    'last_vote_time', 'last_post', 'last_root_post']:
            results[a['name']][key] = parse_time(a[key])


print("Found %d/%d accounts" % (len(results), len(accounts)))
r = shelve.open("accounts.active.shelve")
r['accounts'] = results
r.close()
