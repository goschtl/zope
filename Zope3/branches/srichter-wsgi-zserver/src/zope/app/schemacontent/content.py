##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Content Component Definition and Instance

$Id$
"""
from persistent import Persistent
from persistent.dict import PersistentDict
from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IAdding
from zope.app.component.interfaces.registration import ActiveStatus
from zope.app.container.contained import Contained
from zope.app.component.site import UtilityRegistration
from zope.component.exceptions import ComponentLookupError
from zope.interface import directlyProvides, implements
from zope.schema import getFields
from zope.security.checker import CheckerPublic, Checker, defineChecker
from zope.security.proxy import removeSecurityProxy

from interfaces import IContentComponentDefinition 
from interfaces import IContentComponentInstance


class ContentComponentDefinition(Persistent, Contained):

    implements(IContentComponentDefinition)

    def __init__(self, name=u'', schema=None, copySchema=True):
        self.name = name
        self.schema = schema
        self.copySchema = copySchema
        self.permissions = PersistentDict()


class ContentComponentDefinitionRegistration(UtilityRegistration):
    """Content Component Registration"""

    def activated(self):
        self.component.name = self.name

    def deactivated(self):
        self.component.name = None


class ContentComponentInstance(Persistent):

    implements(IContentComponentInstance)

    def __init__(self, name, schema, schemaPermissions=None):
        super(ContentComponentInstance, self).__init__()

        # Save the name of the object
        self.__name__ = name

        self.__schema = object.__new__(schema.__class__)
        self.__schema.__dict__.update(schema.__dict__)
        # Add the new attributes, if there was a schema passed in
        if schema is not None:
            for name, field in getFields(schema).items():
                setattr(self, name, field.default)
            directlyProvides(self, schema)

            # Build up a Checker rules and store it for later
            if schemaPermissions is None:
                schemaPermissions = {}
            self.__checker_getattr = PersistentDict()
            self.__checker_setattr = PersistentDict()
            for name in getFields(schema):
                get_perm, set_perm = schemaPermissions.get(name, (None, None))
                self.__checker_getattr[name] = get_perm or CheckerPublic
                self.__checker_setattr[name] = set_perm or CheckerPublic

            # Always permit our class's public methods
            self.__checker_getattr['getSchema'] = CheckerPublic


    def __setattr__(self, key, value):
        if (key in ('getSchema',) or
            key.startswith('_p_') or
            key.startswith('__') or
            key.startswith('_ContentComponentInstance__')):
            return super(ContentComponentInstance, self).__setattr__(key,
                                                                     value)

        is_schema_field = self.__schema is not None and \
                          key in getFields(self.__schema).keys()

        if is_schema_field:
            super(ContentComponentInstance, self).__setattr__(key, value)
        else:
            raise AttributeError, 'Attribute "%s" not available' %key


    def getSchema(self):
        return self.__schema


    def __repr__(self):
        return '<ContentComponentInstance called %s>' %self.__name__



def ContentComponentInstanceChecker(instance):
    """A function that can be registered as a Checker in defineChecker()"""
    return Checker(instance.__checker_getattr.get,
                   instance.__checker_setattr.get)

defineChecker(ContentComponentInstance, ContentComponentInstanceChecker)
