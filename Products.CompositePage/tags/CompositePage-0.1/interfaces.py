##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interfaces and exceptions in the CompositePage product.

$Id: interfaces.py,v 1.2 2003/10/01 18:59:31 shane Exp $
"""

from Interface import Interface

class ISlot(Interface):
    """A slot in a composite.
    """

    def single():
        """Renders to a string as a single-element slot.
        """

    def multiple():
        """Renders to a sequence of strings as a multiple-element slot.
        """

    def reorder(name, new_index):
        """Moves an item to a new index.
        """

    def nullify(name):
        """Removes an item from the slot, returning the old item.

        Leaves a null element in its place.  The null element ensures
        that other items temporarily keep their index within the slot.
        """

    def pack():
        """Removes all null elements from the slot.
        """



class CompositeError(Exception):
    """An error in constructing a composite
    """

