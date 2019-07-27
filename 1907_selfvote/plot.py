import shelve
import sys
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt


total_rshares = {}
total_exl_rshares = {}
sv_rshares = {}
dapp_rshares = {}
top1_rshares = {}
top3_rshares = {}
top5_rshares = {}
top10_rshares = {}
bot_rshares = {}
dapp_rshares = {}
voters = {}
authors = {}

for fname in sys.argv[1:]:
    s = shelve.open(fname)
    data = s['data']
    s.close()

    date = data['maxdate']
    total_rshares[date] = data['total_rshares'] #- data['bot_rshares'] - data['dapp_rshares']
    total_exl_rshares[date] = data['total_rshares'] - data['bot_rshares'] - data['dapp_rshares']
    sv_rshares[date] = data['sv_rshares']
    bot_rshares[date] = data['bot_rshares']
    dapp_rshares[date] = data['dapp_rshares']
    dapp_rshares[date] = data['dapp_rshares']
    top1_rshares[date] = data['top1_rshares']
    top3_rshares[date] = data['top3_rshares']
    top5_rshares[date] = data['top5_rshares']
    top10_rshares[date] = data['top10_rshares']
    for date in sorted(data['voters'])[:7]:
        voters[date] = data['voters'][date]
    for date in sorted(data['authors'])[:7]:
        authors[date] = data['authors'][date]

def dict_to_xy(d):
    x = sorted(d.keys())[:-1]
    y = [d[k] for k in x]
    return x, y

def dict_to_rel_xy(d, t):
    x = sorted(d.keys())[:-1]
    y = [d[k]*100/t[k] for k in x]
    return x, y

plt.figure(figsize=(12, 6))
xrange, yrange = dict_to_xy(total_rshares)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="Total rshares")
xrange, yrange = dict_to_xy(bot_rshares)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="bot rshares")
xrange, yrange = dict_to_xy(dapp_rshares)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="dapp rshares")
# xrange, yrange = dict_to_xy(total_exl_rshares)
# plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="Total rshares excl. bots and dapps")
plt.grid()
plt.legend()
plt.xlabel("Date")
plt.ylabel("rshares")
plt.title("Vote value as accumulated weekly rshares")
plt.savefig("total_rshares.png")

plt.figure(figsize=(12, 6))
xrange, yrange = dict_to_xy(total_rshares)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="Total rshares")
xrange, yrange = dict_to_xy(total_exl_rshares)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="Total rshares excl. bots and dapps")
xrange, yrange = dict_to_xy(sv_rshares)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="Selfvote rshares")
xrange, yrange = dict_to_xy(top3_rshares)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="80% of rshares to up to 3 authors")
xrange, yrange = dict_to_xy(top5_rshares)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="80% of rshares to up to 5 authors")
xrange, yrange = dict_to_xy(top10_rshares)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="80% of rshares to up to 10 authors")
plt.grid()
plt.legend()
plt.xlabel("Date")
plt.ylabel("rshares")
plt.title("Vote value as accumulated weekly rshares")
plt.savefig("total_rshares2.png")

plt.figure(figsize=(12, 6))
rel = total_exl_rshares  # total_rshares
xrange, yrange = dict_to_rel_xy(sv_rshares, rel)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="Selfvote rshares")
xrange, yrange = dict_to_rel_xy(top3_rshares, rel)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="80% of rshares to up to 3 authors")
xrange, yrange = dict_to_rel_xy(top5_rshares, rel)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="80% of rshares to up to 5 authors")
xrange, yrange = dict_to_rel_xy(top10_rshares, rel)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="80% of rshares to up to 10 authors")
plt.grid()
plt.legend()
plt.xlabel("Date")
plt.ylabel("Relative share (%)")
plt.title("Relative share of low-diversity votes wrt. to all votes")
plt.gca().set_ylim([0, max(yrange)*1.2])
plt.savefig("total_rshares2_rel.png")


plt.figure(figsize=(12, 6))
xrange, yrange = dict_to_xy(voters)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="number of voters per day")
xrange, yrange = dict_to_xy(authors)
plt.plot_date(xrange, yrange, linestyle="-", marker=".", label="number of authors per day")
plt.grid()
plt.xlabel("Date")
plt.ylabel("Number of voters or authors")
plt.legend()
plt.savefig("voters.png")
