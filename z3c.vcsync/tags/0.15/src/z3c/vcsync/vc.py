import os
import py
from datetime import datetime

from zope.interface import Interface
from zope.component import queryUtility, getUtility, queryAdapter
from zope.app.container.interfaces import IContainer
from zope.traversing.interfaces import IPhysicallyLocatable

from z3c.vcsync.interfaces import (IDump, ISerializer, IParser,
                                   IState, IFactory, ISynchronizer,
                                   ISynchronizationInfo)

import grok

class Dump(grok.Adapter):
    """General dump for arbitrary objects.

    Can be overridden for specific objects (such as containers).
    """
    grok.provides(IDump)
    grok.context(Interface)

    def save(self, path):
        serializer = ISerializer(self.context)
        path = path.join(serializer.name())
        path.ensure()
        f = path.open('w')
        serializer.serialize(f)
        f.close()
        return path
    
class ContainerDump(grok.Adapter):
    grok.provides(IDump)
    grok.context(IContainer)
        
    def save(self, path):
        path = path.join(self.context.__name__)
        path.ensure(dir=True)

def resolve(root, root_path, path):
    """Resolve checkout path to obj in state.

    root - the root container in the state
    root_path - a py.path reference to the checkout
    path - a py.path reference to the file in the checkout

    Returns the object in the state, or None.
    """
    rel_path = path.relto(root_path)
    steps = rel_path.split(os.path.sep)
    steps = [step for step in steps if step != '']
    obj = root
    for step in steps:
        name, ex = os.path.splitext(step)
        try:
            obj = obj[name]
        except KeyError:
            return None
    return obj

def resolve_container(root, root_path, path):
    """Resolve checkout path to container in state.

    root - the root container in the state
    root_path - a py.path reference to the checkout
    path - a py.path reference to the directory in the checkout

    Returns the container in the state, or None.
    """
    rel_path = path.relto(root_path)
    steps = rel_path.split(os.path.sep)
    steps = [step for step in steps if step != '']
    if not steps:
        return None
    steps = steps[:-1]
    obj = root
    for step in steps:
        try:
            obj = obj[step]
        except KeyError:
            return None
    return obj

def get_object_path(root, obj):
    """Return state-specific path for obj.

    Given state root container and obj, return internal path to this obj.
    """
    steps = []
    while obj is not root:
        steps.append(obj.__name__)
        obj = obj.__parent__
    steps.reverse()
    return '/' + '/'.join(steps)

class Synchronizer(object):
    grok.implements(ISynchronizer)

    def __init__(self, checkout, state):
        self.checkout = checkout
        self.state = state
        self._to_remove = []

    def sync(self, message='', modified_function=None):
        revision_nr = self.state.get_revision_nr()
        # store some information for the synchronization info
        objects_changed, object_paths_changed, object_paths_removed =\
                         self._get_changed_removed(revision_nr)
        # save the state to the checkout
        self.save(revision_nr)
        # update the checkout
        self.checkout.up()
        # resolve any conflicts
        self.checkout.resolve()
        # now after doing an up, remove dirs that can be removed
        # it is not safe to do this during safe, as an 'svn up' will
        # then recreate the directories again. We do want them
        # well and gone though, as we don't want them to reappear in
        # the ZODB when we do a load.
        for to_remove in self._to_remove:
            p = py.path.local(to_remove)
            if p.check():
                p.remove(rec=True)
        # store what was removed and modified in checkout now
        files_removed = self.checkout.removed(revision_nr)
        files_changed = self.checkout.files(revision_nr)
        # now load the checkout state back into the ZODB state
        modified_objects = self.load(revision_nr)
        # do a final pass with the modified_function if necessary
        if modified_function is not None:
            for obj in modified_objects:
                modified_function(obj)
        # and commit the checkout state
        self.checkout.commit(message)

        # we retrieve the revision number to which we just synchronized
        revision_nr = self.checkout.revision_nr()
        
        # we store the new revision number in the state
        self.state.set_revision_nr(revision_nr)
        # and we return some information about what happened
        return SynchronizationInfo(revision_nr,
                                   object_paths_removed, object_paths_changed,
                                   files_removed, files_changed)

    def _get_changed_removed(self, revision_nr):
        """Construct the true lists of objects that are changed and removed.

        Returns tuple with:

        * actual objects changed
        * object paths changed
        * object paths removed
        """
        # store these to report in SynchronizationInfo below
        object_paths_removed = list(self.state.removed(revision_nr))
        root = self.state.root
        objects_changed = list(self.state.objects(revision_nr))
        object_paths_changed = [get_object_path(root, obj) for obj in
                           objects_changed]
        return objects_changed, object_paths_changed, object_paths_removed
        
    def save(self, revision_nr):
        """Save objects to filesystem.
        """
        objects_changed, object_paths_changed, object_paths_removed =\
                         self._get_changed_removed(revision_nr)
        
        # remove all files that have been removed in the database
        path = self.checkout.path
        for removed_path in object_paths_removed:
            # construct path to directory containing file/dir to remove
            # note: this is a state-specific path which always uses /, so we
            # shouldn't use os.path.sep here
            steps = removed_path.split('/')
            container_dir_path = path.join(*steps[:-1])
            # construct path to potential directory to remove
            name = steps[-1]
            potential_dir_path = container_dir_path.join(name)
            if potential_dir_path.check():
                # the directory exists, so remove it
                potential_dir_path.remove()
                # this only marks the directory for vc deletion, so let's
                # truly get rid of it later
                self._to_remove.append(potential_dir_path.strpath)
            else:
                # there is no directory, so it must be a file to remove
                # the container might not exist for whatever reason
                if not container_dir_path.check():
                    continue
                # find the file and remove it
                file_paths = list(container_dir_path.listdir(
                    str('%s.*' % name)))
                # (could be 0 files in some cases)
                for file_path in file_paths:
                    file_path.remove()

        # now save all files that have been modified/added
        root = self.state.root
        for obj in objects_changed:
            if obj is not root:
                IDump(obj).save(self._get_container_path(root, obj))
  
    def load(self, revision_nr):
        # remove all objects that have been removed in the checkout
        root = self.state.root
        # sort to ensure that containers are deleted before items in them
        removed_paths = self.checkout.removed(revision_nr)
        removed_paths.sort()
        for removed_path in removed_paths:
            obj = resolve(root, self.checkout.path, removed_path)
            if obj is root:
                continue
            if obj is not None:
                del obj.__parent__[obj.__name__]
        # now modify/add all objects that have been modified/added in the
        # checkout
        file_paths = self.checkout.files(revision_nr)
        # to ensure that containers are created before items we sort them
        file_paths.sort()
        modified_objects = []
        for file_path in file_paths:
            # we might get something that doesn't actually exist anymore
            # as it was since removed, so skip it
            if not file_path.check():
                continue
            container = resolve_container(root, self.checkout.path, file_path)
            if container is None:
                continue
            name = file_path.purebasename
            ext = file_path.ext

            # if we already have the object, overwrite it, otherwise
            # create a new one
            if name in container:
                parser = getUtility(IParser, name=ext)
                parser(container[name], file_path)
            else:
                factory = getUtility(IFactory, name=ext)
                container[name] = factory(file_path)
            modified_objects.append(container[name])
        return modified_objects
    
    def _get_container_path(self, root, obj):
        steps = []
        assert root is not obj, "No container exists for the root"
        obj = obj.__parent__
        while obj is not root:
            steps.append(obj.__name__)
            obj = obj.__parent__
        steps.reverse()
        return self.checkout.path.join(*steps)

class AllState(object):
    """Report all state as changed.
    
    It reports all objects in the state as modified, and reports nothing
    removed. It actually completely ignores revision numbers. This
    implementation is not something you'd typically want to use in your
    own applications, but is useful for testing purposes.
    """
    grok.implements(IState)

    def __init__(self, root):
        self.root = root

    def set_revision_nr(self, revision_nr):
        pass

    def get_revision_nr(self):
        return 0
    
    def objects(self, revision_nr):
        for container in self._containers():
            for item in container.values():
                if not IContainer.providedBy(item):
                    yield item
            yield container

    def removed(self, revision_nr):
        return []
    
    def _containers(self):
        return self._containers_helper(self.root)

    def _containers_helper(self, container):
        yield container
        for obj in container.values():
            if not IContainer.providedBy(obj):
                continue
            for sub_container in self._containers_helper(obj):
                yield sub_container

class SynchronizationInfo(object):
    grok.implements(ISynchronizationInfo)

    def __init__(self, revision_nr,
                 objects_removed, objects_changed,
                 files_removed, files_changed):
        self.revision_nr = revision_nr
        self._objects_removed = objects_removed
        self._objects_changed = objects_changed
        self._files_removed = files_removed
        self._files_changed = files_changed

    def objects_removed(self):
        """Paths of objects removed in synchronization.

        The paths are state internal paths.
        """
        return self._objects_removed
    
    def objects_changed(self):
        """Paths of objects added or changed in synchronization.

        The paths are state internal paths.
        """
        return self._objects_changed
    
    def files_removed(self):
        """Paths of files removed in synchronization.

        The paths are filesystem paths (py.path objects)
        """
        return self._files_removed
    
    def files_changed(self):
        """The paths of files added or changed in synchronization.

        The paths are filesystem paths (py.path objects)
        """
        return self._files_changed
