import sys
import datetime
import pytz
import persistent
from zope import interface, event, component
from zc.copyversion import interfaces
import zope.annotation.interfaces
from zope.cachedescriptors.property import Lazy
# import rwproperty
from zc.copyversion import rwproperty

def method(f):
    def wrapper(self, *args, **kwargs):
        try: # micro-optimize for the "yes, I'm already versioned" story
            versioned = self._z_versioned
        except AttributeError:
            versioned = interfaces.IVersioning(self)._z_versioned
        if versioned:
            raise interfaces.VersionedError
        return f(self, *args, **kwargs)
    return wrapper

class setproperty(rwproperty.rwproperty):

    @staticmethod
    def createProperty(func):
        return property(None, method(func))

    @staticmethod
    def enhanceProperty(oldprop, func):
        return property(oldprop.fget, method(func), oldprop.fdel)

class delproperty(rwproperty.rwproperty):

    @staticmethod
    def createProperty(func):
        return property(None, None, method(func))

    @staticmethod
    def enhanceProperty(oldprop, func):
        return property(oldprop.fget, oldprop.fset, method(func))

def makeProperty(name, default=None):
    protected = '_z_%s__' % name
    sys._getframe(1).f_locals[name] = property(
        lambda self: getattr(self, protected, default),
        method(lambda self, value: setattr(self, protected, value)))

class VersioningData(persistent.Persistent):
    interface.implements(interfaces.IVersioningData)
    def __init__(self):
        self._z__version_timestamp = datetime.datetime.now(pytz.utc)

    @property
    def _z_version_timestamp(self):
        return self._z__version_timestamp
    

class Versioning(object):
    interface.implements(interfaces.IVersioning)

    _z__versioning_data = None

    @property
    def _z_versioned(self):
        return self._z__versioning_data is not None

    @property
    def _z_version_timestamp(self):
        res = self._z__versioning_data
        if res is not None:
            return res._z_version_timestamp

    @method
    def _z_version(self):
        self._z__versioning_data = VersioningData()
        event.notify(interfaces.ObjectVersionedEvent(self))

KEY = "zc.copyversion._z_version_timestamp"

class VersioningAdapter(object):
    interface.implements(interfaces.IVersioning)
    component.adapts(zope.annotation.interfaces.IAnnotatable)

    def __init__(self, context):
        self.context = context

    @Lazy
    def annotations(self):
        return zope.annotation.interfaces.IAnnotations(self.context)

    @property
    def _z_versioned(self):
        return self.annotations.get(KEY) is not None

    @property
    def _z_version_timestamp(self):
        res = self.annotations.get(KEY)
        if res is not None:
            return res._z_version_timestamp

    @method
    def _z_version(self):
        self.annotations[KEY] = VersioningData()
        event.notify(interfaces.ObjectVersionedEvent(self.context))

