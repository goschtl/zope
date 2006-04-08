##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""
$Id$
"""
import sys
from zope.event import notify
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.interface import implementedBy
from zope.interface.declarations import Declaration

from zope.generic.directlyprovides.event import DirectlyProvidesModifiedEvent
from zope.generic.directlyprovides.helper import assertListOfInterfaces
from zope.generic.directlyprovides.helper import updateDirectlyProvided

_marker = object()


def hack_checker(value, length, inst):
    from zope.interface.declarations import Declaration
    flattened = [i for i in value.flattened()]

    # precondition for the hack checker
    for iface in implementedBy(inst.__class__):
        if iface in flattened:
            return True

    iterated = [i for i in value]
    if not flattened[0:length] == iterated[0:length]:
        declaration = Declaration(*iterated)
        if [i for i in declaration.flattened()][0:length] == flattened[0:length]:
            return True
        else:
            return False
    return True


class ProvidesProperty(object):
    """Prepend the values of the declared names to the directly provided interfaces."""

    def __init__(self, *names):
        self.__names = names

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = inst.__dict__.get('__provides__', _marker)
        if value is _marker:
            raise AttributeError('__provides__')

        return value

    def __set__(self, inst, value):
        # remove a provides declaration
        if value is None:
            if '__provides__' in inst.__dict__:
                del inst.__dict__['__provides__']

        # evaluate interfaces that should be prepended
        prepended = self._evaluatePrepended(inst)

        if value:
            ifaces = list(value)
        else:
            ifaces = []

        is_ok = (len(ifaces) >= len(prepended) and ifaces[0:len(prepended)] == prepended)

        # XXX: An exception that I do not understand???
        # Problem if a interface is directly provided by the regular mechanism
        # and afterward is set by our mechanism
        if is_ok and not hack_checker(value, len(prepended), inst):
            directlyProvides(inst)
            directlyProvides(inst, *ifaces)

        # everything prepended correctly   
        elif is_ok:
            if list(Declaration(value.__bases__[:-1])) != list(directlyProvidedBy(inst)):
                value.changed()
                inst.__dict__['__provides__'] = value
                
                notify(DirectlyProvidesModifiedEvent(inst))

        # order the interfaces first
        elif len(ifaces) > 0:
            # remove duplicates
            for iface in prepended:
                while iface in ifaces:
                    ifaces.remove(iface)
            
            for iface in implementedBy(inst.__class__):
                while iface in ifaces:
                    ifaces.remove(iface)

            # put pretended and other interfaces together and asign it again
            ordered = prepended + ifaces
            directlyProvides(inst, *ordered)

        # no other directly provided interface
        else:
            directlyProvides(inst, *prepended)

    def _evaluatePrepended(self, inst):
        prependes = []
        for name in self.__names:
            for iface in assertListOfInterfaces(getattr(inst, name)):
                if iface not in prependes:
                    prependes.append(iface)

        return prependes



def provides(*names):
    """Declare the attributes which should be asserted by the directly provided mechnism.

    This is used within a class suite defining an attribute __provides__:

        >>> from zope.interface import Interface
        >>> class IFoo(Interface):
        ...     pass

        >>> class Bar(object):
        ...     provides('foo')
        ...     foo = IFoo

        >>> Bar.__provides__._ProvidesProperty__names
        ('foo',)

    It is invalid to call contains outside a class suite:

        >>> provides('foo')
        Traceback (most recent call last):
        ...
        TypeError: provides not called from suite

    Each time when attribute __provides__ is set an directly provides event
    is notified:

        >>> from zope.app.testing import placelesssetup
        >>> placelesssetup.setUp()
    
        >>> from zope.app.event.tests.placelesssetup import events
        >>> from zope.interface import directlyProvidedBy

        >>> class IA(Interface):
        ...     pass

        >>> len(events)
        0

        >>> bar = Bar()
        >>> directlyProvides(bar, IA)
        
        >>> len(events)
        1
        >>> events.pop() # doctest: +ELLIPSIS
        <zope.generic.directlyprovides.event.DirectlyProvidesModifiedEvent...>

        >>> placelesssetup.tearDown()
    """

    frame = sys._getframe(1)
    f_locals = frame.f_locals
    f_globals = frame.f_globals

    if not (f_locals is not f_globals
            and f_locals.get('__module__')):
        raise TypeError('provides not called from suite')

    f_locals['__provides__'] = ProvidesProperty(*names)



class UpdateProvides(object):
    """Update the provides attribute after a new value is set.
    
    Note that UpdateProvides cannot be used with slots. They can only
    be used for attributes stored in instance dictionaries.
    """

    def __init__(self, field, before=None, after=None, value_hook=None, ):
        self.__field = field
        self.__name = field.__name__
        self.__before = before
        self.__after = after
        self.__value_hook = value_hook

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = inst.__dict__.get(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                value = getattr(field, 'missing_value', _marker)

                if value is _marker:
                    raise AttributeError(self.__name)

        return value

    def __set__(self, inst, value):

        previous_value = getattr(inst, self.__name)

        # hook to rearrange values -> ordered features
        if self.__value_hook:
            value = self.__value_hook(inst, value, previous_value)

        if value != previous_value:
            # validate the value
            field = self.__field.bind(inst)
            field.validate(value)

            # invoke before
            if self.__before:
                self.__before(inst, value, previous_value)

            # store value within __dict__
            if value is not getattr(field, 'missing_value', _marker):
                inst.__dict__[self.__name] = value
            else:
                if self.__name in inst.__dict__:
                    del inst.__dict__[self.__name]

            # update directly provides
            updateDirectlyProvided(inst, value, previous_value)

            # invoke after
            if self.__after:
                self.__after(inst, value, previous_value)

    def __getattr__(self, name):
        return getattr(self.__field, name)
