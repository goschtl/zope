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
$Id: copypastemove.py,v 1.11 2003/09/21 17:30:08 jim Exp $
"""

from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.copypastemove import IObjectMover
from zope.app.interfaces.copypastemove import IObjectCopier
from zope.app.interfaces.container import IAddNotifiable
from zope.app.interfaces.container import INameChooser
from zope.proxy import removeAllProxies
from zope.interface import implements
from zope.exceptions import NotFoundError, DuplicationError
from zope.app.location import locationCopy
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCopiedEvent
from zope.proxy import removeAllProxies

class ObjectMover:
    """Adapter for moving objects between containers

    To use an object mover, pass a contained object to the class.
    The contained object should implement IContained.  It should be
    contained in a container that has an adapter to INameChooser.

    >>> from zope.app.container.sample import SampleContainer
    >>> class SampleContainer(SampleContainer):
    ...     implements(INameChooser)
    ...     def chooseName(self, name, ob):
    ...        while name in self:
    ...           name += '_'
    ...        return name

    >>> from zope.app.container.contained import Contained
    >>> ob = Contained()
    >>> container = SampleContainer()
    >>> container[u'foo'] = ob
    >>> mover = ObjectMover(ob)

    In addition to moving objects, object movers can tell you if the
    object is movable:

    >>> mover.moveable()
    1

    which, at least for now, they always are.  A better question to
    ask is whether we can move to a particular container. Right now,
    we can always move to a container of the same class:

    >>> container2 = SampleContainer()
    >>> mover.moveableTo(container2)
    1
    >>> mover.moveableTo({})
    0

    Of course, once we've decided we can move an object, we can use
    the mover to do so:

    >>> mover.moveTo(container2)
    >>> list(container)
    []
    >>> list(container2)
    [u'foo']
    >>> ob.__parent__ is container2
    1
    
    We can also specify a name:

    >>> mover.moveTo(container2, u'bar')
    >>> list(container2)
    [u'bar']
    >>> ob.__parent__ is container2
    1
    >>> ob.__name__
    u'bar'

    But we may not use the same name given, if the name is already in
    use:

    >>> container2[u'splat'] = 1
    >>> mover.moveTo(container2, u'splat')
    >>> l = list(container2)
    >>> l.sort()
    >>> l
    [u'splat', u'splat_']
    >>> ob.__name__
    u'splat_'
    

    If we try to move to an invalid container, we'll get an error:

    >>> mover.moveTo({})
    Traceback (most recent call last):
    ...
    TypeError: Can only move objects between like containers
        
    """

    implements(IObjectMover)

    def __init__(self, object):
        self.context = object

    def moveTo(self, target, new_name=None):
        '''Move this object to the target given.

        Returns the new name within the target
        Typically, the target is adapted to IPasteTarget.'''

        obj = self.context
        container = obj.__parent__

        # XXX Only allow moving between the same types of containers for
        # now, until we can properly implement containment constraints:
        if target.__class__ != container.__class__:
            raise TypeError(
                _("Can only move objects between like containers")
                )
        
        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name

        if target is container and new_name == orig_name:
            # Nothing to do
            return

        chooser = zapi.getAdapter(target, INameChooser)
        new_name = chooser.chooseName(new_name, obj)

        # Can't store security proxies
        obj = removeAllProxies(obj)

        target[new_name] = obj
        del container[orig_name]

    def moveable(self):
        '''Returns True if the object is moveable, otherwise False.'''
        return True

    def moveableTo(self, target, name=None):
        '''Say whether the object can be moved to the given target.

        Returns True if it can be moved there. Otherwise, returns
        false.
        '''
        return self.context.__parent__.__class__ == target.__class__ 

class ObjectCopier:
    """Adapter for copying objects between containers

    To use an object copier, pass a contained object to the class.
    The contained object should implement IContained.  It should be
    contained in a container that has an adapter to INameChooser.

    >>> from zope.app.container.sample import SampleContainer
    >>> class SampleContainer(SampleContainer):
    ...     implements(INameChooser)
    ...     def chooseName(self, name, ob):
    ...        while name in self:
    ...           name += '_'
    ...        return name

    >>> from zope.app.container.contained import Contained
    >>> ob = Contained()
    >>> container = SampleContainer()
    >>> container[u'foo'] = ob
    >>> copier = ObjectCopier(ob)

    In addition to moving objects, object copiers can tell you if the
    object is movable:

    >>> copier.copyable()
    1

    which, at least for now, they always are.  A better question to
    ask is whether we can copy to a particular container. Right now,
    we can always copy to a container of the same class:

    >>> container2 = SampleContainer()
    >>> copier.copyableTo(container2)
    1
    >>> copier.copyableTo({})
    0

    Of course, once we've decided we can copy an object, we can use
    the copier to do so:

    >>> copier.copyTo(container2)
    >>> list(container)
    [u'foo']
    >>> list(container2)
    [u'foo']
    >>> ob.__parent__ is container
    1
    >>> container2[u'foo'] is ob
    0
    >>> container2[u'foo'].__parent__ is container2
    1
    >>> container2[u'foo'].__name__
    u'foo'
    
    We can also specify a name:

    >>> copier.copyTo(container2, u'bar')
    >>> l = list(container2)
    >>> l.sort()
    >>> l
    [u'bar', u'foo']

    >>> ob.__parent__ is container
    1
    >>> container2[u'bar'] is ob
    0
    >>> container2[u'bar'].__parent__ is container2
    1
    >>> container2[u'bar'].__name__
    u'bar'

    But we may not use the same name given, if the name is already in
    use:

    >>> copier.copyTo(container2, u'bar')
    >>> l = list(container2)
    >>> l.sort()
    >>> l
    [u'bar', u'bar_', u'foo']
    >>> container2[u'bar_'].__name__
    u'bar_'
    

    If we try to copy to an invalid container, we'll get an error:

    >>> copier.copyTo({})
    Traceback (most recent call last):
    ...
    TypeError: Can only copy objects to like containers
        
    """

    implements(IObjectCopier)

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
        container = obj.__parent__

        # XXX Only allow moving between the same types of containers for
        # now, until we can properly implement containment constraints:
        if target.__class__ != container.__class__:
            raise TypeError(
                _("Can only copy objects to like containers")
                )

        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name

        chooser = zapi.getAdapter(target, INameChooser)
        new_name = chooser.chooseName(new_name, obj)

        copy = removeAllProxies(obj)
        copy = locationCopy(copy)
        copy.__parent__ = copy.__name__ = None
        publish(target, ObjectCopiedEvent(copy))

        target[new_name] = copy

    def copyable(self):
        '''Returns True if the object is copyable, otherwise False.'''
        return True

    def copyableTo(self, target, name=None):
        '''Say whether the object can be copied to the given target.

        Returns True if it can be copied there. Otherwise, returns
        False.
        '''
        return self.context.__parent__.__class__ == target.__class__ 


class PrincipalClipboard:
    '''Principal clipboard

    Clipboard information consists on tuples of
    {'action':action, 'target':target}.
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


def rename(container, oldid, newid):
    object = container.get(oldid)
    if object is None:
        raise NotFoundError(container, oldid)
    mover = zapi.getAdapter(object, IObjectMover)

    if newid in container:
        raise DuplicationError("name, %s, is already in use" % newid)

    if mover.moveable() and mover.moveableTo(container, newid):
        mover.moveTo(container, newid)
