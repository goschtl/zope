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
"""Define adder component for folders.

$Id: Adder.py,v 1.3 2002/06/18 14:47:02 jim Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.ComponentArchitecture import createObject
from Zope.App.OFS.Services.AddableService import getAddableContent
from Zope.App.OFS.Container.Exceptions import DuplicateIDError
from Zope.Proxy.ProxyIntrospection import removeAllProxies

class ContainerAdder(BrowserView):

    def _listAddables( self ):
        """
            Derived classes override this to change the registry
            in which factories are looked up.
        """
        return getAddableContent(self.context)

    def listAddableInfo( self ):
        """
            Return a sequence of mappings for the addables for our
            folder.
        """
        return self._listAddables()

    def action( self, id, type_name, REQUEST=None):
        """
            Instantiate an object and put it in our folder.
        """
        context = self.context
        
        if id in context.keys():
            raise DuplicateIDError, "ID '%s' already in use." % id

        # Create the new object
        new_object = createObject(context, type_name)

        # Remove thye security proxy and context wrappers, if any.
        # It's a good thing this is trusted code. :)
        new_object = removeAllProxies(new_object)

        context.setObject(id, new_object)

        if REQUEST is not None:
            # for unit tests
            REQUEST.response.redirect(REQUEST.URL[-1])

        return self.confirmed( type_name=type_name, id=id )

    index = ViewPageTemplateFile('add.pt')
    confirmed = ViewPageTemplateFile('add_confirmed.pt')
