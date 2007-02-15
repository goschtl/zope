import grok
import Acquisition
from zope.interface import implements
from zope.app.container.interfaces import IContainer
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base

class Model(SimpleItem, grok.Model):

    def __init__(self, id=None):
        if id is not None:
            self.id = id

# This is a grok.Model only because it needs to be found as a possible
# context for views, adapters, etc.
class Container(BTreeFolder2Base, ObjectManager, grok.Model):
    implements(IContainer)

    # make Zope 2's absolute_url() happy
    def getId(self):
        return self.id

    # fulfill IContainer interface

    def keys(self):
        return self.objectIds()

    def values(self):
        return self.objectValues()

    def items(self):
        return self.objectItems()

    def get(self, name, default=None):
        return getattr(self, name, default)

    # __getitem__ is already implemented by ObjectManager

    def __setitem__(self, name, obj):
        name = str(name) # Zope 2 doesn't like unicode names
        # TODO there should be a check here if 'name' contains
        # non-ASCII unicode data. In this case I think we should just
        # raise an error.
        self._setObject(name, obj)

    def __delitem__(self, name):
        self.manage_delObjects([name])

    def __contains__(self, name):
        return self.hasObject(name)

    def __iter__(self):
        return iter(self.objectIds())

    def __len__(self):
        return len(self.objectIds())
