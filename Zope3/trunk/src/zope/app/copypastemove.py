##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

Revision information:
$Id: copypastemove.py,v 1.6 2003/05/01 19:35:02 faassen Exp $
"""

from zope.app.traversing import getParent, objectName, getPath
from zope.component import getAdapter, queryAdapter
from zope.app.interfaces.copypastemove import IObjectMover
from zope.app.interfaces.copypastemove import IObjectCopier, INoChildrenObjectCopier
from zope.app.interfaces.container import IAddNotifiable
from zope.app.interfaces.container import IDeleteNotifiable
from zope.app.interfaces.container import IMoveNotifiable
from zope.app.interfaces.container import ICopyNotifiable
from zope.app.interfaces.container import IMoveSource
from zope.app.interfaces.container import ICopySource, INoChildrenCopySource, \
     CopyException
from zope.app.interfaces.container import IPasteTarget
from zope.app.event.objectevent import ObjectMovedEvent, ObjectCopiedEvent
from zope.app.event import publish
from zope.proxy.introspection import removeAllProxies

class ObjectMover:
    '''Use getAdapter(obj, IObjectMover) to move an object somewhere.'''

    __implements__ = IObjectMover

    def __init__(self, object):
        self.context = object

    def moveTo(self, target, new_name=None):
        '''Move this object to the target given.

        Returns the new name within the target
        Typically, the target is adapted to IPasteTarget.'''

        obj = self.context
        container = getParent(obj)
        orig_name = objectName(obj)
        if new_name is None:
            new_name = orig_name

        movesource = getAdapter(container, IMoveSource)
        target_path = getPath(target)
        source_path = getPath(container)

        if queryAdapter(obj, IMoveNotifiable):
            getAdapter(obj, IMoveNotifiable).beforeDeleteHook(obj, container, \
                                    movingTo=target_path)
        elif queryAdapter(obj, IDeleteNotifiable):
            getAdapter(obj, IDeleteNotifiable).beforeDeleteHook(obj, container)

        new_obj = movesource.removeObject(orig_name, target)
        pastetarget = getAdapter(target, IPasteTarget)
        # publish an ObjectCreatedEvent (perhaps...?)
        new_name = pastetarget.pasteObject(new_name, new_obj)

        # call afterAddHook
        if queryAdapter(new_obj, IMoveNotifiable):
            getAdapter(new_obj, IMoveNotifiable).afterAddHook(new_obj, container, \
                                movedFrom=source_path)
        elif queryAdapter(new_obj, IAddNotifiable):
            getAdapter(new_obj, IAddNotifiable).afterAddHook(new_obj, container)

        # publish ObjectMovedEvent
        publish(container, ObjectMovedEvent(container, source_path, target_path))

        return new_name

    def moveable(self):
        '''Returns True if the object is moveable, otherwise False.'''
        return True

    def moveableTo(self, target, name=None):
        '''Say whether the object can be moved to the given target.

        Returns True if it can be moved there. Otherwise, returns
        false.
        '''
        obj = self.context
        if name is None:
            name = objectName(obj)
        pastetarget = getAdapter(target, IPasteTarget)
        return pastetarget.acceptsObject(name, obj)

class ObjectCopier:

    __implements__ = IObjectCopier

    def __init__(self, object):
        self.context = object

    def copyTo(self, target, new_name=None):
        """Copy this object to the target given.

        Returns the new name within the target, or None
        if the target doesn't do names.
        Typically, the target is adapted to IPasteTarget.
        After the copy is added to the target container, publish
        an IObjectCopied event in the context of the target container.
        If a new object is created as part of the copying process, then
        an IObjectCreated event should be published.
        """
        obj = self.context
        container = getParent(obj)
        orig_name = objectName(obj)
        if new_name is None:
            new_name = orig_name

        target_path = getPath(target)
        source_path = getPath(container)

        copysource = getAdapter(container, ICopySource)
        obj = copysource.copyObject(orig_name, target_path)

        pastetarget = getAdapter(target, IPasteTarget)
        # publish an ObjectCreatedEvent (perhaps...?)
        new_name = pastetarget.pasteObject(new_name, obj)

        # call afterAddHook
        if queryAdapter(obj, ICopyNotifiable):
            getAdapter(obj, ICopyNotifiable).afterAddHook(obj, container, \
                                copiedFrom=source_path)
        elif queryAdapter(obj, IAddNotifiable):
            getAdapter(obj, IAddNotifiable).afterAddHook(obj, container)

        # publish ObjectCopiedEvent
        publish(container, ObjectCopiedEvent(container, source_path, target_path))

        return new_name

    def copyable(self):
        '''Returns True if the object is copyable, otherwise False.'''
        return True

    def copyableTo(self, target, name=None):
        '''Say whether the object can be copied to the given target.

        Returns True if it can be copied there. Otherwise, returns
        False.
        '''
        obj = self.context
        if name is None:
            name = objectName(obj)
        pastetarget = getAdapter(target, IPasteTarget)
        return pastetarget.acceptsObject(name, obj)


class NoChildrenObjectCopier(ObjectCopier):

    __implements__ = INoChildrenObjectCopier

    def __init__(self, object):
        self.context = object

    def copyTo(self, target, new_name=None):
        """Copy this object but not its children to the target given.

        Returns the new name within the target, or None
        if the target doesn't do names.
        Typically, the target is adapted to IPasteTarget.
        After the copy is added to the target container, publish
        an IObjectCopied event in the context of the target container.
        If a new object is created as part of the copying process, then
        an IObjectCreated event should be published.
        """
        obj = self.context
        container = getParent(obj)
        orig_name = objectName(obj)
        if new_name is None:
            new_name = orig_name

        target_path = getPath(target)
        source_path = getPath(container)

        copysource = getAdapter(container, INoChildrenCopySource)
        obj = copysource.copyObjectWithoutChildren(orig_name, target_path)
        if obj is None:
            raise CopyException(container, orig_name, \
                                'Could not get a copy without children of %s' % orig_name) 

        pastetarget = getAdapter(target, IPasteTarget)
        # publish an ObjectCreatedEvent (perhaps...?)
        new_name = pastetarget.pasteObject(new_name, obj)

        # call afterAddHook
        if queryAdapter(obj, ICopyNotifiable):
            getAdapter(obj, ICopyNotifiable).afterAddHook(obj, container, \
                                copiedFrom=source_path)
        elif queryAdapter(obj, IAddNotifiable):
            getAdapter(obj, IAddNotifiable).afterAddHook(obj, container)

        # publish ObjectCopiedEvent
        publish(container, ObjectCopiedEvent(container, source_path, target_path))

        return new_name

class PrincipalClipboard:
    '''Clipboard information consists on tuples of {'action':action, 'target':target}.
    '''

    def __init__(self, annotation):
        self.context = annotation

    def clearContents(self):
        '''Clear the contents of the clipboard'''
        self.context['clipboard'] = ()

    def addItems(self, action, targets):
        '''Add new items to the clipboard'''
        contents = self.getContents()
        actions = []
        for target in targets:
            actions.append({'action':action, 'target':target})
        self.context['clipboard'] = contents + tuple(actions)

    def setContents(self, clipboard):
        '''Replace the contents of the clipboard by the given value'''
        self.context['clipboard'] = clipboard

    def getContents(self):
        '''Return the contents of the clipboard'''
        return removeAllProxies(self.context.get('clipboard', ()))

