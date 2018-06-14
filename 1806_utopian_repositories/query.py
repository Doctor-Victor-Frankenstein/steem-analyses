#!/usr/bin/python

import pyodbc
import shelve
import sys
import config

connection = pyodbc.connect(driver=config.driver,
                              server=config.server,
                              database=config.database,
                              uid=config.uid, pwd=config.pwd)
cursor = connection.cursor()
keys = ['created', 'json_metadata', 'active_votes']
keylist = ", ".join(keys)
for month in range(3, 6):

    query = "SELECT %s FROM Comments " \
            "INNER JOIN TxVotes ON " \
            "Comments.author = TxVotes.author AND " \
            "Comments.permlink = TxVotes.permlink WHERE " \
            "TxVotes.voter = 'utopian-io' AND " \
            "Comments.depth = 0 AND " \
            "YEAR(Comments.created) = 2018 AND " \
            "MONTH(Comments.created) = %d" % (keylist, month)

    posts = []
    cursor.execute(query)
    for op in cursor:
        entry = {}
        for k, v in zip(keys, op):
            entry[k] = v
        posts.append(entry)

    s = shelve.open('utopian-posts-%02d.shelf' % (month))
    s['posts'] = posts
    s.close()
    print(month, len(posts))

connection.close()
