##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
__docformat__ = "reStructuredText"

import persistent
import zope.interface
import zope.schema
from zope.schema import fieldproperty
from zope.security import checker
from zope.app import annotation
from zope.app import container
from zope.webdev import interfaces


class ContentComponentDefinition(persistent.Persistent,
                                 container.contained.Contained):
    """Content Component Definition

    A persistent implementation of a content component definition. It can be
    used to create content components on local sites.
    """
    zope.interface.implements(interfaces.IContentComponentDefinition)

    def __init__(self, name=u'', schema=None):
        self.name = name
        self.schema = schema
        self.permissions = persistent.dict.PersistentDict()

    def __call__(self, **kwargs):
        """See interfaces.IContentComponentDefinition"""
        instance = ContentComponentInstance(self)
        # We do not want to update the isntance dictionary directly, since we
        # want to use the ``__setattr__`` method to ensure that only supported
        # attributes are set.
        for key, value in kwargs.items():
            setattr(instance, key, value)
        return instance

    def __repr__(self):
        # If it is added to a package, make it part of the name
        if self.__parent__:
            name = self.__parent__.__name__ + '.' + self.name
        else:
            name = self.name
        return '<%s %r>' %(self.__class__.__name__, name)


class ContentComponentInstance(persistent.Persistent,
                               container.contained.Contained):
    """Content Component Instance

    An object that acts as an instance of a content component definition.
    """
    zope.interface.implements(interfaces.IContentComponentInstance,
                              annotation.interfaces.IAttributeAnnotatable)

    def __init__(self, definition):
        super(ContentComponentInstance, self).__init__()
        # See interfaces.IContentComponentInstance
        self.__definition__ = definition
        # Update the instance
        self.__update__()

    def __update__(self):
        """See interfaces.IContentComponentInstance"""
        schema = self.__definition__.schema

        # Make sure the instance provides the schema.
        zope.interface.directlyProvides(self, schema)

        # Add the new attributes
        for name, field in zope.schema.getFields(schema).items():
            # Only set the field to the default value, if it is not already set
            if not hasattr(self, name):
                setattr(self, name, field.default)

        # Build up Checker rules
        checker_getattr = {}
        checker_setattr = {}
        permissions = self.__definition__.permissions
        for name in zope.schema.getFields(schema):
            get_perm, set_perm = permissions.get(name, (None, None))
            checker_getattr[name] = get_perm or checker.CheckerPublic
            checker_setattr[name] = set_perm or checker.CheckerPublic

        # Store the checker in an attribute that is recognized by the security
        # framework.
        self.__Security_checker__ = checker.Checker(
            checker_getattr, checker_setattr)


    def __repr__(self):
        return '<Instance of %r>' %self.__definition__
