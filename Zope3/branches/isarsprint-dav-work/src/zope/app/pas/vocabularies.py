##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Simple utility name vocabulary to support the PAS

XXX Need doc/test for this still.
XXX For now this is effectively a placeholder.

$Id$
"""

import zope.interface
import zope.schema.interfaces
from zope.app import zapi

class NameTerm:

    def __init__(self, value):
        self.value = unicode(value)

    def token(self):
        # Return our value as a token.  This is required to be 7-bit
        # printable ascii. We'll use base64
        return self.value.encode('base64')[:-1]
    token = property(token)

    def title(self):
        return self.value
    title = property(title)

class UtilityNames:

    zope.interface.implements(zope.schema.interfaces.IVocabularyTokenized)

    def __init__(self, interface):
        self.interface = interface

    def __contains__(value):
        return zapi.queryUtility(self.interface, value) is not None

    def getQuery():
        pass

    def getTerm(value):
        return NameTerm(value)

    def __iter__():
        for name, ut in zapi.getUtilitiesFor(self.interface):
            return NameTerm(name)

    def __len__():
        """Return the number of valid terms, or sys.maxint."""
        return len(list(zapi.getUtilitiesFor(self.interface)))
    
