#!/usr/bin/python
import pyodbc
import shelve
import config
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

month = int(sys.argv[1])
start_day = int(sys.argv[2])
days = int(sys.argv[3])

start_date = datetime(2018, month, start_day)
while start_date < datetime(2018, month, start_day) + timedelta(days=days):
    stop_date = start_date + timedelta(days=1)
    fields = ['created', 'author', 'active_votes', 'depth']
    query = "SELECT %s from Comments WHERE " \
             "created BETWEEN '%s' AND '%s'" % \
            (", ".join(fields), start_date, stop_date)

    entries = []
    cursor.execute(query)
    for op in cursor:
        entry = {}
        for key, value in zip(fields, op):
            if key in ['active_votes']:
                if not value:
                    entry[key] = {}
                else:
                    entry[key] = json.loads(value)
            else:
                entry[key] = value
        entries.append(entry)

    s = shelve.open("posts-%s.shelf" % (datestr(start_date)))
    s['posts'] = entries
    s.close()
    print(start_date, len(entries))
    start_date = stop_date

connection.close()
