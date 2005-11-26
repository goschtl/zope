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
"""Tutorial Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import os
import zope.component
import zope.interface

from zope.tutorial import interfaces

class Tutorial(object):
    """Tutorial"""
    zope.interface.implements(interfaces.ITutorial)

    def __init__(self, title, path):
        self.title = title
        self.path = path

    def __repr__(self):
        return '<%s title=%r, file=%r>' %(
            self.__class__.__name__, self.title, os.path.split(self.path)[-1])
