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
$Id: copypastemove.py,v 1.3 2003/03/19 19:57:21 alga Exp $
"""

from zope.app.traversing import getParent, objectName
from zope.component import getAdapter, queryAdapter
from zope.app.interfaces.copypastemove import IObjectMover
from zope.app.interfaces.copypastemove import IObjectCopier
from zope.app.interfaces.container import IAddNotifiable
from zope.app.interfaces.container import IDeleteNotifiable
from zope.app.interfaces.container import IMoveNotifiable
from zope.app.interfaces.container import ICopyNotifiable
from zope.app.interfaces.container import IMoveSource
from zope.app.interfaces.container import ICopySource
from zope.app.interfaces.container import IPasteTarget
from zope.app.interfaces.traversing import IPhysicallyLocatable
from zope.app.event.objectevent import ObjectMovedEvent, ObjectCopiedEvent
from zope.app.event import publish
from zope.proxy.introspection import removeAllProxies
from zope.app.attributeannotations import AttributeAnnotations

class ObjectMover:
    '''Use getAdapter(obj, IObjectMover) to move an object somewhere.'''

    __implements__ = IObjectMover

    def __init__(self, object):
        self.context = object

    def moveTo(self, target, name=None):
        '''Move this object to the target given.

        Returns the new name within the target
        Typically, the target is adapted to IPasteTarget.'''

        obj = self.context
        container = getParent(obj)
        orig_name = objectName(obj)
        if name is None:
            name = objectName(obj)

        movesource = getAdapter(container, IMoveSource)
        physicaltarget = getAdapter(target, IPhysicallyLocatable)
        target_path = physicaltarget.getPath()

        physicalsource = getAdapter(container, IPhysicallyLocatable)
        source_path = physicalsource.getPath()

        if queryAdapter(obj, IMoveNotifiable):
            getAdapter(obj, IMoveNotifiable).beforeDeleteHook(obj, container, \
                                    movingTo=target_path)
        elif queryAdapter(obj, IDeleteNotifiable):
            getAdapter(obj, IDeleteNotifiable).beforeDeleteHook(obj, container)

        new_obj = movesource.removeObject(orig_name, target)
        pastetarget = getAdapter(target, IPasteTarget)
        # publish an ObjectCreatedEvent (perhaps...?)
        new_name = pastetarget.pasteObject(name,new_obj)

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

    def copyTo(self, target, name=None):
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
        if name is None:
            name = objectName(obj)

        physicaltarget = getAdapter(target, IPhysicallyLocatable)
        target_path = physicaltarget.getPath()

        physicalsource = getAdapter(container, IPhysicallyLocatable)
        source_path = physicalsource.getPath()

        copysource = getAdapter(container, ICopySource)
        obj = copysource.copyObject(name, target_path)

        pastetarget = getAdapter(target, IPasteTarget)
        # publish an ObjectCreatedEvent (perhaps...?)
        new_name = pastetarget.pasteObject(name, obj)

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

