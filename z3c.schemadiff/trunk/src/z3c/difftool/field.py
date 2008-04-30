from zope import interface
from zope import schema
from zope import component

from interfaces import IFieldDiff
from itertools import chain

class TextLineDiff(object):
    interface.implements(IFieldDiff)
    component.adapts(schema.TextLine)
    
    def __init__(self, field):
        pass

    def lines(self, value):
        return (value,)

class TextDiff(object):
    interface.implements(IFieldDiff)
    component.adapts(schema.Text)
    
    def __init__(self, field):
        pass

    def lines(self, value):
        return value.split('\n')

class SetDiff(object):
    interface.implements(IFieldDiff)
    component.adapts(schema.Set)
    
    def __init__(self, field):
        self.field = field

    def lines(self, value):
        diff = IFieldDiff(self.field.value_type)
        return tuple(chain(*[diff.lines(v) for v in value]))
