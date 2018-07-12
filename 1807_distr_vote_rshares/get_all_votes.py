#!/usr/bin/python
import pyodbc
import shelve
import sys
import config
from datetime import datetime, timedelta
import json
from beem.utils import parse_time

connection = pyodbc.connect(driver=config.driver,
                              server=config.server,
                              database=config.database,
                              uid=config.uid, pwd=config.pwd)
cursor = connection.cursor()

start_date = datetime(2018, 4, 1)
stop_date = datetime(2018, 7, 1)

fields = ['active_votes', 'created', 'total_payout_value',
          'curator_payout_value', 'author', 'permlink', 'depth',
          'author_reputation', 'beneficiaries']

while stop_date > start_date:

    qstart = start_date
    qstop = qstart + timedelta(days=1)
    query = "SELECT %s FROM Comments WHERE " \
            "created BETWEEN '%04d-%02d-%02d' AND '%04d-%02d-%02d'" % \
            (", ".join(fields), qstart.year, qstart.month,
             qstart.day, qstop.year, qstop.month, qstop.day)
    #query = "SELECT TOP 10 %s FROM Comments" % \
    #        (", ".join(fields))
    print(query)
    cursor.execute(query)

    ops = []
    for op in cursor:
        entry = {}
        # print(op)
        for field, value in zip(fields, op):
            if field == "active_votes":
                value = json.loads(value)
                # print(len(value))
                for vote in range(len(value)):
                    value[vote]['rshares'] = int(value[vote]['rshares'])
                    value[vote]['weight'] = int(value[vote]['weight'])
                    value[vote]['percent'] = int(value[vote]['percent'])
                    value[vote]['time'] = parse_time(value[vote]['time'])
                    value[vote]['reputation'] = int(value[vote]['reputation'])

            entry[field] = value
        ops.append(entry)
        sys.stdout.write("%s\r" % (entry['created']))
        # print(entry)

    s = shelve.open("posts-%d%02d%02d.shelf" % (qstart.year,
                                                qstart.month,
                                                qstart.day))
    s['posts'] = ops
    s.close()

    print(start_date, len(ops))

    start_date = qstop
