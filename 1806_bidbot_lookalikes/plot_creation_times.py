import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter
import shelve
import sys
from beem.utils import addTzInfo
from datetime import datetime

dateFmt = DateFormatter('%Y-%m-%d')
start = addTzInfo(datetime(2018, 6, 10))
stop = addTzInfo(datetime(2018, 6, 12))

s = shelve.open("accounts.active.shelve")
accounts = s['accounts']
s.close()

alike_names = []
creation_dates = []

with open("alike_names.txt") as f:
    for line in f.readlines():
        name = line[:-1]
        creation_dates.append(date2num(accounts[name]['created']))
        sys.stdout.write("%s\r" % (name))
        if start <= accounts[name]['created'] <= stop:
            alike_names.append(name)

print("\n", len(alike_names), len(creation_dates))
print(alike_names)

# Full scale
plt.figure(figsize=(12, 6))
plt.hist(creation_dates, bins=100)
plt.grid()
plt.gca().xaxis.set_major_formatter(dateFmt)
plt.title("Account creation date of look-alike accounts")
plt.xlabel("Account creation date")
plt.ylabel("Number of accounts")
plt.savefig("look-alike_account_creation_dates.png")

# Zoomed
zoomrange = [date2num(datetime(2018, 6, 5)), date2num(datetime(2018, 6, 15))]
plt.figure(figsize=(12, 6))
plt.hist(creation_dates, bins=100, range=zoomrange)
plt.grid()
plt.gca().xaxis.set_major_formatter(dateFmt)
plt.title("Account creation date of look-alike accounts")
plt.xlabel("Account creation date")
plt.ylabel("Number of accounts")
plt.savefig("look-alike_account_creation_dates_zoomed.png")

with open("alike_names_zoomed.txt", "w") as f:
    f.write("\n".join(alike_names))
    f.write("\n")
