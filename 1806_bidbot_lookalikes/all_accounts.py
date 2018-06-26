#!/usr/bin/python
from beem.blockchain import Blockchain
import shelve
import sys

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
        # print(account_names)
        if lastname == account_names[-1]:
            raise StopIteration
        if account_names[0] == lastname:
            account_names = account_names[1:]
        lastname = account_names[-1]
        yield s.rpc.get_accounts(account_names)

keys = ['created', 'name', 'reputation', 'post_count',
        'last_vote_time', 'balance', 'savings_balance', 'sbd_balance',
        'vesting_shares', 'delegated_vesting_shares',
        'received_vesting_shares', 'last_bandwidth_update',
        'last_post', 'last_root_post', 'reputation']

accounts = []
b = Blockchain()
for accs in get_all_accounts(b.steem):
    for account in accs:
        for k in list(account.keys()):
            if k not in keys:
                del account[k]
        # print(account)
        accounts.append(account)
    sys.stdout.write("\r%16s" % (accs[-1]['name']))

sh = shelve.open("accounts.shelve")
sh['accounts'] = accounts
sh.close()
