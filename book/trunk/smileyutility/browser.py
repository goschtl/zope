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
"""Local Smiley Theme Browser components

$Id$
"""
__docformat__ = 'restructuredtext'
from zope.app import zapi

from localtheme import queryNextTheme, getURL

class Overview(object):

    def getLocalSmileys(self):
        return [{'text': name, 'url': getURL(smiley, self.request)}
                for name, smiley in self.context.items()]
    
    def getAcquiredSmileys(self):
        theme = queryNextTheme(self.context, zapi.name(self.context))
        map = theme.getSmileysMapping(self.request)
        return [{'text': name, 'url': path} for name, path in map.items()
                if name not in self.context]
