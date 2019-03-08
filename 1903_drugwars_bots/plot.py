import shelve
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

s = shelve.open("results.shelf")
op_distribution = s['op_distribution']  # Counter
signer_distribution = s['signer_distribution']  # Counter
all_players = s['all_players']  # dict of sets
bot_players = s['bot_players']  # dict of sets
all_ops = s['all_ops']
bot_ops = s['bot_ops']
s.close()

total_players = set()
for id in all_players:
    total_players |= all_players[id]
    print("players", id, len(all_players[id]), len(bot_players[id]))
    print("ops", id, all_ops[id], bot_ops[id])

print(bot_players['drugwars'])

labels = all_players.keys()
all_ps = [len(all_players[k]) for k in labels]
bot_ps = [len(bot_players[k]) for k in labels]
plt.figure(figsize=(12, 6))
plt.grid()
plt.bar(labels, all_ps, label="All players")
plt.bar(labels, bot_ps, label="players with scripted ops")
plt.legend()
plt.title("Number of players with scripted operations")
plt.ylabel("Number of players")
plt.savefig("players.png")

labels = all_players.keys()
allo = [all_ops[k] for k in labels]
boto = [bot_ops[k] for k in labels]
plt.figure(figsize=(12, 6))
plt.grid()
plt.bar(labels, allo, label="All game operations")
plt.bar(labels, boto, label="scripted operations")
plt.legend()
plt.title("Number of scripted operations")
plt.ylabel("Number of operations")
plt.savefig("ops.png")

print("Sum of ops:", sum(allo))
print("Players:", len(total_players))
