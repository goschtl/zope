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
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.App.ZMI.IGenericCreatorMarker import IGenericCreatorMarker
from Zope.Proxy.ContextWrapper import getWrapperContext
from Zope.App.OFS.Container.Exceptions import DuplicateIDError
from Zope.ComponentArchitecture import createObject

class GenericCreatorView(BrowserView):
    """Provide an interface for editing a contact
    """

    # Assert that we can only be applied to IGenericCreatorMarker
    __used_for__=IGenericCreatorMarker

    # Input form
    index = ViewPageTemplateFile('add.pt', globals())

    # action method
    def action(self, name, REQUEST=None):
        """Create an item of the class identified by the Addable (held
        in _context) within the container that is the parent of the
        Addable"""
        addable=self.context
        container=getWrapperContext(addable)
        
        if name in container:
            raise DuplicateIDError, "ID '%s' already in use." % name

        container.setObject(name, createObject(container, addable.id))

        if REQUEST is not None:
            # for unit tests
            REQUEST.getResponse().redirect(REQUEST.URL[-3])

        return self.confirmed( type_name=addable.id, id=name )

    confirmed = ViewPageTemplateFile('add_confirmed.pt')
