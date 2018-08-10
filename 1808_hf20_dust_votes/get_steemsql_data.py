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

start_date = datetime(2018, 7, 23)
while start_date < datetime(2018, 8, 9):
    stop_date = start_date + timedelta(days=1)
    comment_stop_date = start_date + timedelta(days=30)

    fields = ['created', 'author', 'permlink', 'active_votes']
    query = "SELECT %s from Comments WHERE " \
             "created BETWEEN '%s' AND '%s' AND LEN(active_votes) > 3" % \
            (", ".join(fields), start_date, stop_date)

    entries = []
    cursor.execute(query)
    for op in cursor:
        entry = {}
        for key, value in zip(fields, op):
            if 'active_votes' in key:
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
