##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""An implementation of things that can be registered in a Registry.

$Id: registeredobject.py,v 1.4 2004/03/05 18:37:52 srichter Exp $
"""

from zope.app.interfaces.security import IRegisteredObject
from zope.interface import implements

class RegisteredObject(object):
    implements(IRegisteredObject)

    def __init__(self, id, title, description):
        self._id = id
        self._title = title
        self._description = description

    def getId(self):
        return self._id

    def getTitle(self):
        return self._title

    def getDescription(self):
        return self._description
