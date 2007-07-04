# replaces code in zope.copypastemove and in zope.location.pickling

import tempfile
import cPickle
import zope.component
import zope.event
import zope.lifecycleevent
import zope.copypastemove
import zope.app.container.interfaces
import zope.app.container.constraints
import zope.location
import zope.location.location
import zope.location.interfaces

from zc.copy import interfaces

# this is the part that replaces zope.location.pickling
@zope.component.adapter(zope.location.interfaces.ILocation)
@zope.interface.implementer(interfaces.ICopyHook)
def location_copyfactory(obj):
    def factory(location, register):
        if not zope.location.location.inside(obj, location):
            return obj
        raise interfaces.ResumeCopy
    return factory

# this is a more general form of zope.location.pickling.copyLocation
def clone(loc):
    tmp = tempfile.TemporaryFile()
    persistent = CopyPersistent(loc)

    # Pickle the object to a temporary file
    pickler = cPickle.Pickler(tmp, 2)
    pickler.persistent_id = persistent.id
    pickler.dump(loc)

    # Now load it back
    tmp.seek(0)
    unpickler = cPickle.Unpickler(tmp)
    unpickler.persistent_load = persistent.load

    res = unpickler.load()
    # run the registered cleanups
    def convert(obj):
        return unpickler.memo[pickler.memo[id(obj)][0]]
    for call in persistent.registered:
        call(convert)
    return res

def copy(loc):
    res = clone(loc)
    if getattr(res, '__parent__', None) is not None:
        try:
            res.__parent__ = None
        except AttributeError:
            pass
    if getattr(res, '__name__', None) is not None:
        try:
            res.__name__ = None
        except AttributeError:
            pass
    return res

class CopyPersistent(object):
    def __init__(self, location):
        self.location = location
        self.pids_by_id = {}
        self.others_by_pid = {}
        self.load = self.others_by_pid.get
        self.registered = []

    def id(self, obj):
        hook = interfaces.ICopyHook(obj, None)
        if hook is not None:
            oid = id(obj)
            if oid in self.pids_by_id:
                return self.pids_by_id[oid]
            try:
                res = hook(self.location, self.registered.append)
            except interfaces.ResumeCopy:
                pass
            else:
                pid = len(self.others_by_pid)
    
                # The following is needed to overcome a bug
                # in pickle.py. The pickle checks the boolean value
                # of the id, rather than whether it is None.
                pid += 1
    
                self.pids_by_id[oid] = pid
                self.others_by_pid[pid] = res
                return pid
        return None

# this is a generic object copier that uses the new copier above.
class ObjectCopier(zope.copypastemove.ObjectCopier):

    def copyTo(self, target, new_name=None):
        """Copy this object to the `target` given.

        Returns the new name within the `target`.

        Typically, the `target` is adapted to `IPasteTarget`.
        After the copy is added to the `target` container, publish
        an `IObjectCopied` event in the context of the target container.
        If a new object is created as part of the copying process, then
        an `IObjectCreated` event should be published.
        """
        obj = self.context
        container = obj.__parent__

        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name

        zope.app.container.constraints.checkObject(target, new_name, obj)

        chooser = zope.app.container.interfaces.INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)

        new = copy(obj)
        zope.event.notify(zope.lifecycleevent.ObjectCopiedEvent(new, obj))

        target[new_name] = new
        return new_name
