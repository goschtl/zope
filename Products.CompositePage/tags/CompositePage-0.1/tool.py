##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Composite tool.

$Id: tool.py,v 1.2 2003/10/01 18:59:31 shane Exp $
"""

import Globals
from Acquisition import aq_base, aq_parent, aq_inner
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.ZopeGuards import guarded_getattr

from interfaces import ISlot, CompositeError


_transformers = {}

def registerTransformer(name, obj):
    """Registers a transformer for use with the composite tool.
    """
    if _transformers.has_key(name):
        raise RuntimeError("There is already a transformer named %s" % name)
    obj._setId(name)
    _transformers[name] = obj



class Transformers(SimpleItem):
    """The container of transformer objects.

    Makes page transformers accessible through URL traversal.
    """

    def __init__(self, id):
        self._setId(id)

    def __getattr__(self, name):
        try:
            return _transformers[name]
        except KeyError:
            raise AttributeError, name



class CompositeTool(SimpleItem):
    """Page composition helper tool.
    """
    meta_type = "Composite Tool"
    id = "composite_tool"

    security = ClassSecurityInfo()

    security.declarePublic("transformers")
    transformers = Transformers("transformers")

    _check_security = 1  # Turned off in unit tests


    security.declarePublic("moveElements")
    def moveElements(self, source_paths, target_path, target_index):
        """Moves elements to a slot.
        """
        target_index = int(target_index)
        # Coerce the paths to sequences of path elements.
        if hasattr(target_path, "split"):
            target_path = target_path.split('/')
        sources = []
        for p in source_paths:
            if hasattr(p, "split"):
                p = p.split('/')
            if p:
                sources.append(p)

        # Ignore descendants when an ancestor is already listed.
        i = 1
        sources.sort()
        while i < len(sources):
            prev = sources[i - 1]
            if sources[i][:len(prev)] == prev:
                del sources[i]
            else:
                i = i + 1

        # Prevent parents from becoming their own descendants.
        for source in sources:
            if target_path[:len(source)] == source:
                raise CompositeError(
                    "Can't make an object a descendant of itself")

        # Gather the sources, replacing with nulls to avoid changing
        # indexes while moving.
        root = self.getPhysicalRoot()
        orig_slots = {}  # id(aq_base(slot)) -> slot
        elements = []
        try:
            for source in sources:
                slot = root.restrictedTraverse(source[:-1])
                assert ISlot.isImplementedBy(slot), repr(slot)
                slot_id = id(aq_base(slot))
                if not orig_slots.has_key(slot_id):
                    orig_slots[slot_id] = slot
                nullify = guarded_getattr(slot, "nullify")  # Check security
                element = nullify(source[-1])
                elements.append(element)

            # Add the elements and reorder.
            slot = root.restrictedTraverse(target_path)
            assert ISlot.isImplementedBy(slot), repr(slot)
            for element in elements:
                if self._check_security:
                    slot._verifyObjectPaste(element)  # Check security
                new_id = slot._get_id(element.getId())
                element._setId(new_id)
                slot._setObject(new_id, element)
                reorder = guarded_getattr(slot, "reorder")  # Check security
                reorder(new_id, target_index)
                target_index += 1
        finally:
            # Clear the nulls just added.
            for slot in orig_slots.values():
                slot.pack()


    security.declarePublic("deleteElements")
    def deleteElements(self, source_paths):
        sources = []
        for p in source_paths:
            if hasattr(p, "split"):
                p = p.split('/')
            if p:
                sources.append(p)

        # Replace with nulls to avoid changing indexes while deleting.
        orig_slots = {}
        try:
            for source in sources:
                slot = self.restrictedTraverse(source[:-1])
                assert ISlot.isImplementedBy(slot), repr(slot)
                slot_id = id(aq_base(slot))
                if not orig_slots.has_key(slot_id):
                    orig_slots[slot_id] = slot
                nullify = guarded_getattr(slot, "nullify")  # Check security
                nullify(source[-1])
        finally:
            # Clear the nulls just added.
            for slot in orig_slots.values():
                slot.pack()


    security.declarePublic("moveAndDelete")
    def moveAndDelete(self, move_source_paths="", move_target_path="",
                      move_target_index="", delete_source_paths="",
                      REQUEST=None):
        """Move and delete elements.
        """
        if move_source_paths:
            p = move_source_paths.split(':')
            self.moveElements(p, move_target_path, int(move_target_index))
        if delete_source_paths:
            p = delete_source_paths.split(':')
            self.deleteElements(p)
        if REQUEST is not None:
            # Return to the page the user was looking at.
            REQUEST["RESPONSE"].redirect(REQUEST["HTTP_REFERER"])

Globals.InitializeClass(CompositeTool)


def manage_addCompositeTool(dispatcher, REQUEST=None):
    """Adds a composite tool to a folder.
    """
    ob = CompositeTool()
    dispatcher._setObject(ob.getId(), ob)
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST)


