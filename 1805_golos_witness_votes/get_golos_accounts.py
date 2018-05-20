from piston import Steem
from piston.blockchain import Blockchain
import shelve

s = Steem(node='wss://ws.golos.io')
b = Blockchain(s)


def get_all_accounts(start='', stop='', steps=1e3):
    lastname = start
    accounts = []
    while True:
        print(lastname, len(accounts))
        names = s.rpc.lookup_accounts(lastname, steps, api='database_api')
        accs = s.rpc.get_accounts(names, api='database_api')
        accounts.extend(accs)
        for name in names:
            if name == stop:
                break
        lastname = names[-1]
        if len(names) < steps:
            break
    return accounts

accounts = get_all_accounts()
sh = shelve.open("accounts.shelf")
sh['accounts'] = accounts
sh.close()
