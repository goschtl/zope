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
from zope.location.interfaces import ILocation
from zope.interface import implements
from grokcore.component import Context

class AppRoot(object):
    grok.implements(IAppRoot, ILocation)

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
	key = megrok.storm.directive.key.bind().get(self)
	rc = []
	for obj in store.find(object):
	    obj.__name__ = getattr(obj, key)
	    obj.__parent__ = self
	    rc.append(obj)
        return iter( rc )

    def __getitem__(self, name):
        store = self.getStore()
	object = megrok.storm.directive.rdb_object.bind().get(self)
	key = megrok.storm.directive.key.bind().get(self)
        key_property = getattr(object, key)
        item = store.find(object, key_property == name).one()
        ### Set ILocation if item
	if item:
	    item.__parent__ = self
	    item.__name__ = name 
        return item

    def  __setitem__(self, name, item):
        key = self.key
        setattr(item, key, name)
        store = self.getStore()
        store.add(item)
	### Add Location Information
	key = megrok.storm.directive.key.bind().get(self)
	item.__name__ = getattr(item, key) 
	item.__parent__ = self

    def add(self, item):
        store = self.getStore()
        store.add(item)
	### Add Location Information
	key = megrok.storm.directive.key.bind().get(self)
	item.__name__ = getattr(item, key) 
	item.__parent__ = self

    def delete(self, item):	
        store = self.getStore()
        store.remove(item)

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

    def get(self, key, default=None):
        try:
	    return self[key]
	except TypeError:
	    return default

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


class Model(Context):
    implements(ILocation)

    __parent__ = None
    __name__ = None


