import random
from datetime import datetime, timedelta
from zope import component
import grok
from hurry.query.query import Query
from hurry import query

from grokstar.interfaces import PUBLISHED

class Year(grok.Model):
    def __init__(self, year):
        self.year = year

    def traverse(self, name):
        try:
            month = int(name)
        except ValueError:
            return None
        if month < 1 or month > 12:
            return None
        return Month(self.year, month)

class YearIndex(grok.View):
    grok.name('index')
    grok.context(Year)
    grok.template('dateindex')

    def entries(self):
        from_ = datetime(self.context.year, 1, 1)
        until = datetime(self.context.year + 1, 1, 1)
        return entriesInDateRange(from_, until)

class Month(grok.Model):
    def __init__(self, year, month):
        self.year = year
        self.month = month

    def traverse(self, name):
        try:
            day = int(name)
        except ValueError:
            return None
        # XXX should check whether day is acceptable
        return Day(self.year, self.month, day)

class MonthIndex(grok.View):
    grok.name('index')
    grok.context(Month)
    grok.template('dateindex')

    def entries(self):
        from_ = datetime(self.context.year,
                         self.context.month,
                         1)
        month = self.context.month + 1
        year = self.context.year
        if month > 12:
            month = 1
            year += 1
        until = datetime(year, month, 1)
        return entriesInDateRange(from_, until)

class Day(grok.Model):
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

class DayIndex(grok.View):
    grok.name('index')
    grok.context(Day)
    grok.template('dateindex')

    def entries(self):
        from_ = datetime(self.context.year,
                         self.context.month,
                         self.context.day)
        until = from_ + timedelta(days=1)
        return entriesInDateRange(from_, until)

def entriesInDateRange(from_, until):
    entries = Query().searchResults(
        query.And(query.Between(('entry_catalog', 'published'), from_, until),
                  query.Eq(('entry_catalog', 'workflow_state'), PUBLISHED)))
    
    return sorted(
        entries, key=lambda entry: entry.published, reverse=True
        )
