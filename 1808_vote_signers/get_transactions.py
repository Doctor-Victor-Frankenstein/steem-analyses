import sys
from datetime import datetime, timedelta
from beem import Steem
from beem.blockchain import Blockchain
from beem.utils import parse_time
from beem.nodelist import NodeList
from mongostorage import MongoStorage

BATCH_SIZE = 100

if len(sys.argv) != 4:
    print("ERROR: Command line argument count mismatch")
    print("Usage: %s [year] [month] [day]" % (sys.argv[0]))
    exit(-1)

year = int(sys.argv[1])
month = int(sys.argv[2])
day = int(sys.argv[3])

nl = NodeList()
s = Steem(node=nl.get_nodes(appbase=True, normal=False))
b = Blockchain(steem_instance=s)

start_date = datetime(year, month, day)
end_date = start_date + timedelta(days=1)
start_block = b.get_estimated_block_num(start_date)
end_block = b.get_estimated_block_num(end_date) - 1

m = MongoStorage(db_name="steem", host='172.18.0.3', port=27017, user='',
                 passwd='')
m.ensure_indexes()

for block in b.blocks(start=start_block, stop=end_block,
                      max_batch_size=BATCH_SIZE):

    sys.stdout.write("%s - %s - %s\r" % (start_block, block.block_num,
                                         end_block))
    for trx in block.transactions:
        if "'vote_operation'" not in str(trx):
            continue
        m.Transactions.insert(trx)
