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
"""A node in the treee

$Id: node.py,v 1.1 2004/01/16 12:39:00 philikon Exp $
"""

from zope.interface import implements
from zope.app import zapi

from interfaces import INode, IUniqueId, IChildObjects, \
     ITreeStateEncoder

__metaclass__ = type

class Node:
    """A tree node

    This object represents a node in the tree. It wraps the actual
    object and provides the INode interface to be relied on. In that
    way, it works similar to an adapter.

    This implementation is designed to be as lazy as
    possible. Especially, it will only create child nodes when
    necessary.
    """
    implements(INode)

    __slots__ = (
        'context', 'expanded', 'filter', '_id', '_expanded_nodes',
        '_child_nodes', '_child_objects_adapter',
        )

    def __init__(self, context, expanded_nodes=[], filter=None):
        self.context = context
        self.expanded = False
        self.filter = filter
        self._expanded_nodes = expanded_nodes
        self._id = id = zapi.getAdapter(context, IUniqueId).getId()
        if id in expanded_nodes:
            self.expand()

    def _create_child_nodes(self):
        """Create child nodes and save the result so we don't have
        to create that sequence every time
        """
        nodes = []
        for obj in self.getChildObjects():
            node = Node(obj, self._expanded_nodes, self.filter)
            nodes.append(node)
        self._child_nodes = nodes

    def _get_child_objects_adapter(self):
        """Lazily create the child objects adapter
        """
        if not hasattr(self, '_child_objects_adapter'):
            self._child_objects_adapter = zapi.getAdapter(
                self.context, IChildObjects)
        return self._child_objects_adapter

    def expand(self, recursive=False):
        """See the zope.products.statictree.interfaces.INode interface
        """
        self.expanded = True
        if recursive:
            for node in self.getChildNodes():
                node.expand(True)

    def collapse(self):
        """See the zope.products.statictree.interfaces.INode interface
        """
        self.expanded = False

    def getId(self):
        """See the zope.products.statictree.interfaces.INode interface
        """
        return self._id

    def hasChildren(self):
        """See the zope.products.statictree.interfaces.INode interface
        """
        # we could actually test for the length of the result of
        # getChildObjects(), but we need to watch performance
        return self._get_child_objects_adapter().hasChildren()

    def getChildObjects(self):
        """See the zope.products.statictree.interfaces.INode interface
        """
        filter = self.filter
        children = self._get_child_objects_adapter().getChildObjects()
        if filter:
            return [child for child in children if filter.matches(child)]
        return children
        
    def getChildNodes(self):
        """See the zope.products.statictree.interfaces.INode interface
        """
        if not self.expanded:
            return []
        if not hasattr(self, '_child_nodes'):
            # children nodes are not created until they are explicitly
            # requested through this method
            self._create_child_nodes()
        return self._child_nodes[:]

    def getFlatNodes(self):
        """See the zope.products.statictree.interfaces.INode interface
        """
        nodes = []
        for node in self.getChildNodes():
            nodes.append(node)
            nodes += node.getFlatNodes()
        return nodes

    def getFlatDicts(self, depth=0, maxdepth=0):
        """See the zope.products.statictree.interfaces.INode interface
        """
        nodes = []
        encoder = zapi.getUtility(self.context, ITreeStateEncoder)

        if self.hasChildren() and depth > maxdepth:
            maxdepth = depth

        for node in self.getChildNodes():
            id = node.getId()
            expanded_nodes = self._expanded_nodes[:]
            if id in self._expanded_nodes:
                # if the node is already expanded, the toggle would
                # collapse it
                expanded_nodes.remove(id)
            else:
                # if it isn't expanded, the toggle would expand it
                expanded_nodes += [id]
            flatdict = {
                'depth': depth,
                'node': node,
                'tree-state': encoder.encodeTreeState(expanded_nodes),
                }
            nodes.append(flatdict)
            child_nodes, maxdepth = node.getFlatDicts(depth+1, maxdepth)
            nodes += child_nodes
        return nodes, maxdepth
