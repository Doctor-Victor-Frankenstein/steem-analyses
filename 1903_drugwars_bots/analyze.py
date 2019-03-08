import sys
import shelve
from beem.blockchain import Blockchain
from datetime import datetime, timedelta
from collections import Counter
from beembase.signedtransactions import Signed_Transaction
from beemgraphenebase.base58 import Base58
from beemgraphenebase.account import PublicKey

def get_signer(trx):
    try:
        st = Signed_Transaction(trx.copy())
    except Exception:
        return None

    keys = []
    for key in st.verify(recover_parameter=True):
        keys.append(format(Base58(key, prefix='STM'), 'STM'))
    return keys

s = shelve.open("transactions.shelf")
transactions = s['transactions']
s.close()

DW_IDs = ['dw-heist', 'drugwars', 'dw-unit', 'dw-upgrade', 'dw-char']
KNOWN_DW_KEYS = [
    'STM8a2nxaUySYeeKPa4PTgX6AU41WNcyvp3MsG9vcrnGwQg5FUH9E', # @drugwars.app
    'STM5khoFYgEg8Mvh989JmXLhgEgwAF78nPRr2xppQgafzWCXe2krQ'  # @steemconnect
]

op_distribution = Counter()
signer_distribution = Counter()

all_ops = {}
bot_ops = {}
all_players = {}
bot_players = {}
for id in DW_IDs:
    all_players[id] = set()
    bot_players[id] = set()
    all_ops[id] = 0
    bot_ops[id] = 0

i = 0
num_trx = len(transactions)

for trx in transactions:
    sys.stdout.write("%d / %d (%.1f%%)\r" % (i, num_trx, i * 100 / num_trx))

    signer = get_signer(trx)
    signer_distribution.update([signer[0]])
    botter = (signer[0] not in KNOWN_DW_KEYS)

    for op in trx['operations']:
        if op['type'] == 'custom_json_operation' and \
           op['value']['id'] in DW_IDs:
            otype = op['value']['id']
            acc = op['value']['required_posting_auths'][0]
            all_players[otype] |= set([acc])
            all_ops[otype] += 1
            if botter:
                bot_players[otype] |= set([acc])
                bot_ops[otype] += 1
            op_distribution.update([otype])
    i += 1

print(op_distribution)
print(signer_distribution)

total_players = set()
for id in DW_IDs:
    print(id, len(all_players[id]), len(bot_players[id]))
    total_players |= all_players[id]

print("Players:", len(total_players))

s = shelve.open("results.shelf")
s['op_distribution'] = op_distribution
s['signer_distribution'] = signer_distribution
s['all_players'] = all_players
s['bot_players'] = bot_players
s['all_ops'] = all_ops
s['bot_ops'] = bot_ops
s.close()
