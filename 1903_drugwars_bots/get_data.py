import sys
import shelve
from beem.blockchain import Blockchain
from datetime import datetime, timedelta

start_date = datetime(2019, 3, 5)
stop_date = start_date + timedelta(days=1)
DW_IDs = ['dw-heist', 'drugwars', 'dw-unit', 'dw-upgrade', 'dw-char']

b = Blockchain()
start_block = b.get_estimated_block_num(start_date)
stop_block = b.get_estimated_block_num(stop_date)

transactions = []
for blk in b.blocks(start=start_block, stop=stop_block,
                    max_batch_size=50):
    sys.stdout.write("%s\r" % (blk['timestamp']))
    for trx in blk.transactions:
        keep = False
        for op in trx['operations']:
            if op['type'] == 'custom_json_operation' and \
               op['value']['id'] in DW_IDs:
                keep = True
        if keep:
            transactions.append(trx)

s = shelve.open("transactions.shelf")
s['transactions'] = transactions
s.close()
