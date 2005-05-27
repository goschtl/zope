##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Copy, Paste and Move support for content components

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements, Invalid
from zope.exceptions import NotFoundError, DuplicationError

from zope.app import zapi
from zope.app.container.sample import SampleContainer
from zope.event import notify
from zope.app.event.objectevent import ObjectCopiedEvent
from zope.app.copypastemove.interfaces import IObjectMover
from zope.app.copypastemove.interfaces import IObjectCopier
from zope.app.location.pickling import locationCopy
from zope.app.container.interfaces import INameChooser
from zope.app.container.constraints import checkObject

class ObjectMover(object):
    """Adapter for moving objects between containers

    To use an object mover, pass a contained `object` to the class.
    The contained `object` should implement `IContained`.  It should be
    contained in a container that has an adapter to `INameChooser`.


    >>> from zope.app.container.contained import Contained
    >>> ob = Contained()
    >>> container = ExampleContainer()
    >>> container[u'foo'] = ob
    >>> mover = ObjectMover(ob)

    In addition to moving objects, object movers can tell you if the
    object is movable:

    >>> mover.moveable()
    1

    which, at least for now, they always are.  A better question to
    ask is whether we can move to a particular container. Right now,
    we can always move to a container of the same class:

    >>> container2 = ExampleContainer()
    >>> mover.moveableTo(container2)
    1
    >>> mover.moveableTo({})
    Traceback (most recent call last):
    ...
    TypeError: Container is not a valid Zope container.

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
    TypeError: Container is not a valid Zope container.


    Do a test for preconditions:

    >>> import zope.interface
    >>> import zope.schema
    >>> def preNoZ(container, name, ob):
    ...     "Silly precondition example"
    ...     if name.startswith("Z"):
    ...         raise zope.interface.Invalid("Invalid name.")

    >>> class I1(zope.interface.Interface):
    ...     def __setitem__(name, on):
    ...         "Add an item"
    ...     __setitem__.precondition = preNoZ

    >>> from zope.app.container.interfaces import IContainer
    >>> class C1(object):
    ...     zope.interface.implements(I1, IContainer)
    ...     def __repr__(self):
    ...         return 'C1'

    >>> from zope.app.container.constraints import checkObject
    >>> container3 = C1()
    >>> mover.moveableTo(container3, 'ZDummy')
    0
    >>> mover.moveableTo(container3, 'newName')
    1

    And a test for constraints:

    >>> def con1(container):
    ...     "silly container constraint"
    ...     if not hasattr(container, 'x'):
    ...         return False
    ...     return True
    ...
    >>> class I2(zope.interface.Interface):
    ...     __parent__ = zope.schema.Field(constraint = con1)
    ...
    >>> class constrainedObject(object):
    ...     zope.interface.implements(I2)
    ...     def __init__(self):
    ...         self.__name__ = 'constrainedObject'
    ...
    >>> cO = constrainedObject()
    >>> mover2 = ObjectMover(cO)
    >>> mover2.moveableTo(container)
    0
    >>> container.x = 1
    >>> mover2.moveableTo(container)
    1

    """

    implements(IObjectMover)

    def __init__(self, object):
        self.context = object
        self.__parent__ = object # TODO: see if we can automate this

    def moveTo(self, target, new_name=None):
        '''Move this object to the `target` given.

        Returns the new name within the `target`
        Typically, the `target` is adapted to `IPasteTarget`.'''

        obj = self.context
        container = obj.__parent__

        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name

        checkObject(target, new_name, obj)

        if target is container and new_name == orig_name:
            # Nothing to do
            return

        chooser = INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)

        target[new_name] = obj
        del container[orig_name]

    def moveable(self):
        '''Returns ``True`` if the object is moveable, otherwise ``False``.'''
        return True

    def moveableTo(self, target, name=None):
        '''Say whether the object can be moved to the given target.

        Returns ``True`` if it can be moved there. Otherwise, returns
        ``False``.
        '''
        if name is None:
            name = self.context.__name__
        try:
            checkObject(target, name, self.context)
        except Invalid:
            return False
        return True

class ObjectCopier(object):
    """Adapter for copying objects between containers

    To use an object copier, pass a contained `object` to the class.
    The contained `object` should implement `IContained`.  It should be
    contained in a container that has an adapter to `INameChooser`.

    >>> from zope.app.container.contained import Contained
    >>> ob = Contained()
    >>> container = ExampleContainer()
    >>> container[u'foo'] = ob
    >>> copier = ObjectCopier(ob)

    In addition to moving objects, object copiers can tell you if the
    object is movable:

    >>> copier.copyable()
    1

    which, at least for now, they always are.  A better question to
    ask is whether we can copy to a particular container. Right now,
    we can always copy to a container of the same class:

    >>> container2 = ExampleContainer()
    >>> copier.copyableTo(container2)
    1
    >>> copier.copyableTo({})
    Traceback (most recent call last):
    ...
    TypeError: Container is not a valid Zope container.

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
    TypeError: Container is not a valid Zope container.

    Do a test for preconditions:

    >>> import zope.interface
    >>> import zope.schema
    >>> def preNoZ(container, name, ob):
    ...     "Silly precondition example"
    ...     if name.startswith("Z"):
    ...         raise zope.interface.Invalid("Invalid name.")

    >>> class I1(zope.interface.Interface):
    ...     def __setitem__(name, on):
    ...         "Add an item"
    ...     __setitem__.precondition = preNoZ

    >>> from zope.app.container.interfaces import IContainer
    >>> class C1(object):
    ...     zope.interface.implements(I1, IContainer)
    ...     def __repr__(self):
    ...         return 'C1'

    >>> from zope.app.container.constraints import checkObject
    >>> container3 = C1()
    >>> copier.copyableTo(container3, 'ZDummy')
    0
    >>> copier.copyableTo(container3, 'newName')
    1

    And a test for constraints:

    >>> def con1(container):
    ...     "silly container constraint"
    ...     if not hasattr(container, 'x'):
    ...         return False
    ...     return True
    ...
    >>> class I2(zope.interface.Interface):
    ...     __parent__ = zope.schema.Field(constraint = con1)
    ...
    >>> class constrainedObject(object):
    ...     zope.interface.implements(I2)
    ...     def __init__(self):
    ...         self.__name__ = 'constrainedObject'
    ...
    >>> cO = constrainedObject()
    >>> copier2 = ObjectCopier(cO)
    >>> copier2.copyableTo(container)
    0
    >>> container.x = 1
    >>> copier2.copyableTo(container)
    1

    """

    implements(IObjectCopier)

    def __init__(self, object):
        self.context = object
        self.__parent__ = object # TODO: see if we can automate this

    def copyTo(self, target, new_name=None):
        """Copy this object to the `target` given.

        Returns the new name within the `target`, or ``None``
        if the target doesn't do names.
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

        checkObject(target, new_name, obj)

        chooser = INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)

        copy = locationCopy(obj)
        self._configureCopy(copy, target, new_name)
        notify(ObjectCopiedEvent(copy))

        target[new_name] = copy

    def _configureCopy(self, copy, target, new_name):
        """Configures the copied object before it is added to `target`.
        
        `target` and `new_name` are provided as additional information.
        
        By default, `copy.__parent__` and `copy.__name__` are set to ``None``.
        
        Subclasses may override this method to perform additional
        configuration of the copied object.
        """
        copy.__parent__ = copy.__name__ = None

    def copyable(self):
        '''Returns True if the object is copyable, otherwise False.'''
        return True

    def copyableTo(self, target, name=None):
        '''Say whether the object can be copied to the given `target`.

        Returns ``True`` if it can be copied there. Otherwise, returns
        ``False``.
        '''
        if name is None:
            name = self.context.__name__
        try:
            checkObject(target, name, self.context)
        except Invalid:
            return False
        return True


class PrincipalClipboard(object):
    '''Principal clipboard

    Clipboard information consists on tuples of
    ``{'action':action, 'target':target}``.
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
        return self.context.get('clipboard', ())


def rename(container, oldid, newid):
    object = container.get(oldid)
    if object is None:
        raise NotFoundError(container, oldid)
    mover = IObjectMover(object)

    if newid in container:
        raise DuplicationError("name, %s, is already in use" % newid)

    if mover.moveable() and mover.moveableTo(container, newid):
        mover.moveTo(container, newid)

class ExampleContainer(SampleContainer):
    # Sample container used for examples in doc stringss in this module

    implements(INameChooser)

    def chooseName(self, name, ob):
       while name in self:
          name += '_'
       return name
