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
import warnings
from Products.Five.security import CheckerPublic, protectName
from Globals import InitializeClass as initializeClass
import zope.app.component.contentdirective

class ClassDirective(zope.app.component.contentdirective.ClassDirective):
        
    def __protectName(self, name, permission_id):
        self.__context.action(
            discriminator = ('five:protectName', self.__class, name),
            callable = protectName,
            args = (self.__class, name, permission_id)
            )

    def __call__(self):
        """Handle empty/simple declaration."""
        return self.__context.action(
            discriminator = ('five:initialize:class', self.__class),
            callable = initializeClass,
            args = (self.__class,)
            )

# BBB 2006/02/24, to be removed after 12 months
class ContentDirective(ClassDirective):

    def __init__(self, _context, class_):
        warnings.warn_explicit(
            "The 'content' alias for the 'class' directive has been "
            "deprecated and will be removed in Zope 2.12.\n",
            DeprecationWarning, _context.info.file, _context.info.line)        
        super(ContentDirective, self).__init__(_context, class_)
