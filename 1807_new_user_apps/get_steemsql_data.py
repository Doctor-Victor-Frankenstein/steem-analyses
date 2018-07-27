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

start_date = datetime(2018, 3, 1)
while start_date < datetime(2018, 7, 26):
    stop_date = start_date + timedelta(days=1)
    comment_stop_date = start_date + timedelta(days=30)

    fields = ['a.name', 'a.created', 'a.recovery_account', 'a.post_count',
              'c.created', 'c.permlink', 'c.json_metadata']
    query = "SELECT %s from Comments as c INNER JOIN Accounts as a ON " \
            "c.author = a.name WHERE " \
            "a.created BETWEEN '%s' AND '%s' AND c.depth = 0 AND " \
            "c.created < '%s'" % \
            (", ".join(fields), start_date, stop_date, comment_stop_date)

    entries = []
    cursor.execute(query)
    for op in cursor:
        entry = {}
        for key, value in zip(fields, op):
            if 'json_metadata' in key:
                if not value:
                    entry[key] = {}
                else:
                    entry[key] = json.loads(value)
            else:
                entry[key] = value
        entries.append(entry)

    s = shelve.open("entries-%s.shelf" % (datestr(start_date)))
    s['entries'] = entries
    s.close()
    print(start_date, len(entries))
    start_date = stop_date

connection.close()
