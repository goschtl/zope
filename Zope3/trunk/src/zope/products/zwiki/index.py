##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""A custom Text Index for Wikis

$Id: index.py,v 1.1 2003/12/16 10:05:52 nmurthy Exp $
"""
from zope.app.index.text.index import TextIndex
from zope.products.zwiki.interfaces import IWikiPage

class WikiTextIndex(TextIndex):

    def notify(wrapped_self, event):
        """An event occurred.  Index or unindex the object in response."""
        if IWikiPage.isImplementedBy(event.object):
            super(WikiTextIndex, wrapped_self).notify(event)
            
