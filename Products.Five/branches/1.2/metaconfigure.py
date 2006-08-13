##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Generic Components ZCML Handlers

$Id$
"""
from types import ModuleType

from zope.interface import classImplements
from zope.configuration.exceptions import ConfigurationError
from zope.app.component import contentdirective
from Products.Five.security import protectName, initializeClass

class ContentDirective(contentdirective.ContentDirective):

    def __init__(self, _context, class_):
        self.__class = class_
        if isinstance(self.__class, ModuleType):
            raise ConfigurationError('Content class attribute must be a class')
        self.__context = _context

    def __protectName(self, name, permission_id):
        "Set a permission on a particular name."
        self.__context.action(
            discriminator = ('five:protectName', self.__class, name),
            callable = protectName,
            args = (self.__class, name, permission_id)
            )

    def __protectSetAttributes(self, attributes, permissions):
        raise ConfigurationError('set_attributes parameter not supported.')

    def __proctectSetSchema(self, schema, permission):
        raise ConfigurationError('set_schema parameter not supported.')

    def __mimic(self, _context, class_):
        raise ConfigurationError('like_class parameter not supported.')

    def __call__(self):
        return self.__context.action(
            discriminator = None,
            callable = initializeClass,
            args = (self.__class,)
            )
