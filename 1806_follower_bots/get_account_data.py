#!/usr/bin/python
from beem.account import Account
from beem.utils import formatTimeString
from beem.amount import Amount
import sys
import shelve
import json
from datetime import datetime


def acc_to_dict(account):
    output = account.copy()
    if 'json_metadata' in output:
        output["json_metadata"] = json.dumps(output["json_metadata"], separators=[',', ':'])
    parse_times = [
            "last_owner_update", "last_account_update", "created", "last_owner_proved", "last_active_proved",
            "last_account_recovery", "last_vote_time", "sbd_seconds_last_update", "sbd_last_interest_payment",
            "savings_sbd_seconds_last_update", "savings_sbd_last_interest_payment", "next_vesting_withdrawal",
            "last_market_bandwidth_update", "last_post", "last_root_post", "last_bandwidth_update"
        ]
    for p in parse_times:
        if p in output:
            date = output.get(p, datetime(1970, 1, 1, 0, 0))
            if isinstance(date, (datetime, date)):
                output[p] = formatTimeString(date)
            else:
                output[p] = date
    amounts = [ "balance", "savings_balance", "sbd_balance",
                "savings_sbd_balance", "reward_sbd_balance",
                "reward_steem_balance", "reward_vesting_balance",
                "reward_vesting_steem", "vesting_shares",
                "delegated_vesting_shares", "received_vesting_shares" ]
    for p in amounts:
        if p in output and isinstance(output[p], Amount):
            output[p] = output[p].json()
    return json.loads(str(json.dumps(output)))

accountnames = []
with open("follower-bots.txt") as f:
    for line in f.readlines():
        name = line[:-1]  # strip newline
        accountnames.append(name)

acclist = []
for name in accountnames:
    a = Account(name)
    acc = acc_to_dict(a)
    acc['reputation'] = a.get_reputation()
    acc['steem_power'] = a.get_steem_power()
    acc['own_steem_power'] = a.get_steem_power(onlyOwnSP=True)
    op = list(a.history(0, 1, use_block_num=False))[0]
    if op['type'] in ['account_create',
                      'account_create_with_delegation']:
        acc['creator'] = op['creator']
    else:
        print("WARN: unexpected first op for %s:\n%s" %
              (a['name'], op))
        acc['creator'] = "unknown"

    acclist.append(acc)
    sys.stdout.write("\r%d/%d" % (accountnames.index(name),
                                  len(accountnames)))

s = shelve.open("accounts.shelf")
s['accounts'] = acclist
s.close()
