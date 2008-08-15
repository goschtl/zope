import martian
from martian.error import GrokError
from sqlalchemy.ext.declarative import instrument_declarative

from megrok import rdb

def default_tablename(factory, module, **data):
    return factory.__name__.lower()

class ModelGrokker(martian.ClassGrokker):
    martian.component(rdb.Model)
    martian.directive(rdb.tablename, get_default=default_tablename)
    martian.directive(rdb.metadata)
    martian.directive(rdb.reflected)
    
    def execute(self, class_, tablename, metadata, reflected, **kw):
        class_.__tablename__ = tablename
        if reflected:
            if not hasattr(metadata, '_reflected_registry'):
                metadata._reflected_registry = {}
            metadata._reflected_registry[class_] = None
            # if this table is reflected, don't instrument now but
            # manually map later
            return True
        # we associate the _decl_registry with the metadata object
        # to make sure it's unique per metadata. A bit of a hack..
        if not hasattr(metadata, '_decl_registry'):
            metadata._decl_registry = {}
        instrument_declarative(class_, metadata._decl_registry, metadata)
        return True
    
class ContainerGrokker(martian.ClassGrokker):
    martian.component(rdb.Container)
    
    def grok(self, name, factory, module_info, config, **kw):
        rdb_key = rdb.key.bind().get(factory)
        if rdb_key and hasattr(factory, 'keyfunc'):
            raise GrokError(
                "It is not allowed to specify a custom 'keyfunc' method "
                "for rdb.Container %r, when a rdb.key directive has also "
                "been given." % factory, factory)
        return True
