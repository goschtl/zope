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
"""Slot class and supporting code.

$Id: slot.py,v 1.3 2003/10/01 20:59:52 shane Exp $
"""

import os
import sys
from cgi import escape

import Globals
from Acquisition import aq_base, aq_inner, aq_parent
from ZODB.POSException import ConflictError
from OFS.SimpleItem import SimpleItem
from DocumentTemplate.DT_Util import safe_callable
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo

try:
    # Use OrderedFolder if it's available.
    from OFS.OrderedFolder import OrderedFolder
except ImportError:
    # Fall back to normal folders, which happen to retain order anyway.
    from OFS.Folder import Folder as OrderedFolder

from interfaces import ISlot
import perm_names

_www = os.path.join(os.path.dirname(__file__), "www")


class NullElement(SimpleItem):
    """Temporary slot content
    """
    meta_type = "Temporary Null Page Element"

    def __init__(self, id):
        self.id = id


class Slot (OrderedFolder):
    """A slot in a composite.
    """
    meta_type = "Composite Slot"

    __implements__ = ISlot, OrderedFolder.__implements__

    security = ClassSecurityInfo()

    null_element = NullElement("null_element")


    def __init__(self, id):
        self.id = id

    security.declareProtected(perm_names.view, "single")
    def single(self):
        """Renders as a single-element slot."""
        allow_add = (not self._objects)
        return "".join(self.renderToList(allow_add))

    security.declareProtected(perm_names.view, "multiple")
    def multiple(self):
        return self.renderToList(1)

    security.declareProtected(perm_names.change_composites, "reorder")
    def reorder(self, name, new_index):
        if name not in self.objectIds():
            raise KeyError, name
        objs = [info for info in self._objects if info['id'] != name]
        objs.insert(new_index,
                    {'id': name, 'meta_type': getattr(self, name).meta_type})
        self._objects = tuple(objs)

    security.declareProtected(perm_names.change_composites, "nullify")
    def nullify(self, name):
        res = self[name]
        objs = list(self._objects)
        # Replace the item with a pointer to the null element.
        for info in objs:
            if info["id"] == name:
                info["id"] = "null_element"
        delattr(self, name)
        return res

    security.declareProtected(perm_names.change_composites, "nullify")
    def pack(self):
        objs = [info for info in self._objects if info["id"] != "null_element"]
        self._objects = tuple(objs)

    security.declareProtected(perm_names.view, "renderToList")
    def renderToList(self, allow_add):
        """Renders the items to a list.
        """
        res = []
        composite = aq_parent(aq_inner(aq_parent(aq_inner(self))))
        editing = composite.isEditing()
        items = self.objectItems()
        if editing:
            mypath = escape('/'.join(self.getPhysicalPath()))
        for index in range(len(items)):
            name, obj = items[index]

            if editing and allow_add:
                tag = ('<div class="slot_target" target_path="%s" '
                       'target_index="%d"></div>' % (mypath, index))
                res.append(tag)

            try:
                if safe_callable(obj):
                    text = obj()
                else:
                    text = str(obj)
            except ConflictError:
                # Ugly ZODB requirement: don't catch ConflictErrors
                raise
            except:
                t, v = sys.exc_info()[:2]
                t = getattr(t, '__name__', t)
                text = "<code>%s</code>" % (
                    escape(('%s: %s' % (t, v))[:80]))

            if editing:
                path = escape('/'.join(obj.getPhysicalPath()))
                tag = '<div class="slot_element" source_path="%s">' % path
            else:
                # Output a <div> just to ensure that the element
                # is rendered as an HTML block in both editing mode
                # and rendering mode.
                tag = "<div>"
            res.append("%s\n%s\n</div>" % (tag, text))

        if editing and allow_add:
            index = len(items)
            tag = ('<div class="slot_target" target_path="%s" '
                   'target_index="%d"></div>' % (mypath, index))
            res.append(tag)

        return res

Globals.InitializeClass(Slot)



addSlotForm = PageTemplateFile("addSlotForm", _www)

def manage_addSlot(dispatcher, id, REQUEST=None):
    """Adds a slot to a composite.
    """
    ob = Slot(id)
    dispatcher._setObject(ob.getId(), ob)
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST)

def manage_generateSlots(dispatcher, REQUEST=None):
    """Adds all slots requested by a template to a composite.
    """
    dispatcher.this().generateSlots()
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST)
    
