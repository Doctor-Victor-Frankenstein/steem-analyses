#!/usr/bin/python
import pyodbc
import shelve

import config
# create a file config.py with
# driver = '{ODBC Driver 17 for SQL Server}'
# server = 'vip.steemsql.com,1433'
# database = 'DBSteem'
# uid = "yoursteemsqlusername"
# pwd = "yoursteemsqlpassword"

import json
from datetime import datetime, timedelta
import sys

def datestr(date):
    return "%04d-%02d-%02d" % (date.year, date.month, date.day)

connection = pyodbc.connect(driver=config.driver,
                            server=config.server,
                            database=config.database,
                            uid=config.uid, pwd=config.pwd)
cursor = connection.cursor()

year = int(sys.argv[1])
month = int(sys.argv[2])
if len(sys.argv) == 4:
    start_day = int(sys.argv[3])
else:
    start_day = 1

start_date = datetime(year, month, start_day)
while start_date.month == month:
    stop_date = start_date + timedelta(days=1)

    fields = ['created', 'last_update', 'author', 'permlink',
              'active_votes', 'author_reputation',
              'total_payout_value', 'curator_payout_value',
              'author_rewards', 'max_accepted_payout',
              'percent_steem_dollars', 'allow_votes',
              'allow_curation_rewards', 'beneficiaries', 'promoted',
              'depth', 'json_metadata', 'children']

    query = "SELECT %s from Comments WHERE " \
             "created BETWEEN '%s' AND '%s'" % \
            (", ".join(fields), start_date, stop_date)

    entries = []
    cursor.execute(query)
    for op in cursor:
        entry = {}
        for key, value in zip(fields, op):
            if key in ['active_votes', 'beneficiaries',
                       'json_metadata']:
                if not value:
                    entry[key] = {}
                else:
                    try:
                        entry[key] = json.loads(value)
                    except:
                        print("Failed to parse", value)
                        entry[key] = {}
            else:
                entry[key] = value
        entries.append(entry)

    s = shelve.open("posts-%s.shelf" % (datestr(start_date)))
    s['posts'] = entries
    s.close()
    print(start_date, len(entries))
    start_date = stop_date

connection.close()
