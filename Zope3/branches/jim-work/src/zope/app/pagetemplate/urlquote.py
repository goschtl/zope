##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""URL quoting for ZPT

$Id: simpleviewclass.py 25177 2004-06-02 13:17:31Z jim $
"""

import urllib
from zope.interface import implements
from zope.app.traversing.interfaces import IPathAdapter

class URLQuote(object):

    __used_for__ = basestring
    implements(IPathAdapter)

    def __init__(self, context):
        if not isinstance(context, basestring):
            context = str(context)
        self.context = context

    def quote(self):
        """Return the objects URL quote representation."""
        return urllib.quote(self.context)

    def quote_plus(self):
        """Return the objects URL quote_plus representation."""
        return urllib.quote_plus(self.context)

    def unquote(self):
        """Return the objects URL unquote representation."""
        return urllib.unquote(self.context)

    def unquote_plus(self):
        """Return the objects URL unquote_plus representation."""
        return urllib.unquote_plus(self.context)

