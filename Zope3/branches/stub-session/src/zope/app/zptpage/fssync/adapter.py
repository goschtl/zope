##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Filesystem synchronization support.

$Id$
"""

from zope.interface import implements
from zope.fssync.server.entryadapter import ObjectEntryAdapter
from zope.fssync.server.interfaces import IObjectFile

class ZPTPageAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for ZPT page objects.
    """
    implements(IObjectFile)

    def getBody(self):
        return self.context.getSource()

    def setBody(self, data):
        # Convert the data to Unicode, since that's what ZPTPage wants;
        # it's normally read from a file so it'll be bytes.
        # XXX This will die if it's not ASCII.  Guess encoding???
        self.context.setSource(unicode(data))
