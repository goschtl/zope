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
"""Content Object Instance

$Id$
"""
from persistent import Persistent
from persistent.dict import PersistentDict
from zope.interface import directlyProvides, implements, Interface
from zope.schema import getFields, TextLine, Choice
from zope.security.checker import CheckerPublic, Checker, defineChecker


class IContentComponentInstance(Interface):
    """Interface describing a Conten Object Instance"""

    __name__ = TextLine(
        title=u"Name of Content Component Type",
        description=u"""This is the name of the document type.""",
        required=True)

    __schema__ = Choice(
        title=u"Schema",
        description=u"Specifies the schema that characterizes the document.",
        vocabulary="Interfaces",
        required=True)


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
            raise AttributeError, 'Attribute not available'


    def getSchema(self):
        return self.__schema

    def __repr__(self):
        return '<ContentComponentInstance called %s>' %self.__name__


def ContentComponentInstanceChecker(instance):
    """A function that can be registered as a Checker in defineChecker()"""
    return Checker(instance.__checker_getattr.get,
                   instance.__checker_setattr.get)

defineChecker(ContentComponentInstance, ContentComponentInstanceChecker)


