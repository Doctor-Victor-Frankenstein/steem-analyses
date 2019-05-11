import sys
import shelve
from beem import Steem
from beem.blockchain import Blockchain
from datetime import datetime, timedelta

year = 2019
month = int(sys.argv[1])
day = int(sys.argv[2])

start_date = datetime(year, month, day)
stop_date = start_date + timedelta(days=1)
DW_IDs = ['dw-heist', 'drugwars', 'dw-unit', 'dw-upgrade', 'dw-char']

stm = None  #Steem(node=['https://api.steemit.com'])
b = Blockchain(steem_instance=stm)
start_block = b.get_estimated_block_num(start_date)
stop_block = b.get_estimated_block_num(stop_date)

transactions = []
for blk in b.blocks(start=start_block, stop=stop_block,
                    threading=True):
                    # max_batch_size=50):
    sys.stdout.write("%s\r" % (blk['timestamp']))
    for trx in blk.transactions:
        keep = False
        for op in trx['operations']:
            if op['type'] == 'custom_json_operation' and \
               op['value']['id'] in DW_IDs:
                keep = True
        if keep:
            transactions.append(trx)

s = shelve.open("transactions_%04d%02d%02d.shelf" % (year, month, day))
s['transactions'] = transactions
s.close()
