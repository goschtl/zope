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
"""Contact

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface

from zf.zscp import interfaces

class Contact(object):
    """Contact Implementation"""
    zope.interface.implements(interfaces.IContact)

    name = None
    email = None

    def __repr__(self):
        return "<%s '%s <%s>'>" % (
            self.__class__.__name__, self.name, self.email)
