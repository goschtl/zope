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
"""Browser views

$Id: browser.py,v 1.2 2004/01/16 14:17:01 philikon Exp $
"""

from zope.app import zapi
from zope.app.publisher.browser import BrowserView
from zope.app.interfaces.content.folder import IFolder
from zope.app.interfaces.services.service import ISite, ISiteManager
from zope.app.interfaces.traversing import IContainmentRoot

from interfaces import ITreeStateEncoder
from node import Node
from filters import OnlyInterfacesFilter

class StaticTreeView(BrowserView):

    request_variable = 'tree-state'

    def cookieTree(self, root=None, filter=None):
        """Build a tree with tree state information from a request.
        """
        if root is None:
            root = self.context
        request = self.request
        expanded_nodes = []
        tree_state = request.get(self.request_variable, "")
        tree_state = str(tree_state)
        if tree_state:
            # set a cookie right away
            request.response.setCookie(self.request_variable,
                                       tree_state)
            encoder = zapi.getUtility(root, ITreeStateEncoder)
            expanded_nodes = encoder.decodeTreeState(tree_state)
        node = Node(root, expanded_nodes, filter)
        node.expand()
        return node

    def folderCookieTree(self, root=None):
        """Cookie tree with only folders (and site managers).
        """
        filter = OnlyInterfacesFilter(IFolder, ISiteManager)
        return self.cookieTree(root, filter)

    def siteCookieTree(self):
        """Cookie tree with only folders and the nearest site as root
        node.
        """
        parent = self.context
        for parent in zapi.getParents(self.context):
            if ISite.isImplementedBy(parent):
                break
        return self.folderCookieTree(parent)

    def rootCookieTree(self):
        """Cookie tree with only folders and the root container as
        root node.
        """
        root = zapi.getRoot(self.context)
        return self.folderCookieTree(root)
