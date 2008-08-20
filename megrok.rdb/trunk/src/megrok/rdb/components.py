from sqlalchemy.orm.collections import MappedCollection, collection

from zope.interface import implements

from grokcore.component import Context
from grok.interfaces import IContainer

from megrok.rdb import directive
from z3c.saconfig import Session

class Model(Context):
    def __init__(self, **kwargs):
        # XXX can we use the __init__ that sqlalchemy.ext.declarative sets up?
        for k in kwargs:
            if not hasattr(type(self), k):
                raise TypeError('%r is an invalid keyword argument for %s' %
                                (k, type(self).__name__))
            setattr(self, k, kwargs[k])

def default_keyfunc(node):
    primary_keys = node.__table__.primary_key.keys()
    if len(primary_keys) == 1:
        return getattr(node, primary_keys[0])
    else:
        raise RuntimeError(
            "don't know how to do keying with composite primary keys")

class Container(MappedCollection):
    implements(IContainer)

    def __init__(self, *args, **kw):
        rdb_key = directive.key.bind().get(self)
        if rdb_key:
            keyfunc = lambda node:getattr(node, rdb_key)
        elif hasattr(self, 'keyfunc'):
            keyfunc = self.keyfunc
        else:
            keyfunc = default_keyfunc
        MappedCollection.__init__(self, keyfunc=keyfunc)

    def _sa_on_link(self, adapter):
        self.__parent__ = adapter.owner_state.obj()
        self.__name__ = unicode(adapter.attr.key)
        
    def __setitem__(self, key, item):
        self._receive(item)
        MappedCollection.__setitem__(self, key, item)

    def __delitem__(self, key):
        self._release(self[key])
        MappedCollection.__delitem__(self, key)

    def _receive(self, item):
        item.__name__ = unicode(self.keyfunc(item))
        item.__parent__ = self

    def _release(self, item):
        del item.__name__
        del item.__parent__
    
    @collection.internally_instrumented
    @collection.appender
    def set(self, value, _sa_initiator=None):
        key = self.keyfunc(value)
        if key is None:
            session = Session()
            session.flush()
            key = self.keyfunc(value)
        self.__setitem__(key, value, _sa_initiator)
