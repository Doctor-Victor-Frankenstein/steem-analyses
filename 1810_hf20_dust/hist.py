#!/usr/bin/python
from prettytable import PrettyTable

class hist:
    def __init__(self):
        self.hist = {}
        self.list_of_values = {}

    def fill(self, key, incr = 1):
        if not key in self.hist:
            self.hist[key] = 0
            self.list_of_values[key] = []
        self.hist[key] += incr
        self.list_of_values[key].append(incr)

    def xrange(self, sort='value', reverse=True):
        if sort!='value':
            return [x for x in sorted(self.hist, reverse=reverse)]
        else:
            return [x for x in sorted(self.hist, key=lambda k:
                                      self.hist[k], reverse=reverse)]

    def yrange(self, sort='value', reverse=True):
        if sort!='value':
            return [self.hist[x] for x in sorted(self.hist,
                                                 reverse=reverse)]
        else:
            return [self.hist[x] for x in sorted(self.hist, key=lambda
                                                 k: self.hist[k],
                                                 reverse=reverse)]

    def prettytable(self, sort='value', limit=None, reverse=True, field_names=[]):
        t = PrettyTable()
        if field_names:
            t.field_names = field_names
        rows = 0
        for x, y in zip(self.xrange(sort=sort, reverse=reverse),
                        self.yrange(sort=sort, reverse=reverse)):
            t.add_row([x, y])
            rows += 1
            if limit and rows > limit:
                break
        return t
