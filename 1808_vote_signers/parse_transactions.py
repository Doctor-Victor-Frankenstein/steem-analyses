from mongostorage import MongoStorage
from signers import get_signer
import sys
from pymongo.errors import BulkWriteError

m = MongoStorage(db_name="steem", host='172.18.0.3', port=27017, user='',
                 passwd='')

m.ensure_indexes()
latest_vote = m.Votes.find_one(sort=[('block_num', -1)])
latest_block = 0
if latest_vote:
    latest_block = latest_vote['block_num']
max = m.Transactions.count({'block_num': {"$gte": latest_block}})
print("Starting from block %d, %d transactions remaining" %
      (latest_block, max))

permlinks = set()
idx = 0
limit = 1000

for trx in m.Transactions.find({'block_num': {"$gte": latest_block}},
                               sort=[('block_num', 1)]):
    sys.stdout.write("%d/%d (%.2f%%)\r" % (idx, max, idx*100/max))
    idx += 1
    signer = get_signer(trx)
    votes = []
    for op in trx['operations']:
        if op['type'] != 'vote_operation':
            continue
        if op['value']['weight'] == 0:
            # skip unvotes
            continue
        vote = {
            'author': op['value']['author'],
            'permlink': op['value']['permlink'],
            'voter': op['value']['voter'],
            'percent': int(op['value']['weight']),
            'block_num': trx['block_num'],
            'transaction_num': trx['transaction_num'],
            'signer': signer,
        }
        votes.append(vote)
    if len(votes):
        try:
            m.Votes.insert_many(votes)
        except BulkWriteError:
            continue
