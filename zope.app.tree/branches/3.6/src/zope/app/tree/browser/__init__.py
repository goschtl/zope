##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Browser views

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.component
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import BrowserView

from zope.app.tree.interfaces import ITreeStateEncoder
from zope.app.tree.node import Node

class IStaticTreeLayer(IBrowserRequest):
    """Layer that we can register our own navigation macro for."""

try: # we try not to depend on zope.app.rotterdam hardly
    from zope.app.rotterdam import Rotterdam
    class IStaticTreeSkin(IStaticTreeLayer, Rotterdam):
        """Skin based on Rotterdam that includes the static tree
        navigation macro."""
except ImportError:
    pass

class StatefulTreeView(BrowserView):

    def statefulTree(self, root=None, filter=None, tree_state=None):
        """Build a tree with tree state information from a request.
        """
        if root is None:
            root = self.context
        expanded_nodes = []
        if tree_state is not None:
            encoder = zope.component.getUtility(ITreeStateEncoder)
            expanded_nodes = encoder.decodeTreeState(tree_state)
        node = Node(root, expanded_nodes, filter)
        node.expand()
        return node
