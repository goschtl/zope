"""
Use 'structured monkey patching' to enable zope.app.container event sending for
Zope 2 objects.
"""

from Products.Five.fiveconfigure import isFiveMethod
from zope.event import notify
from zope.interface import implements
from zope.app.container.interfaces import IObjectAddedEvent,\
     IObjectRemovedEvent
from zope.app.container.contained import ObjectMovedEvent
from zope.app.event.objectevent import ObjectCopiedEvent

# ObjectAddedEvent and ObjectRemovedEvent are different in Zope 2
class ObjectAddedEvent(ObjectMovedEvent):
    implements(IObjectAddedEvent)

    def __init__(self, object, newParent=None, newName=None):
        if newParent is None:
            newParent = object.aq_inner.aq_parent
        if newName is None:
            newName = object.id
        ObjectMovedEvent.__init__(self, object, None, None, newParent, newName)
    
class ObjectRemovedEvent(ObjectMovedEvent):
    implements(IObjectRemovedEvent)

    def __init__(self, object, oldParent=None, oldName=None):
        if oldParent is None:
            oldParent = object.aq_inner.aq_parent
        if oldName is None:
            oldName = object.id
        ObjectMovedEvent.__init__(self, object, oldParent, oldName, None, None)
    
def manage_afterAdd(self, item, container):
    original_location_path = getattr(self, '__five_location_path__', None)
    is_copied = getattr(self, '__five_is_copied__', None)
    self.__five_location_path__ = self.getPhysicalPath()
    try:
        del self.__five_is_copied__
    except:
        pass
    if original_location_path is None or is_copied:
        notify(ObjectAddedEvent(self))
    else:
        original_location = self.unrestrictedTraverse(
            original_location_path[:-1])
        notify(ObjectMovedEvent(self,
                                original_location, original_location_path[-1],
                                container, self.id))
    # call original
    method = getattr(self, '__five_original_manage_afterAdd', None)
    if method is not None:
        self.__five_original_manage_afterAdd(item, container)

manage_afterAdd.__five_method__ = None

def manage_afterClone(self, item):
    self.__five_is_copied = True
    notify(ObjectCopiedEvent(self))
    # call original
    method = getattr(self, '__five_original_manage_afterClone', None)
    if method is not None:
        self.__five_original_manage_afterClone(item)

manage_afterClone.__five_method__ = None

def manage_beforeDelete(self, item, container):
    notify(ObjectRemovedEvent(self))
    # call original
    method = getattr(self, '__five_manage_beforeDelete', None)
    if method is not None:
        self._five_original_manage_beforeDelete(item, container)

manage_beforeDelete.__five_method__ = None

def classSendEvents(class_):
    """Make instances of the class send Object*Event.
    """
    # tuck away original methods if necessary
    for name in ['manage_afterAdd', 'manage_beforeDelete',
                 'manage_afterClone']:
        method = getattr(class_, name, None)
        if not isFiveMethod(method):
            # if we haven't alread overridden this, tuck away originals
            setattr(class_, '__five_original_' + name, method)

    class_.manage_afterAdd = manage_afterAdd
    class_.manage_afterClone = manage_afterClone
    class_.manage_beforeDelete = manage_beforeDelete
    
def sendEvents(_context, class_):
    _context.action(
        discriminator = ('five:sendEvents', class_),
        callable = classSendEvents,
        args=(class_,)
        )
