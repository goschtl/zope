from zope.app.interfaces.copy import IObjectMover
from zope.app.interfaces.copy import IObjectCopier

class ObjectMover:
    '''Use getAdapter(obj, IObjectMover) to move an object somewhere.'''

    __implements__ = IObjectMover

    def __init__(self, container):
        self.context = container

    def moveTo(target, name=None):
        '''Move this object to the target given.
        
        Returns the new name within the target
        Typically, the target is adapted to IPasteTarget.'''

        object = self.context
        if target.acceptsObject(object):
            return target.pasteObject(object, name)
        
    def moveable():
        '''Returns True if the object is moveable, otherwise False.'''
        return True

    def moveableTo(target, name=None):
        '''Say whether the object can be moved to the given target.

        Returns True if it can be moved there. Otherwise, returns
        false.
        '''
        return True
    
class ObjectCopier:

    __implements__ = IObjectCopier

    def __init__(self, container):
        self.context = container

    def copyTo(target, name=None):
        """Copy this object to the target given.

        Returns the new name within the target, or None
        if the target doesn't do names.
        Typically, the target is adapted to IPasteTarget.
        After the copy is added to the target container, publish
        an IObjectCopied event in the context of the target container.
        If a new object is created as part of the copying process, then
        an IObjectCreated event should be published.
        """
        object = self.context
        if target.acceptsObject(object):
            return target.pasteObject(object, name)

    def copyable():
        '''Returns True if the object is copyable, otherwise False.'''
        return True

    def copyableTo(target, name=None):
        '''Say whether the object can be copied to the given target.
        
        Returns True if it can be copied there. Otherwise, returns
        False.
        '''
        return True
