#!/usr/bin/python
import pyodbc
import shelve
import config
import json
from datetime import datetime, timedelta
import sys

connection = pyodbc.connect(driver=config.driver,
                            server=config.server,
                            database=config.database,
                            uid=config.uid, pwd=config.pwd)
cursor = connection.cursor()

fields = ['name', 'created', 'recovery_account', 'post_count',
          'voting_manabar_current_mana',
          'voting_manabar_last_update_time', 'voting_power',
          'last_vote_time', 'balance', 'savings_balance',
          'sbd_balance', 'savings_sbd_balance', 'reward_sbd_balance',
          'reward_steem_balance', 'reward_vesting_balance',
          'reward_vesting_steem', 'vesting_shares',
          'delegated_vesting_shares', 'received_vesting_shares',
          'vesting_withdraw_rate', 'next_vesting_withdrawal',
          'withdrawn', 'to_withdraw', 'withdraw_routes',
          'curation_rewards', 'posting_rewards', 'proxied_vsf_votes',
          'witnesses_voted_for', 'last_post', 'last_root_post',
          'pending_claimed_accounts', 'vesting_balance', 'reputation',
          'witness_votes']

query = "SELECT %s from Accounts ORDER BY name" % (", ".join(fields))

accounts = []
cursor.execute(query)
for op in cursor:
    entry = {}
    for key, value in zip(fields, op):
        if key in ['posting', 'active', 'owner', 'witness_votes',
                   'json_metadata']:
            if not value:
                entry[key] = {}
            else:
                entry[key] = json.loads(value)
        else:
            entry[key] = value
    accounts.append(entry)

connection.close()

s = shelve.open("accounts.shelf")
s['accounts'] = accounts
s.close()
