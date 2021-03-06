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
"""Package Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.app.container.interfaces import IContained

from zf.zscp import interfaces

class Package(object):
    """Package Implementation."""
    zope.interface.implements(interfaces.IPackage, IContained)

    __parent__ = __name__ = None
    name = None
    publication = None
    releases = None
    certifications = None

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.name)
