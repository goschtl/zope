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
"""Static tree interfaces

$Id: interfaces.py,v 1.1 2004/01/16 12:39:00 philikon Exp $
"""

from zope.interface import Interface, Attribute
from zope.schema import Bool, Int

class IUniqueId(Interface):
    """Interface that promises to return a unique id within a
    tree.

    Problem: How are implementing objects (most probably adapters)
    supposed to know, whether their id is unique in the context? Well,
    they just have to be damn sure that they are unique.
    """

    def getId():
        """Return a string containing a unique id within a tree
        """

class IChildObjects(Interface):
    """Interface providing methods to retrieve child objects so they
    can be wrapped in tree nodes.
    """

    def hasChildren():
        """Return true if child objects are available
        """

    def getChildObjects():
        """Return a sequence of child objects
        """

class INode(IUniqueId, IChildObjects):
    """A node in the tree
    """

    context = Attribute("""
        The object that is being wrapped.
        """)

    depth = Int(
        title=u"Depth",
        description=u"The positional depth of this node in the tree.",
        )

    expanded = Bool(
        title=u"Expanded",
        description=u"True if this node is expanded.",
        )

    def expand(recursive=False):
        """Expand this node.

        'recursive' can be set to True to expand all child nodes as
        well
        """

    def collapse():
        """Collapse this node.
        """

    def getChildNodes():
        """Return a sequence of children nodes if the node is expanded.
        """

    def getFlatNodes():
        """Return a flat list of nodes in the tree. Children of
        expanded nodes are shown.
        """

    def getFlatDicts():
        """Return a tuple:

          1st element: flat list of dictinaries containing nodes in
          the tree and extra information (depth, toggled tree
          state). Children of expanded nodes are shown.

          2nd element: maximum depth
        """

class ITreeStateEncoder(Interface):
    """This utility can encode and decode the ids of expended nodes
    """

    def encodeTreeState(expanded_nodes):
        """Encode the tree expansion information in 'expanded_nodes'.
        """

    def decodeTreeState(tree_state):
        """Decode the tree expansion information 'tree_state'.
        """
