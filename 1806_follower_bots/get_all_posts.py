#!/usr/bin/python
import pyodbc
import shelve
import config
import json
from datetime import datetime

year = 2018
month = 5

connection = pyodbc.connect(driver=config.driver,
                              server=config.server,
                              database=config.database,
                              uid=config.uid, pwd=config.pwd)
cursor = connection.cursor()


for day in range(1, 32):
    date = "%04d%02d%02d" % (year, month, day)
    print("%s: Querying %s" % (datetime.now(), date))

    # get all posts
    query = "SELECT created, author FROM Comments WHERE " \
            "DEPTH = 0 AND CONVERT(date, created) = '%s';" % (date)
    cursor.execute(query)

    posts = []
    authors = set()
    for op in cursor:
        entry = {'created': op[0], 'author': op[1]}
        authors |= set([op[1]])
        posts.append(entry)

    print(date, "Posts: ", len(posts))

    # get all follow ops
    # query = "SELECT timestamp, " \
    #         "JSON_VALUE([json_metadata], '$[1].follower'), " \
    #         "JSON_VALUE([json_metadata], '$[1].following')" \
    #         "FROM TxCustoms WHERE " \
    #         "JSON_VALUE([json_metadata], '$[0]') = 'follow' AND " \
    #         "JSON_VALUE([json_metadata], '$[1].what[0]') = 'blog' AND " \
    #         "CONVERT(date, timestamp) = '%s';" % (date)
    query = "SELECT timestamp, json_metadata FROM TxCustoms WHERE " \
           "json_metadata LIKE '%%\"blog\"%%' AND " \
           "CONVERT(date, timestamp) = '%s';" % (date)
    cursor.execute(query)


    follows = []
    for op in cursor:
        ts = op[0]
        try:
            js = json.loads(op[1])
        except:
            continue
        if len(js) != 2:
            continue
        if js[0] != 'follow':
            continue
        if 'what' not in js[1]:
            continue
        if "blog" not in js[1]['what']:
            continue
        try:
            follower = js[1]['follower']  # op[1]
            following = js[1]['following']  # op[2]
        except:
            #print(op)
            continue
        # follower = op[1]
        # following = op[2]
        if following not in authors:
            continue
        entry = {'timestamp':ts, 'follower': follower, 'following': following}
        follows.append(entry)

    print(date, "Follows: ", len(follows))

    s = shelve.open("posts-%s.shelf" % (date))
    s['posts'] = posts
    s['follows'] = follows
    s.close()

connection.close()
