from zope.interface import Interface

class IObjectMover(Interface):
    '''Use getAdapter(obj, IObjectMover) to move an object somewhere.'''

    def moveTo(target, new_name=None):
        '''Move this object to the target given.

        Returns the new name within the target
        Typically, the target is adapted to IPasteTarget.'''

    def moveable():
        '''Returns True if the object is moveable, otherwise False.'''

    def moveableTo(target, name=None):
        '''Say whether the object can be moved to the given target.

        Returns True if it can be moved there. Otherwise, returns
        false.
        '''

class IObjectCopier(Interface):

    def copyTo(target, new_name=None):
        """Copy this object to the target given.

        Returns the new name within the target, or None
        if the target doesn't do names.
        Typically, the target is adapted to IPasteTarget.
        After the copy is added to the target container, publish
        an IObjectCopied event in the context of the target container.
        If a new object is created as part of the copying process, then
        an IObjectCreated event should be published.
        """

    def copyable():
        '''Returns True if the object is copyable, otherwise False.'''

    def copyableTo(target, name=None):
        '''Say whether the object can be copied to the given target.

        Returns True if it can be copied there. Otherwise, returns
        False.
        '''

class INoChildrenObjectCopier(IObjectCopier):
    """Interface for adapters that can copy an containerish object
    without its children"""

    def copyTo(target, new_name=None):
        """Copy this object without chidren to the target given.

        Returns the new name within the target, or None
        if the target doesn't do names.
        Typically, the target is adapted to IPasteTarget.
        After the copy is added to the target container, publish
        an IObjectCopied event in the context of the target container.
        If a new object is created as part of the copying process, then
        an IObjectCreated event should be published.
        """

class IPrincipalClipboard(Interface):
    '''Interface for adapters that store/retrieve clipboard information
    for a principal.

    Clipboard information consists on tuples of {'action':action, 'target':target}.
    '''

    def clearContents():
        '''Clear the contents of the clipboard'''

    def addItems(action, targets):
        '''Add new items to the clipboard'''

    def setContents(clipboard):
        '''Replace the contents of the clipboard by the given value'''

    def getContents():
        '''Return the contents of the clipboard'''
