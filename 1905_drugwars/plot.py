import os
from datetime import datetime
import shelve
import json
from prettytable import PrettyTable
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def get_file_date(filename):
    base = os.path.splitext(filename)[0]
    arr = base.split("_")
    if len(arr) != 2:
        return None
    if arr[0] != "results":
        return None
    return datetime.strptime(arr[1], "%Y%m%d")

data = {}
for root, dirs, files in os.walk("."):
    for file in files:
        date = get_file_date(file)
        if date is None:
            continue
        s = shelve.open(file)
        data[date] = {}
        for key in ['op_distribution', 'signer_distribution',
                    'all_players', 'bot_players', 'all_ops',
                    'bot_ops']:
            data[date][key] = s[key]
        s.close()

        if date < datetime(2019, 4, 1):
            for op in ['dw-heist', 'dw-unit', 'dw-upgrade', 'dw-char']:
                for key in ['all_players', 'bot_players']:
                    data[date][key]['drugwars'] |= set(data[date][key][op])
                for key in ['all_ops', 'bot_ops']:
                    data[date][key]['drugwars'] += data[date][key][op]

        data[date]['total_players'] = set()
        for id in data[date]['all_players']:
            data[date]['total_players'] |= set(data[date]['all_players'][id])
        data[date]['total_players'] = len(data[date]['total_players'])
        for key in ['all_players', 'bot_players']:
            for op in data[date][key]:
                data[date][key][op] = len(data[date][key][op])
        # print(data[date])

t = PrettyTable(['date', 'all_players', 'bot_players', 'all_ops',
                 'bot_ops'])

dates = sorted(data.keys())
all_players = []
bot_players = []
all_ops = []
bot_ops = []
for date in dates:
    t.add_row([date, data[date]['all_players']['drugwars'],
               data[date]['bot_players']['drugwars'],
               data[date]['all_ops']['drugwars'],
               data[date]['bot_ops']['drugwars']])
    all_players.append(data[date]['all_players']['drugwars'])
    bot_players.append(data[date]['bot_players']['drugwars'])
    all_ops.append(data[date]['all_ops']['drugwars'])
    bot_ops.append(data[date]['bot_ops']['drugwars'])

print(t)

linestyle = {'linestyle': '-', 'marker':'.'}
plt.figure(figsize=(12, 6))
plt.grid()
plt.plot_date(dates, all_players, label="All players", **linestyle)
plt.plot_date(dates, bot_players, label="players with scripted ops", **linestyle)
plt.legend()
plt.title("Number of players")
plt.ylabel("Number of drugwars players")
plt.xlabel("Date")
plt.legend()
plt.gcf().autofmt_xdate(rotation=30)
plt.savefig("players.png")

plt.figure(figsize=(12, 6))
plt.grid()
plt.plot_date(dates, all_ops, label="All ops", **linestyle)
plt.plot_date(dates, bot_ops, label="scripted ops", **linestyle)
plt.legend()
plt.title("Number of drugwars operations on the chain")
plt.ylabel("Number of ops")
plt.xlabel("Date")
plt.legend()
plt.gcf().autofmt_xdate(rotation=30)
plt.savefig("ops.png")
