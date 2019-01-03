from beem.account import Account
import shelve

a = Account("stmdev")
ops = []
for op in a.history(only_ops=['account_update']):
    ops.append(op)

print(len(ops))
s = shelve.open("ops.shelf")
s['ops'] = ops
s.close()
