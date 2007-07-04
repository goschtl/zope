import os
from datetime import datetime

from zope.interface import Interface
from zope.component import queryUtility, queryAdapter
from zope.app.container.interfaces import IContainer
from zope.traversing.interfaces import IPhysicallyLocatable

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
        path.ensure(dir=True)

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

    def sync(self, state, dt, message=''):
        self.save(state, dt)
        self.up()
        self.resolve()
        self.load(state.root)
        self.commit(message)

    def get_container_path(self, root, obj):
        steps = []
        while obj is not root:
            obj = obj.__parent__
            steps.append(obj.__name__)
        steps.reverse()
        return self.path.join(*steps)

    def save(self, state, dt):
        root = state.root

        # remove all files that have been removed in the database
        path = self.path
        for removed_path in state.removed(dt):
            # construct path to directory containing file/dir to remove
            steps = removed_path.split('/')
            container_dir_path = path.join(*steps[:-1])
            # construct path to potential directory to remove
            name = steps[-1]
            potential_dir_path = container_dir_path.join(name)
            if potential_dir_path.check():
                # the directory exists, so remove it
                potential_dir_path.remove()
            else:
                # there is no directory, so it must be a file to remove
                # find the file and remove it
                file_paths = list(container_dir_path.listdir(
                    str('%s.*' % name)))
                assert len(file_paths) == 1
                file_paths[0].remove()
        # now save all files that have been modified/added
        for obj in state.objects(dt):
            IVcDump(obj).save(self,
                               self.get_container_path(root, obj))

    def load(self, object):
        # XXX can only load containers here, not items
        names = [path.purebasename for path in self.path.listdir()
                 if not path.purebasename.startswith('.')]
        assert len(names) == 1
        IVcLoad(object).load(self, self.path.join(names[0]))
        
    def up(self):
        raise NotImplementedError

    def resolve(self):
        raise NotImplementedError

    def commit(self, message):
        raise NotImplementedError

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
