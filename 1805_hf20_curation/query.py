#!/usr/bin/python

import pyodbc
import shelve
import sys
import config
import json

year = 2018
month = 4
days = range(1, 27)

connection = pyodbc.connect(driver=config.driver,
                            server=config.server,
                            database=config.database,
                            uid=config.uid, pwd=config.pwd)
cursor = connection.cursor()

fields = ['active_votes', 'created', 'total_payout_value',
          'curator_payout_value', 'author_rewards']
#fields = ['author', 'permlink', 'total_payout_value', 'active_votes']

for day in days:
    fieldquery = ", ".join(fields)
    query = "SELECT %s FROM Comments (NOLOCK) WHERE " \
            "depth = 0 AND max_accepted_payout > 0 AND " \
            "total_payout_value > 0 AND " \
            "allow_curation_rewards = 1 AND " \
            "DATALENGTH(active_votes) > 2 AND " \
            "DATALENGTH(beneficiaries) < 3 AND " \
            "YEAR(created) = %s AND Month(created) = %s AND " \
            "DAY(created) = %s" % (fieldquery, year, month, day)
    #print(query)
    cursor.execute(query)

    ops = []
    for op in cursor:
        entry = {}
        for field, value in zip(fields, op):
            if field == "active_votes":
                value = json.loads(value)
            entry[field] = value
        #print(entry)
        ops.append(entry)

    s = shelve.open("posts-%d%02d%02d.shelf" % (year, month, day))
    s['posts'] = ops
    s.close()
    print(day, len(ops))

connection.close()
