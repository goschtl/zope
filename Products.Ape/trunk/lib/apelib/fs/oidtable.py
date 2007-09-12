##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""OIDTable class.

$Id$
"""

class OIDTable:
    """Table of (parent_oid, filename, child_oid).

    The oid and filename columns form the primary key.  Maintains an index
    on the child_oid column to allow fast reverse lookups.
    """

    def __init__(self):
        self.fwd = {}  # { parent_oid : {filename : child_oid} }
        self.back = {}  # { child_oid : [(parent_oid, filename)] }

    def add(self, parent_oid, filename, child_oid):
        """Adds an association from a parent and filename to a child.
        """
        d = self.fwd.get(parent_oid)
        if d is None:
            d = {}
            self.fwd[parent_oid] = d
        if d.has_key(filename):
            if d[filename] != child_oid:
                raise KeyError(
                    "'%s' already has a child named '%s', with OID '%s'"
                    % (parent_oid, filename, d[filename]))
        else:
            d[filename] = child_oid
        p = self.back.get(child_oid)
        key = (parent_oid, filename)
        if p is None:
            p = [key]
            self.back[child_oid] = p
        elif key not in p:
            p.append(key)

    def remove(self, parent_oid, filename):
        """Removes an association between a parent and a child.
        """
        d = self.fwd.get(parent_oid)
        if not d:
            return
        child_oid = d.get(filename)
        if not child_oid:
            return
        del d[filename]
        if not d:
            del self.fwd[parent_oid]
        p = self.back.get(child_oid)
        key = (parent_oid, filename)
        if key in p:
            p.remove(key)
        if not p:
            del self.back[child_oid]

    def set_children(self, parent_oid, new_children):
        """Updates all children for a parent.

        new_children is {filename: child_oid}.  Calls self.add() and
        self.remove() to make all changes.
        """
        old_children = self.fwd.get(parent_oid)
        if old_children is not None:
            # The dictionary in the table will change as children are
            # added/removed, so make a copy.
            old_children = old_children.copy()
        else:
            old_children = {}
        for filename, child_oid in new_children.items():
            if old_children.has_key(filename):
                if old_children[filename] != child_oid:
                    # Change this child to a new OID.
                    self.remove(parent_oid, filename)
                    self.add(parent_oid, filename, child_oid)
                del old_children[filename]
            else:
                # Add a new child.
                self.add(parent_oid, filename, child_oid)
        # Remove the filenames left over in old_children.
        for filename, child_oid in old_children.items():
            self.remove(parent_oid, filename)

    def get_path(self, ancestor_oid, descendant_oid):
        """Returns the primary path that connects two OIDs.

        The primary path follows the first parent of each OID.
        """
        parts = []
        back_get = self.back.get
        parts_append = parts.append
        oid = descendant_oid
        while oid != ancestor_oid:
            p = back_get(oid)
            if not p:
                # The primary lineage doesn't reach the ancestor.
                return None
            # Follow only the first parent.
            oid, filename = p[0]
            if oid == descendant_oid:
                # Circular OID chain.
                return None
            parts_append(filename)
        parts.reverse()
        return parts

    def get_children(self, parent_oid):
        """Returns the children of an OID as a mapping of {filename: oid}.

        Do not modify the return value.
        """
        return self.fwd.get(parent_oid)

    def get_parents(self, child_oid):
        """Returns the parents of an OID as a list of (oid, filename).

        Do not modify the return value.
        """
        return self.back.get(child_oid)
