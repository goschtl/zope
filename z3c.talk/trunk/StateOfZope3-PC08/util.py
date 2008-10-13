import csv
import datetime

def getDeveloperList(fn):
    devs = {}
    for row in csv.reader(open(fn, 'r'), delimiter='|'):
        user = row[1].strip()
        devs.setdefault(user, 0)
        devs[user] += 1
    return devs

def getTagList(fn):
    tags = {}
    total = 0
    cutoffDate = datetime.date(2007, 2, 1)
    for tagline in open(fn, 'r').readlines():
        te = [te for te in tagline.strip().split() if te]
        user = te[1]
        date = te[-4:-1]
        if ':' in date[-1]:
            date[-1] = '2008'
        date = datetime.datetime.strptime(
            '%s %s %s' %(date[0], date[1], date[2]), '%b %d %Y').date()
        if date > cutoffDate:
            tags.setdefault(user, 0)
            tags[user] += 1
            total += 1

    return total, tags
