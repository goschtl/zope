##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Permissions

$Id$
"""
from persistent import Persistent
from zope.interface import implements
from zope.schema.interfaces import ValidationError
from zope.security.checker import CheckerPublic
from zope.app import zapi
from zope.app.location import Location
from zope.app.security.interfaces import IPermission

from zope.app.i18n import ZopeMessageIDFactory as _
NULL_ID = _('<permission not activated>')

class Permission(object):
    implements(IPermission)

    def __init__(self, id, title="", description=""):
        self.id = id
        self.title = title
        self.description = description


class LocalPermission(Persistent, Location):
    implements(IPermission)

    def __init__(self, title="", description=""):
        self.id = NULL_ID
        self.title = title
        self.description = description


def setIdOnActivation(event):
    """Set the permission id upon registration activation.

    Let's see how this notifier can be used. First we need to create an event
    using the permission instance and a registration stub:

    >>> class Registration:
    ...     def __init__(self, obj, name):
    ...         self.object = obj
    ...         self.name = name
    ...
    ...     def getComponent(self):
    ...         return self.object

    >>> perm1 = LocalPermission('Permission 1', 'A first permission')
    >>> perm1.id
    u'<permission not activated>'
    
    >>> from zope.app.registration import registration 
    >>> event = registration.RegistrationActivatedEvent(
    ...     Registration(perm1, 'perm1'))

    Now we pass the event into this function, and the id of the permission
    should be set to 'perm1'.

    >>> setIdOnActivation(event)
    >>> perm1.id
    'perm1'

    If the function is called and the component is not a local permission,
    nothing is done:

    >>> class Foo:
    ...     id = 'no id'
    >>> foo = Foo()
    >>> event = registration.RegistrationActivatedEvent(
    ...     Registration(foo, 'foo'))
    >>> setIdOnActivation(event)
    >>> foo.id
    'no id'
    """
    perm = event.object.getComponent()
    if isinstance(perm, LocalPermission):
        perm.id = event.object.name


def unsetIdOnDeactivation(event):
    """Unset the permission id up registration deactivation.

    Let's see how this notifier can be used. First we need to create an event
    using the permission instance and a registration stub:

    >>> class Registration:
    ...     def __init__(self, obj, name):
    ...         self.object = obj
    ...         self.name = name
    ...
    ...     def getComponent(self):
    ...         return self.object

    >>> perm1 = LocalPermission('Permission 1', 'A first permission')
    >>> perm1.id = 'perm1'

    >>> from zope.app.registration import registration 
    >>> event = registration.RegistrationDeactivatedEvent(
    ...     Registration(perm1, 'perm1'))

    Now we pass the event into this function, and the id of the permission
    should be set to NULL_ID.

    >>> unsetIdOnDeactivation(event)
    >>> perm1.id
    u'<permission not activated>'

    If the function is called and the component is not a local permission,
    nothing is done:

    >>> class Foo:
    ...     id = 'foo'
    >>> foo = Foo()
    >>> event = registration.RegistrationDeactivatedEvent(
    ...     Registration(foo, 'foo'))
    >>> unsetIdOnDeactivation(event)
    >>> foo.id
    'foo'
    """
    perm = event.object.getComponent()
    if isinstance(perm, LocalPermission):
        perm.id = NULL_ID


def checkPermission(context, permission_id):
    """Check whether a given permission exists in the provided context.

    >>> from zope.app.tests.placelesssetup import setUp, tearDown
    >>> setUp()

    >>> from zope.app.tests.ztapi import provideUtility
    >>> provideUtility(IPermission, Permission('x'), 'x')

    >>> checkPermission(None, 'x')
    >>> checkPermission(None, 'y')
    Traceback (most recent call last):
    ...
    ValueError: ('Undefined permission id', 'y')

    >>> tearDown()
    """
    if permission_id is CheckerPublic:
        return
    if not zapi.queryUtility(IPermission, permission_id, context=context):
        raise ValueError("Undefined permission id", permission_id)

def allPermissions(context=None):
    """Get the ids of all defined permissions

    >>> from zope.app.tests.placelesssetup import setUp, tearDown
    >>> setUp()

    >>> from zope.app.tests.ztapi import provideUtility
    >>> provideUtility(IPermission, Permission('x'), 'x')
    >>> provideUtility(IPermission, Permission('y'), 'y')

    >>> ids = list(allPermissions(None))
    >>> ids.sort()
    >>> ids
    [u'x', u'y']

    >>> tearDown()
    """
    for id, permission in zapi.getUtilitiesFor(IPermission, context):
        if id != u'zope.Public':
            yield id
