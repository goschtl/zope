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

from security import CheckerPublic
from security import protectName, initializeClass

from zope.app.component.contentdirective import ContentDirective as\
     zope_app_ContentDirective

class ContentDirective(zope_app_ContentDirective):

    def require(self, _context,
                permission=None, attributes=None, interface=None,
                like_class=None, set_attributes=None, set_schema=None):
        super(ContentDirective, self).require(
            _context, permission,
            attributes, interface, like_class,
            set_attributes, set_schema)
        if attributes:
            self.__protectNames(attributes, permission)
        
    def __protectName(self, name, permission_id):
        "Set a permission on a particular name."
        self.__context.action(
            discriminator = ('five:protectName', self.__class, name),
            callable = protectName,
            args = (self.__class, name, permission_id)
            )
        
    def __protectNames(self, names, permission_id):
        "Set a permission on a bunch of names."
        for name in names:
            self.__protectName(name, permission_id)
            
    def allow(self, _context, attributes=None, interface=None):
        """Like require, but with permission_id zope.Public"""
        # XXX this is using CheckerPublic while z3 is using
        # PublicPermission
        return self.require(_context, CheckerPublic, attributes, interface)

    def __call__(self):
        "Handle empty/simple declaration."
        return self.__context.action(
            discriminator = ('five:initialize:class', self.__class),
            callable = initializeClass,
            args = (self.__class,)
            )
