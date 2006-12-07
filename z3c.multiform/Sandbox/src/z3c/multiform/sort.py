from zope import interface, component
from zope.interface import Interface
from zope.schema.interfaces import IField

from z3c.multiform.interfaces import ISorter


class SchemaSorter(object):

    interface.implements(ISorter)
    component.adapts(Interface, IField)

    def __init__(self,schema,field):
        self.schema = schema
        self.name = field.__name__
        self.field = field

    def sort(self,seq):
        l = []
        def _v(o):
            o = self.schema(o)
            field=self.field.bind(o)
            v = field.get(o)
            if hasattr(field,'vocabulary'):
                # XXX maybe this is an adapter issue
                v = field.vocabulary.getTerm(v).token
            return v
        def _cmp(a,b):
            # none comparison
            a,b = a[0],b[0]
            if a==None and b: return -1
            if b==None and a: return 1
            return cmp(a,b)
        for item in seq:
            l.append((_v(item[1]),item))
        l.sort(_cmp)
        return map(lambda i:i[1],l)        
