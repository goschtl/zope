##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Component location field.

$Id: field.py,v 1.7 2003/03/13 17:10:37 gvanrossum Exp $
"""
__metaclass__ = type

from zope.schema import Field
from zope.schema.interfaces import ValidationError
from zope.app.traversing import traverse
from zope.exceptions import NotFoundError
from zope.app.interfaces.services.field import IComponentPath
from zope.app.interfaces.services.field import IComponentLocation
from zope.component import getServiceManager, getAdapter
from zope.app.interfaces.services.module import IModuleService

class ComponentPath(Field):

    __implements__ = IComponentPath

    _type = unicode

    def __init__(self, type, *args, **kw):
        self.type = type
        super(ComponentPath, self).__init__(*args, **kw)

    def _validate(self, value):
        super(ComponentPath, self)._validate(value)

        if not value.startswith('/'):
            raise ValidationError("Not an absolute path", value)

        try:
            component = traverse(self.context, value)
        except NotFoundError:
            raise ValidationError("Path for non-existent object", value)

        if not self.type.isImplementedBy(component):
            raise ValidationError("Wrong component type", value)

class ComponentLocation(Field):

    __implements__ = IComponentLocation

    _type = unicode

    def __init__(self, type, *args, **kw):
        self.type = type
        super(ComponentLocation, self).__init__(*args, **kw)

    def _validate(self, value):
        super(ComponentLocation, self)._validate(value)
        component = locateComponent(value, self.context, self.type)


def locateComponent(location, context, interface=None):
    '''Locate a component by traversal, or by a dotted module name.

    If 'interface' is given, check that the located componenent implements
    the given interface.
    '''
    if location.startswith('/'):
        try:
            component = traverse(context, location)
        except NotFoundError:
            raise ValidationError('Path for non-existent object', location)
    else:
        # Assume location is a dotted module name
        if location.startswith('.'):
            # Catch the error of thinking that this is just like 
            # a leading dot in zcml.
            raise ValidationError(
                    "Module name must not start with a '.'", location)
        # XXX Need to be careful here. Jim was going to look
        #     at whether a checkedResolve method is needed.
        servicemanager = getServiceManager(context)
        resolver = getAdapter(servicemanager, IModuleService)
        try:
            component = resolver.resolve(location)
        except ImportError:
            raise ValidationError("Cannot resolve module name", location)

    if interface is not None and not interface.isImplementedBy(component):
        raise ValidationError(
                'Component must be %s' % interface, location)

    return component
