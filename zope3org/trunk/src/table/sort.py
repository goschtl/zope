from interfaces import ISorter
from zope.interface import implements

class MethodSorter(object):

    implements(ISorter)
    
    def __init__(self,schema,method):
        self.schema = schema
        self.method = method.__name__

    def sort(self,items):

        def _cmp(a,b):
            return cmp(getattr(self.schema(a[1]),self.method)(),
                       getattr(self.schema(b[1]),self.method)())
        return sorted(items,_cmp)
    

class SchemaSorter(object):

    implements(ISorter)

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
                v = field.vocabulary.getTermByToken(v).value
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
