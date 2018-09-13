#!/usr/bin/python
import pyodbc
import shelve
import config
import json
from datetime import datetime, timedelta
import sys
from beem.utils import reputation_to_score

def datestr(date):
    return "%04d-%02d-%02d" % (date.year, date.month, date.day)

connection = pyodbc.connect(driver=config.driver,
                              server=config.server,
                              database=config.database,
                              uid=config.uid, pwd=config.pwd)
cursor = connection.cursor()

start_date = datetime(2018, 7, 1)
while start_date < datetime(2018, 9, 1):
    stop_date = start_date + timedelta(days=1)

    fields = ['created', 'author', 'permlink', 'active_votes',
              'author_reputation', 'total_payout_value',
              'curator_payout_value', 'author_rewards',
              'max_accepted_payout', 'percent_steem_dollars',
              'allow_votes', 'allow_curation_rewards',
              'allow_curation_rewards', 'beneficiaries', 'promoted',
              'depth']
    query = "SELECT %s from Comments WHERE " \
             "created BETWEEN '%s' AND '%s'" % \
            (", ".join(fields), start_date, stop_date)

    entries = []
    cursor.execute(query)
    for op in cursor:
        entry = {}
        for key, value in zip(fields, op):
            if key in ['active_votes', 'beneficiaries']:
                if not value:
                    entry[key] = {}
                else:
                    entry[key] = json.loads(value)
            elif key == 'author_reputation':
                entry[key] = reputation_to_score(int(value))
            else:
                entry[key] = value
        entries.append(entry)

    s = shelve.open("posts-%s.shelf" % (datestr(start_date)))
    s['posts'] = entries
    s.close()
    print(start_date, len(entries))
    start_date = stop_date

connection.close()
