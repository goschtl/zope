import martian.util
import grokcore.component
from martian.error import GrokImportError
import grok
from storm.locals import *
from storm.zope.interfaces import IZStorm
from zope.component import getUtility
from zope.configuration.name import resolve
import megrok.storm
from interfaces import IAppRoot

class AppRoot(grok.Model):
    grok.implements(IAppRoot)

    def getStore(self):
	name = megrok.storm.directive.storename.bind().get(self)
        store = getUtility(IZStorm).get(name)
        return store

    def keys(self):
	key = megrok.storm.directive.key.bind().get(self)
	return [getattr(obj, key) for obj in self.__iter__()]

    def items(self):
	return [obj for obj in self.__iter__()]

    def __iter__(self):
        store = self.getStore()
	object = megrok.storm.directive.rdb_object.bind().get(self)
        return iter( store.find(object))

    def __getitem__(self, name):
        store = self.getStore()
	object = megrok.storm.directive.rdb_object.bind().get(self)
	key = megrok.storm.directive.key.bind().get(self)
        key_property = getattr(object, key)
        item = store.find(object, key_property == name).one()
        return item

    def  __setitem__(self, name, item):
        key = self.key
        setattr(item, key, name)
        store = self.getStore()
        store.add(item)

    def add(self, item):
        store = self.getStore()
        store.add(item)

    def __len__(self):
        store = self.getStore()
	object = megrok.storm.directive.rdb_object.bind().get(self)
        return store.find(object).count()

    def __delitem__(self, name):
        store = self.getStore()
	object = megrok.storm.directive.rdb_object.bind().get(self)
	obj = store.get(object, name)
	store.remove(obj)

    def traverse(self, name):
	return self[name]

    def filter(self, *args, **kwargs):
        store = self.getStore()
	object = megrok.storm.directive.rdb_object.bind().get(self)
	result = store.find(object, *args, **kwargs)
	return result


class Store(object):
    pass

class store(martian.MultipleTimesDirective):
    scope = martian.MODULE

    def factory(self, storename, uri):
	if martian.util.not_unicode_or_ascii(storename):
	    raise GrokImportError(
	        "You can only pass unicode or ASCII"
		"to megrok.storm.Store to the '%s' directive." % self.name)
	if martian.util.not_unicode_or_ascii(uri):
	    raise GrokImportError(
	        "You can only pass unicode or ASCII"
		"to megrok.storm.Store to the '%s' directive." % self.name)
	return (storename, uri)


class Model(grokcore.component.Context):
    pass


