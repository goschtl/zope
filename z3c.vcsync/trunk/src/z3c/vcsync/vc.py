import os
from datetime import datetime

from zope.interface import Interface
from zope.component import queryUtility, getUtility, queryAdapter
from zope.app.container.interfaces import IContainer
from zope.traversing.interfaces import IPhysicallyLocatable

from z3c.vcsync.interfaces import IVcDump, ISerializer, IVcFactory, ISynchronizer

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

def resolve(root, root_path, path):
    rel_path = path.relto(root_path)
    steps = rel_path.split('/')
    steps = [step for step in steps if step != '']
    steps = steps[1:]
    obj = root
    for step in steps:
        name, ex = os.path.splitext(step)
        try:
            obj = obj[name]
        except KeyError:
            return None
    return obj

def resolve_container(root, root_path, path):
    rel_path = path.relto(root_path)
    steps = rel_path.split('/')
    steps = [step for step in steps if step != '']
    steps = steps[1:-1]
    obj = root
    for step in steps:
        try:
            obj = obj[step]
        except KeyError:
            return None
    return obj

class Synchronizer(object):
    grok.implements(ISynchronizer)

    def __init__(self, checkout, state):
        self.checkout = checkout
        self.state = state

    def sync(self, dt, message=''):
        self.save(dt)
        self.checkout.up()
        self.checkout.resolve()
        self.load(dt)
        self.checkout.commit(message)

    def save(self, dt):
        # remove all files that have been removed in the database
        path = self.checkout.path
        for removed_path in self.state.removed(dt):
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
        root = self.state.root
        for obj in self.state.objects(dt):
            IVcDump(obj).save(self,
                               self._get_container_path(root, obj))

    def load(self, dt):
        root = self.state.root

        for deleted_path in self.checkout.deleted():
            obj = resolve(root, self.checkout.path, deleted_path)
            if obj is not None:
                del obj.__parent__[obj.__name__]
        added_paths = self.checkout.added()
        # to ensure that containers are created before items we sort them
        sorted(added_paths)
        for added_path in added_paths:
            obj = resolve_container(root, self.checkout.path, added_path)
            factory = getUtility(IVcFactory, name=added_path.ext)
            obj[added_path.purebasename] = factory(self, added_path)
        for modified_path in self.checkout.modified():
            obj = resolve(root, self.checkout.path, modified_path)
            factory = getUtility(IVcFactory, name=modified_path.ext)
            container = obj.__parent__
            name = obj.__name__
            del container[name]
            container[name] = factory(self, modified_path)

    def _get_container_path(self, root, obj):
        steps = []
        while obj is not root:
            obj = obj.__parent__
            steps.append(obj.__name__)
        steps.reverse()
        return self.checkout.path.join(*steps)
