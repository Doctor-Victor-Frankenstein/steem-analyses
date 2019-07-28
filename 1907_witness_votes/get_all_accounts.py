#!/usr/bin/python
from beem import Steem
from beem.amount import Amount
from beem.utils import parse_time
import shelve
import sys
from prettytable import PrettyTable
from json import loads as jloads

def prepare_account(account):
    json = account.copy()
    dates = [ "last_owner_update", "last_account_update", "created",
              "last_owner_proved", "last_active_proved",
              "last_account_recovery", "last_vote_time",
              "sbd_seconds_last_update", "sbd_last_interest_payment",
              "savings_sbd_seconds_last_update",
              "savings_sbd_last_interest_payment",
              "next_vesting_withdrawal", "last_market_bandwidth_update",
              "last_post", "last_root_post", "last_bandwidth_update" ]
    for date in dates:
        if date in account:
            json[date] = parse_time(account[date])

    amounts = [ "balance", "savings_balance", "sbd_balance",
                "savings_sbd_balance", "reward_sbd_balance",
                "reward_steem_balance", "reward_vesting_balance",
                "reward_vesting_steem", "vesting_shares",
                "delegated_vesting_shares", "received_vesting_shares",
                "vesting_withdraw_rate", "vesting_balance"]
    for amount in amounts:
        if amount in account:
            json[amount] = Amount(account[amount]).amount

    if "json_metadata" in json:
        try:
            json['json_metadata'] = jloads(json['json_metadata'])
        except:
            json['json_metadata'] = {}

    return json

def get_all_accounts(s, start='', stop='', steps=1e3):
    """ Yields account names between start and stop.

            :param str start: Start at this account name
            :param str stop: Stop at this account name
            :param int steps: Obtain ``steps`` ret with a single call from RPC
    """
    if s.rpc.get_use_appbase() and start == "":
        lastname = None
    else:
        lastname = start
    s.rpc.set_next_node_on_empty_reply(False)
    while True:
        account_names = s.rpc.lookup_accounts(lastname, steps)
        if lastname == account_names[-1]:
            raise StopIteration
        if account_names[0] == lastname:
            account_names = account_names[1:]
        lastname = account_names[-1]
        yield s.rpc.get_accounts(account_names)


accounts = []

s = Steem(node="https://api.steemit.com")
for accs in get_all_accounts(s):
    for account in accs:
        accounts.append(prepare_account(account))
    sys.stdout.write("%16s\r" % (accs[-1]['name']))


sh = shelve.open("all_accounts.shelf")
sh['accounts'] = accounts
sh.close()
