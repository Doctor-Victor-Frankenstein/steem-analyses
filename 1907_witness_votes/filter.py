import shelve
import sys

s = shelve.open(sys.argv[1])
accounts = s['accounts']
s.close()

print(accounts[0])

filtered = []
for a in accounts:
    if a['vesting_shares'] == 0 or a['proxy'] != "":
        continue
    copy = ['name', 'vesting_shares', 'proxied_vsf_votes',
            'witness_votes']
    entry = {}
    for field in copy:
        entry[field] = a[field]
    filtered.append(entry)

s = shelve.open(sys.argv[2])
s['accounts'] = filtered
s.close()

print("Parsed %d accounts from %s, kept %d in %s" %
      (len(accounts), sys.argv[1], len(filtered), sys.argv[2]))
