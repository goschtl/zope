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
"""Stateful cookie tree

$Id: cookie.py,v 1.3 2004/03/05 22:09:20 jim Exp $
"""

from zope.app import zapi
from zope.app.folder.interfaces import IFolder
from zope.app.interfaces.services.service import ISite, ISiteManager
from zope.app.interfaces.traversing import IContainmentRoot

from zope.app.tree.filters import OnlyInterfacesFilter
from zope.app.tree.browser import StatefulTreeView

class CookieTreeView(StatefulTreeView):
    """A stateful tree view using cookies to remember the tree state
    """

    request_variable = 'tree-state'

    def cookieTree(self, root=None, filter=None):
        """Build a tree with tree state information from a request.
        """
        request = self.request
        tree_state = request.get(self.request_variable, "")
        tree_state = str(tree_state)
        tree_state = tree_state or None
        if tree_state is not None:
            # set a cookie right away
            request.response.setCookie(self.request_variable,
                                       tree_state)
        return self.statefulTree(root, filter, tree_state)

    def folderTree(self, root=None):
        """Cookie tree with only folders (and site managers).
        """
        filter = OnlyInterfacesFilter(IFolder, ISiteManager)
        return self.cookieTree(root, filter)

    def siteTree(self):
        """Cookie tree with only folders and the nearest site as root
        node.
        """
        parent = self.context
        for parent in zapi.getParents(self.context):
            if ISite.providedBy(parent):
                break
        return self.folderTree(parent)

    def rootTree(self):
        """Cookie tree with only folders and the root container as
        root node.
        """
        root = zapi.getRoot(self.context)
        return self.folderTree(root)
