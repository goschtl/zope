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
"""

Revision information: $Id: Contents.py,v 1.2 2002/06/10 23:27:56 jim Exp $
"""


import os

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.App.OFS.Container.IContainer import IContainer

class Contents(BrowserView):

    __used_for__ = IContainer

    def _extractContentInfo( self, item ):
        info = {}
        info['id'] = item[0]
        info['object'] = item[1]

        # XXX:  We will fake this stuff out for now
        info[ 'title' ] = info[ 'url' ] = item[0]
        info['icon'] = None

        return info


    def removeObjects(self, ids, REQUEST=None):
        """ """
        for id in ids:
            self.remove(id)

        # XXX:  This is horribly broken, but I can't do better until
        #       we have a way to compute absolute URLs.
        if REQUEST is not None:
            # for unit tests
            REQUEST.getResponse().redirect(REQUEST.URL['-1'])
        return self.confirmRemoved()
    

    def remove( self, name, silent=0 ):
        """
            Remove the object stored under 'name', or raise a KeyError
            if no such object (pass non-zero 'silent' to suppress the
            exception).
        """
        try:
            del self.context[name]
        except KeyError:
            if not silent:
                raise
        return self.confirmRemoved( name=name )

    def listContentInfo(self):
        return map(self._extractContentInfo, self.context.items())

    index = ViewPageTemplateFile('main.pt')
    confirmRemoved = ViewPageTemplateFile('remove_confirmed.pt')

