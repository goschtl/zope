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

$Id: slot.py,v 1.21 2004/04/26 09:30:25 gotcha Exp $
"""

import os
import sys
from cgi import escape

import Globals
from Acquisition import aq_base, aq_inner, aq_parent, aq_get
from ZODB.POSException import ConflictError
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from zLOG import LOG, ERROR

from interfaces import ICompositeElement


try:
    # Use OrderedFolder if it's available.
    from OFS.OrderedFolder import OrderedFolder
except ImportError:
    # Fall back to normal folders, which happen to retain order anyway.
    from OFS.Folder import Folder as OrderedFolder

from interfaces import ISlot
import perm_names

_www = os.path.join(os.path.dirname(__file__), "www")


target_tag = '''<div class="slot_target" title="Slot: %s [%d]"
target_path="%s" target_index="%d"></div>'''

edit_tag = '''<div class="slot_element" source_path="%s" icon="%s" title="%s">
<div class="slot_element_body">%s</div>
</div>'''

# view_tag includes a <div> just to ensure that the element is
# rendered as an HTML block in both editing mode and view mode.
view_tag = '''<div>
%s
</div>'''

# error_tag lets the user click on the 'log' link even if the
# container normally stops clicks.
error_tag = '''%s
(<a href="%s" onmousedown="document.location=this.href">log</a>)'''


class NullElement(SimpleItem):
    """Temporary slot content
    """
    meta_type = "Temporary Null Page Element"

    def __init__(self, id):
        self.id = id

class Slot(OrderedFolder):
    """A slot in a composite.
    """
    meta_type = "Composite Slot"

    __implements__ = ISlot, OrderedFolder.__implements__

    security = ClassSecurityInfo()

    null_element = NullElement("null_element")


    def __init__(self, id):
        self.id = id

    def all_meta_types(self):
        return OrderedFolder.all_meta_types(
            self, interfaces=(ICompositeElement,))

    security.declareProtected(perm_names.view, "single")
    def single(self):
        """Renders as a single-element slot.

        Attempts to prevent the user from adding multiple elements
        by not providing insertion points when the slot already
        contains elements.
        """
        allow_add = (not self._objects)
        return "".join(self.renderToList(allow_add))

    security.declareProtected(perm_names.view, "multiple")
    def multiple(self):
        """Renders as a list containing multiple elements.
        """
        return self.renderToList(1)

    def __str__(self):
        """Renders as a string containing multiple elements.
        """
        return "".join(self.renderToList(1))

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
        res = ['<div class="slot_header"></div>']
        composite = aq_parent(aq_inner(aq_parent(aq_inner(self))))
        editing = composite.isEditing()
        items = self.objectItems()
        if editing:
            mypath = escape('/'.join(self.getPhysicalPath()))
            myid = self.getId()
            if hasattr(self, 'portal_url'):
                icon_base_url = self.portal_url()
            elif hasattr(self, 'REQUEST'):
                icon_base_url = self.REQUEST['BASEPATH1']
            else:
                icon_base_url = '/'
        for index in range(len(items)):
            name, obj = items[index]

            if editing and allow_add:
                res.append(target_tag % (myid, index, mypath, index))

            try:
                assert ICompositeElement.isImplementedBy(obj), (
                    "Not a composite element: %s" % repr(obj))
                text = obj.renderInline()
            except ConflictError:
                # Ugly ZODB requirement: don't catch ConflictErrors
                raise
            except:
                text = formatException(self, editing)


            if editing:
                res.append(self._render_editing(obj, text, icon_base_url))
            else:
                res.append(view_tag % text)

        if editing and allow_add:
            index = len(items)
            res.append(target_tag % (myid, index, mypath, index))

        return res

    def _render_editing(self, obj, text, icon_base_url):
        o2 = obj.dereference()
        icon = getIconURL(o2, icon_base_url)
        title = o2.title_and_id()
        path = escape('/'.join(obj.getPhysicalPath()))
        return edit_tag % (path,
                               escape(icon), escape(title), text)

Globals.InitializeClass(Slot)


def getIconURL(obj, icon_base_url):
    base = aq_base(obj)
    if hasattr(base, 'getIcon'):
        icon = str(obj.getIcon())
    elif hasattr(base, 'icon'):
        icon = str(obj.icon)
    else:
        icon = ""
    if icon and '://' not in icon:
        if not icon.startswith('/'):
            icon = '/' + icon
        icon = icon_base_url + icon
    return icon


def formatException(context, editing):
    """Returns an HTML-ified error message.

    If not editing, the message includes no details.
    """
    exc_info = sys.exc_info()
    try:
        if editing:
            # Show editors the real error
            t, v = exc_info[:2]
            t = getattr(t, '__name__', t)
            msg = "An error occurred. %s" % (
                escape(('%s: %s' % (t, v))[:80]))
        else:
            # Show viewers a simplified error.
            msg = ("An error occurred while generating "
                    "this part of the page.")
        try:
            log = aq_get(context, '__error_log__', None, 1)
        except AttributeError:
            LOG("Composite", ERROR, "Error in a page element",
                error=exc_info)
            return msg
        else:
            error_log_url = log.raising(exc_info)
            return error_tag % (msg, error_log_url)
    finally:
        del exc_info


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
