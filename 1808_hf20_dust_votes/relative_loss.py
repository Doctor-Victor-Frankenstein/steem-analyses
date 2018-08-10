import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

sp = [1.2, 5, 10, 15, 50, 100, 200, 500, 1000, 5000, 10000, 50000, 100000]
TRESHOLD = 1.2
rel_loss = [(TRESHOLD * 100/s) for s in sp]

print("| SP | relative value loss in rshares |")
for i in range(len(sp)):
    print("| %d SP | %.2f %% |" % (sp[i], rel_loss[i]))

plt.figure(figsize=(12, 6))
plt.plot(sp, rel_loss)
plt.xlabel("Effective vote SP")
plt.ylabel("Relative loss of vote value (%)")
plt.title("Relative loss of vote value in rshares (HF20)")
plt.grid()
plt.xscale('log')
plt.savefig("rel_loss.png")
