import shelve
import sys
import json
from datetime import datetime, timedelta
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


def get_weeknum(date):
    return date.isocalendar()[1]

def get_tags(entry):
    if type(entry['c.json_metadata']) != dict:
        return []
    if 'tags' not in entry['c.json_metadata']:
        return []
    tags = entry['c.json_metadata']['tags']
    return tags

def get_app(entry):
    tags = get_tags(entry)
    if not tags:
        return None
    if tags[0] == 'utopian-io':
        return tags[0]
    app = entry['c.json_metadata'].get('app', None)
    if not app:
        return None
    if type(app) == dict and 'name' in app:
        app = app['name']

    app = app.split('/')[0]
    if app == "ntopaz":
        app = "artisteem"
    return app

apps = {}
apps_per_week = {}
apps_per_user = {}
appusers = {}
weekly_data = {}

known_apps = ['steempeak', 'partiko', 'actifit', 'utopian-io',
              'dtube', 'zappl', 'steemkr', 'steemeasy', 'artisteem',
              'parley', 'tasteem', 'steemauto', 'dlive', 'steepshot',
              'dsound', 'steemhunt', 'esteem', 'steemgig',
              'bescouted', 'busy', 'dlike', 'ios-steemitapp', 'hede',
              'steem-plus-app', 'steemit', 'ulogs', 'dmania',
              'bsteem', 'steempress']

date = datetime(2018, 3, 1)
all_entries = []
while date < datetime(2018, 7, 26):
    try:
        s = shelve.open('entries-2018-%02d-%02d.shelf' % (date.month,
                                                          date.day))
        entries = s['entries']
        all_entries.extend(entries)
        s.close()
    except:
        pass
    date += timedelta(days=1)

for entry in sorted(all_entries, key=lambda k: k['c.created']):
    app = get_app(entry)
    if not app:
        continue
    if app not in known_apps:
        app = "other"
    tags = get_tags(entry)
    if not tags:
        continue

    weeknum = get_weeknum(entry['c.created'])
    print(entry['a.created'], weeknum)
    if weeknum not in weekly_data:
        weekly_data[weeknum] = {}
        for ka in known_apps:
            weekly_data[weeknum][ka] = 0
        weekly_data[weeknum]['other'] = 0

    # print(entry['a.name'], app, tags)
    if app not in apps:
        apps[app] = 1
    else:
        apps[app] += 1

    author = entry['a.name']
    if app not in apps_per_user:
        apps_per_user[app] = 1
        appusers[app] = set([author])
        weekly_data[weeknum][app] = 1
    elif author not in appusers[app]:
        apps_per_user[app] += 1
        appusers[app] |= set([author])
        weekly_data[weeknum][app] += 1


for week in weekly_data:
    print(week, weekly_data[week])

all_apps = known_apps.copy()
all_apps.append('other')

xrange = {}
yrange = {}

for app in all_apps:
    xrange[app] = list(weekly_data.keys())[1:-1]
    yrange[app] = [weekly_data[wk][app] for wk in xrange[app]]

for app in sorted(yrange, key=lambda k: max(yrange[k]), reverse=True):
    print(app, yrange[app])

apps_sorted = sorted(yrange, key=lambda k: max(yrange[k]), reverse=True)
args = {'linestyle':'-', 'marker':"."}

# plot steemit
plt.figure(figsize=(12, 6))
m = 100
xticks = []
for app in apps_sorted[0:1]:
    plt.plot(xrange[app], yrange[app], label=app, **args)
    m = max(m, max(yrange[app]))
    xticks = xrange[app]
plt.grid()
plt.gca().set_xticks(xticks)
plt.xlabel("Calendar Week")
plt.title("Number of first time app users per app and week")
plt.ylabel("Number of first time app users")
plt.ylim([0, m*1.2])
plt.legend()
plt.savefig("apps0.png")

# plot all others in groups of 6
step = 6
for i in range(1, len(apps_sorted)+1, step):
    print(i, i+step)
    plt.figure(figsize=(12, 6))
    m = 100
    xticks = []
    for app in apps_sorted[i:i+step]:
        plt.plot(xrange[app], yrange[app], label=app, **args)
        xticks = xrange[app]
        m = max(m, max(yrange[app]))
    plt.grid()
    plt.legend()
    plt.gca().set_xticks(xticks)
    plt.xlabel("Calendar Week")
    plt.title("Number of first time app users per app and week")
    plt.ylabel("Number of first time app users")
    plt.ylim([0, m*1.2])
    plt.savefig("apps%d.png" % (i))
