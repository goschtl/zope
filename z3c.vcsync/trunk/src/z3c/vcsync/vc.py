import os

from zope.interface import Interface
from zope.component import queryUtility
from zope.app.container.interfaces import IContainer

from z3c.vcsync.interfaces import (IVcDump, IVcLoad,
                                   ISerializer, IVcFactory,
                                   IModified, ICheckout)

import grok

class VcDump(grok.Adapter):
    """General VcDump for arbitrary objects.

    Can be overridden for specific objects (such as containers).
    """
    grok.provides(IVcDump)
    grok.context(Interface)

    def save(self, checkout, path):
        serializer = ISerializer(self.context)
        path = path.join(serializer.name())
        if not path.check():
            checkout.add(path)
        path.ensure()
        f = path.open('w')
        serializer.serialize(f)
        f.close()
        return path
    
class ContainerVcDump(grok.Adapter):
    grok.provides(IVcDump)
    grok.context(IContainer)
        
    def save(self, checkout, path):
        path = path.join(self.context.__name__)
        if not path.check():
            checkout.add(path)
        path.ensure(dir=True)
        added_paths = []
        for value in self.context.values():
            added_paths.append(IVcDump(value).save(checkout, path))
        # remove any paths not there anymore
        for existing_path in path.listdir():
            if existing_path not in added_paths:
                checkout.delete(existing_path)
                existing_path.remove()
        return path

class ContainerVcLoad(grok.Adapter):
    grok.provides(IVcLoad)
    grok.context(IContainer)
    
    def load(self, checkout, path):
        loaded = []
        for sub in path.listdir():
            if sub.basename.startswith('.'):
                continue
            if sub.check(dir=True):
                object_name = '' # containers are indicated by empty string
            else:
                object_name = sub.ext
            #if sub.read().strip() == '200':
            #    import pdb; pdb.set_trace()
            factory = queryUtility(IVcFactory, name=object_name, default=None)
            # we cannot handle this kind of object, so skip it
            if factory is None:
                continue
            # create instance of object and put it into the container
            # XXX what if object is already there?
            obj = factory(checkout, sub)
            # store the newly created object into the container
            if sub.purebasename in self.context:
                del self.context[sub.purebasename]
            self.context[sub.purebasename] = obj
            loaded.append(sub.purebasename)
        # remove any objects not there anymore
        for name in list(self.context.keys()):
            if name not in loaded:
                del self.context[name]

class CheckoutBase(object):
    """Checkout base class.

    (hopefully) version control system agnostic.
    """
    grok.implements(ICheckout)
    
    def __init__(self, path):
        self.path = path
        self.clear()

    def sync(self, object, message=''):
        self.save(object)
        self.up()
        self.resolve()
        self.load(object)
        self.commit(message)

    def save(self, object):
        IVcDump(object).save(self, self.path)

    def load(self, object):
        # XXX can only load containers here, not items
        names = [path.purebasename for path in self.path.listdir()
                 if not path.purebasename.startswith('.')]
        assert len(names) == 1
        IVcLoad(object).load(self, self.path.join(names[0]))
        
    def clear(self):
        self._added_by_save = []
        self._deleted_by_save = []
        
    def up(self):
        raise NotImplementedError

    def resolve(self):
        raise NotImplementedError

    def commit(self, message):
        raise NotImplementedError

    def add(self, path):
        self._added_by_save.append(path)

    def delete(self, path):
        self._deleted_by_save.append(path)

    def added_by_save(self):
        return self._added_by_save

    def deleted_by_save(self):
        return self._deleted_by_save

    def added_by_up(self):
        raise NotImplementedError

    def deleted_by_up(self):
        raise NotImplementedError

    def modified_by_up(self):
        raise NotImplementedError

class ContainerModified(grok.Adapter):
    grok.provides(IModified)
    grok.context(IContainer)

    def modified_since(self, dt):
        # containers themselves are never modified
        return False

