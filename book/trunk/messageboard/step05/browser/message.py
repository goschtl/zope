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
"""Browser Views for IMessage

$Id: message.py,v 1.3 2003/12/13 17:24:36 srichter Exp $
"""
from zope.app import zapi
from zope.app.dublincore.interfaces import ICMFDublinCore

from book.messageboard.interfaces import IMessage


class MessageDetails:

    def author(self):
        """Get user who last modified the Message."""
        creators = ICMFDublinCore(self.context).creators
        if not creators:
            return 'unknown'
        return creators[0]

    def modified(self):
        """Get last modification date."""
        date = ICMFDublinCore(self.context).modified
        if date is None:
            date = ICMFDublinCore(self.context).created
        if date is None:
            return ''
        return date.strftime('%d/%m/%Y %H:%M:%S')

    def parent_info(self):
        """Get the parent of the message"""
        parent = zapi.getParent(self.context)
        if not IMessage.providedBy(parent):
            return None
        return {'name': zapi.name(parent), 'title': parent.title}
