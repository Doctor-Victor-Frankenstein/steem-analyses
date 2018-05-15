from datetime import datetime
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

number_of_bots = {
    datetime(2017, 11, 1): 28,
    datetime(2017, 12, 1): 50,
    datetime(2018, 1, 1): 63,
    datetime(2018, 2, 1): 105,
    datetime(2018, 3, 1): 125,
    datetime(2018, 4, 1): 146,
    datetime(2018, 4, 15): 163,
    datetime(2018, 5, 1): 163,
    datetime(2018, 5, 2): 169,
    datetime(2018, 5, 4): 172,
    datetime(2018, 5, 6): 162,
    datetime(2018, 5, 8): 165,
    datetime(2018, 5, 10): 165,
    datetime(2018, 5, 12): 161,
    datetime(2018, 5, 14): 153,
    }

plt.figure(figsize=(12, 6))
vals = [number_of_bots[k] for k in number_of_bots]
dates = number_of_bots.keys()
plt.plot_date(dates, vals, linestyle="-", marker="*")
plt.xlabel("Date")
plt.ylim([0, max(vals) * 1.2])
plt.ylabel("Number of active bots")
plt.title("Number of active paid voting bots over time")
plt.tight_layout()
plt.grid()
plt.savefig("bots_over_time.png")
