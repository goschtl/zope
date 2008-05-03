from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.collections import MappedCollection
from sqlalchemy.schema import MetaData

from zope.interface import implements

from grokcore.component import Context
from zope.app.container.interfaces import IContainer

_lcl_metadata = MetaData()

class Model(Context):
    __metaclass__ = DeclarativeMeta
    metadata = _lcl_metadata
    _decl_class_registry = {}

    def __init__(self, **kwargs):
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
        raise RuntimeError("don't know how to do keying with composite primary keys")

class Container(Context, MappedCollection):
    implements(IContainer)

    def __init__(self, *args, **kw):
        if hasattr(self, '__rdb_key__'):
            keyfunc = lambda node:getattr(node, self.__rdb_key__)
        elif hasattr(self, 'keyfunc'):
            keyfunc = self.keyfunc
        else:
            keyfunc = default_keyfunc
        MappedCollection.__init__(self, keyfunc=keyfunc)
