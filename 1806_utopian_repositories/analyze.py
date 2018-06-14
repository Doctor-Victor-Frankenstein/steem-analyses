import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import shelve
import json
import re
from hist import hist
from prettytable import PrettyTable
from datetime import date, timedelta

# important dates
rejecting_bitdbots = date(2018, 6, 5)
vipo_service = date(2018, 6, 4)
bug_tr = date(2018, 6, 1)
rules_to_guidelines = date(2018, 5, 21)
graphics_tr = date(2018, 3, 16)
social_tr = date(2018, 3, 29)


def print_hist(hist, label="Key", limit=10):
    t = PrettyTable([label, "Value"])
    t.align = "l"
    for key, val in zip(hist.xrange()[:limit], hist.yrange()[:limit]):
        t.add_row([key, val])
    print(t.get_string())

posts = []
for month in range(3, 6):
    s = shelve.open("utopian-posts-new-%02d.shelf" % (month))
    posts.extend([p for p in s['posts'] if p['created'].date() > graphics_tr])
    s.close()

repo_regex = "^(\/exit\?url=|\s*)http[s]?:\/\/[w\.]*github\.com\/([^\/]+\/[^\/]+)(\/?|\/issues.*|\/pull.*|\/commit.*|\/tree.*|\/wiki.*)$"
contribution_types = ['copywriting', 'tutorials', 'development', 'tutorial',
                      'ideas', 'documentation', 'video-tutorials',
                      'blog', 'graphics', 'analysis', 'bug-hunting',
                      'social', 'translations', 'sub-projects', 'bug']
tasks = ["task-%s" % (t) for t in contribution_types]
contribution_types.extend(tasks)

type_whitelist = [ 'development', 'bug-hunting', 'graphics', 'ideas',
                   'analysis', 'blog', 'copywriting', 'tutorials', 'social' ]
type_color = {'analysis': 'green', 'blog': 'blue', 'bug-hunting':
              'red', 'copywriting': 'grey', 'development':'black',
              'graphics': 'orange', 'ideas':'lightgreen', 'tutorials':
              'violet', 'social':'lightblue'}

def parse_meta(meta):
    repo = None
    # if "bug-hunting" in str(meta):
    #     print(meta)
    if 'repository' in meta and meta['repository'] and \
       'full_name' in meta['repository']:
        repo = meta['repository']['full_name']
    elif 'links' in meta:
        for link in meta['links']:
            m = re.search(repo_regex, link)
            if m:
                repo = m.groups()[1].lower()
                break
    if not repo:
        print(meta)

    ctype = None
    if 'type' in meta and meta['type'] in contribution_types:
        ctype = meta['type']
    elif 'tags' in meta:
        if len(meta['tags']) > 1 and \
           meta['tags'][1] in contribution_types:
            ctype = meta['tags'][1]
        elif len(meta['tags']) > 2 and \
           meta['tags'][2] in contribution_types:
            ctype = meta['tags'][2]
    # if repo and not ctype:
    #     print("***", meta['tags'], repo)
    if ctype and 'tutorial' in ctype:
        ctype = "tutorials"
    if ctype and 'bug' in ctype:
        ctype = "bug-hunting"
    return {'repo': repo, 'type': ctype}

repos = 0
failed = 0
repo_stats = hist()
report_type_stats = {}
contribs_per_repo = {}
repo_set = set()
dev_repo_set = set()
bug_repo_set = set()

first_contribs = hist()
first_dev_contribs = hist()
first_bug_contribs = hist()
num_contribs = hist()
start_date = graphics_tr
while start_date < date(2018, 6, 1):
    first_contribs.fill(start_date, 0)
    num_contribs.fill(start_date, 0)
    first_dev_contribs.fill(start_date, 0)
    first_bug_contribs.fill(start_date, 0)
    start_date += timedelta(days=1)


for p in posts:
    votes = json.loads(p['active_votes'])
    upvoted = False
    for v in votes:
        if v['voter'] == "utopian-io" and int(v['percent']) > 0:
            upvoted = True
            break
    if not upvoted:
        continue
    meta = json.loads(p['json_metadata'])
    if 'tags' in meta and "utopian" not in meta['tags'][0]:
        continue
    if 'tags' in meta and 'utopian-edu' in meta['tags']:
        continue
    if 'tags' in meta and (set(tasks) & set(meta['tags'])):
        continue
    if 'github' not in str(meta):
        continue
    pm = parse_meta(meta)
    if pm['repo'] and pm['type']:
        if pm['type'] not in type_whitelist:
            continue
        if pm['repo'] not in repo_set:
            first_contribs.fill(p['created'].date())
        repo_set |= set([pm['repo']])
        if pm['type'] == "development":
            if pm['repo'] not in dev_repo_set:
                first_dev_contribs.fill(p['created'].date())
            dev_repo_set |= set([pm['repo']])
        if pm['type'] == "bug-hunting":
            if pm['repo'] not in bug_repo_set:
                first_bug_contribs.fill(p['created'].date())
            bug_repo_set |= set([pm['repo']])
        num_contribs.fill(p['created'].date())
        # if "bug" in pm['type']:
        #     print(pm)

        repos += 1
        # print(pm)
        repo_stats.fill(pm['repo'])
        if pm['type'] not in report_type_stats:
            report_type_stats[pm['type']] = hist()
        report_type_stats[pm['type']].fill(pm['repo'])

        if pm['repo'] not in contribs_per_repo:
            contribs_per_repo[pm['repo']] = hist()
        contribs_per_repo[pm['repo']].fill(pm['type'])
    else:
        print(pm)
        failed += 1

print(repos, failed)
print_hist(repo_stats, limit=20, label="All contributions")
print_hist(report_type_stats['development'], limit=20,
           label="Development contributions")
print_hist(report_type_stats['bug-hunting'], limit=20,
           label="Bug-hunting contributions")

###############################################################################
# first contributions
###############################################################################
fig = plt.figure(figsize=(12, 6))
w = 0.3
num_xrange = date2num(num_contribs.xrange('key'))
left = [x - 0.25 for x in num_xrange]
right = [x + 0.25 for x in num_xrange]
label = "Total number of voted utopian contributions per day"
plt.bar(num_xrange, num_contribs.yrange('key'), label=label, width=1)
label = "Number of first-time contributions to a repository per day"
plt.bar(num_xrange, first_contribs.yrange('key'), label=label,
        width=1)
label = "Number of first-time development contributions to a repository per day"
plt.bar(left, first_dev_contribs.yrange('key'), label=label,
        width=0.5, color="black", align="center")
label = "Number of first-time bug-hunting contributions to a repository per day"
plt.bar(right, first_bug_contribs.yrange('key'), label=label,
        width=0.5, color="red", align="center")
lineargs = {'linewidth': 2, 'linestyle': 'dashed'}
plt.axvline(date2num(bug_tr), label="Bug-hunting via TR only",
            **lineargs, color="green")
plt.axvline(date2num(graphics_tr),
            label="Graphics/Visibility/Copywriting via TR only",
            **lineargs, color="red")
plt.title("Number of contributions per day")
plt.xlabel("Date")
plt.legend()
plt.ylabel("Number of contributions")
plt.gca().xaxis_date()
plt.gcf().autofmt_xdate(rotation=30)
plt.grid()
plt.savefig("first_contribs.png")

###############################################################################
# contribution types to repos with only a single contribution
###############################################################################
single_type = hist()
single_type_list = open("single_type_list.txt", "w")
for repo in contribs_per_repo:
    total = sum(contribs_per_repo[repo].yrange())
    #if total >= MIN_CONTRIB_COUNT:

    if total != 1:
        continue
    single_type.fill(contribs_per_repo[repo].xrange()[0])
    single_type_list.write(repo+"\n")
print_hist(single_type, label="single type contributions")
single_type_list.close()

###############################################################################
# Contributions per repo + single-contrib breakdown
###############################################################################
fig = plt.figure(figsize=(12, 6))
max_contributions = max(repo_stats.yrange())
total_repos = len(repo_stats.xrange())
print("total_repos", total_repos)
xlabel = "Number of contributions"
ylabel = "Number of repositories"
title = "Number of contributions per repository"
p1 = fig.add_subplot(121, xlabel=xlabel, ylabel=ylabel, title=title)
p1.hist(repo_stats.yrange(), bins=max_contributions, # [0, 10, 20, 30, 40, 50, 60, 70, 80], #
         range=[1, max_contributions])
p1.grid()

title = "Contribution type of repos with only a single contribution"
p2 = fig.add_subplot(122, title=title)
p2.pie(single_type.yrange(), labels=single_type.xrange(),
       autopct="%.1f%%")

plt.tight_layout()
plt.savefig("contribs_per_repo.png")



limit = 20
t = PrettyTable(["Repo", 'Contrib count', 'types'])
t.align = "l"
row = 0
stacks = {}
repos = []
for repo, count in zip(repo_stats.xrange()[:limit],
                       repo_stats.yrange()[:limit]):
    t.add_row([repo, count, contribs_per_repo[repo].hist])
    for tp in type_whitelist:
        if tp not in stacks:
            stacks[tp] = []
        if tp in contribs_per_repo[repo].hist:
            stacks[tp].append(contribs_per_repo[repo].hist[tp])
        else:
            stacks[tp].append(0)
    row += 1
    repos.append(repo)
print(t.get_string())



###############################################################################
# Contribution type breakdown - all contributions
###############################################################################
xrange = range(row)
plt.figure(figsize=(12, 6))
bottom = [0] * row
for tp in stacks:
    plt.bar(xrange, stacks[tp], bottom=bottom, label=tp, color=type_color[tp])
    bottom = [bottom[k] + stacks[tp][k] for k in range(row)]
plt.grid()
plt.title("Repositories with most contributions")
plt.gca().set_xticklabels(repos)
plt.gca().set_xticks(xrange)
plt.gcf().autofmt_xdate(rotation=30)
plt.legend()
plt.savefig("stacks_all.png")



row = 0
t = PrettyTable(["#", "Repo", 'Contrib count', 'types'])
t.align = "l"
stacks = {}
repos = []
repos_per_type = hist()
for repo, count in zip(repo_stats.xrange(),
                       repo_stats.yrange()):
    for ct in contribs_per_repo[repo].xrange():
        repos_per_type.fill(ct)
    if row < 20:
        min_req = set(['development', 'bug-hunting'])
        ctypes = set(contribs_per_repo[repo].hist.keys())
        #print(repo, (min_req & ctypes))
        if (min_req & ctypes) == min_req:
            for tp in type_whitelist:
                if tp not in stacks:
                    stacks[tp] = []
                if tp in contribs_per_repo[repo].hist:
                    stacks[tp].append(contribs_per_repo[repo].hist[tp])
                else:
                    stacks[tp].append(0)

            row += 1
            repos.append(repo)
            t.add_row([row, repo, count, contribs_per_repo[repo].hist])
print(t.get_string())
print("Number of repos with dev+bug", len(repos))

###############################################################################
# Distinct repositories per contribution type
###############################################################################
plt.figure(figsize=(12, 6))
xrange = range(len(repos_per_type.xrange()))
plt.bar(xrange, repos_per_type.yrange())
plt.gca().set_xticklabels(repos_per_type.xrange())
plt.gca().set_xticks(xrange)
plt.gcf().autofmt_xdate(rotation=30)
plt.grid()
plt.title("Number of repositories reached per contribution type")
plt.xlabel("Category")
plt.ylabel("Number of repositories")
plt.savefig("repos_per_type.png")

print_hist(repos_per_type, "repos per type")

###############################################################################
# Contribution type breakdown - at least development + bug-hunting
###############################################################################
xrange = range(row)
plt.figure(figsize=(12, 6))
bottom = [0] * row
for tp in stacks:
    plt.bar(xrange, stacks[tp], bottom=bottom, label=tp, color=type_color[tp])
    bottom = [bottom[k] + stacks[tp][k] for k in range(row)]

plt.grid()
plt.title("Repositories with most contributions\n"
          "but with at least development and bug-reporting")
plt.gca().set_xticklabels(repos)
plt.gca().set_xticks(xrange)
plt.gcf().autofmt_xdate(rotation=30)
plt.legend()
plt.savefig("stacks.png")
