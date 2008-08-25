import martian
import grokcore.component
import megrok.storm
from martian.error import GrokError
from grok.meta import ViewGrokker, default_view_name
from zope.configuration.exceptions import ConfigurationError

from storm.zope.metaconfigure import store

class StoreGrokker(martian.ClassGrokker):
    martian.component(megrok.storm.Store)
    martian.directive(megrok.storm.storename)
    martian.directive(megrok.storm.uri)

    def execute(self, factory, config, storename, uri, **kw):
	store(config, storename, uri)
	return True

def default_tablename(factory, module, **data):
    return factory.__name__.lower()

class ModelGrokker(martian.ClassGrokker):
    martian.component(megrok.storm.Model)
    martian.directive(megrok.storm.tablename, get_default=default_tablename)
    
    def execute(self, class_, tablename,  **kw):
        class_.__storm_table__ = tablename
        # we associate the _decl_registry with the metadata object
        # to make sure it's unique per metadata. A bit of a hack..
        return True

class AppRootGrokker(martian.ClassGrokker):
    martian.component(megrok.storm.AppRoot)
    martian.directive(megrok.storm.key)
    martian.directive(megrok.storm.rdb_object)

    def execute(self, class_, key, rdb_object, **kw):
	class_.key = key
	class_.rdb_object = rdb_object
	return True
