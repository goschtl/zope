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
    Define adder component for folders.
"""
from Zope.ComponentArchitecture import createObject
from Zope.App.OFS.Container.Views.Browser.Adder import ContainerAdder
from Zope.App.OFS.Container.Exceptions import DuplicateIDError

class Adder(ContainerAdder):

    type_name = "Zope.App.OFS.Services.RoleService.Role."

    def _listAddables(self):
        # XXX Hack, but it lets us reuse the page template for now.
        return ()

    def action( self, id, REQUEST=None):
        """
            Instantiate an object and put it in our folder.
        """
        context = self.context
        
        if id in context:
            raise DuplicateIDError, "ID '%s' already in use." % id

        role = createObject(context, self.type_name)
        role.setId(id)

        context.setObject(id, role)

        if REQUEST is not None:
            # for unit tests
            REQUEST.getResponse().redirect(REQUEST.URL['-2'])

        return self.confirmed( type_name="Role", id=id )


