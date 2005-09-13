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
"""Composite class and supporting code.

$Id: composite.py,v 1.2 2003/10/01 18:59:31 shane Exp $
"""

import os
import re

import Globals
import Acquisition
from Acquisition import aq_base, aq_inner, aq_parent, aq_get
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from AccessControl import ClassSecurityInfo
from AccessControl.ZopeGuards import guarded_getattr

from interfaces import ISlot, CompositeError
from slot import Slot
import perm_names

_www = os.path.join(os.path.dirname(__file__), "www")


class SlotGenerator (Acquisition.Explicit):
    """Automatically makes slots available to the template.
    """
    def __getitem__(self, name):
        composite = aq_parent(aq_inner(self))
        slots = composite.filled_slots
        try:
            return slots[name]
        except (KeyError, AttributeError):
            # Generate a new slot.
            s = Slot(name)
            if composite._v_generating:
                # Persist the slot immediately.
                slots._setObject(s.getId(), s)
            else:
                # Persist automatically if the slot changes
                jar = AddOnChangeJar(slots)
                s._p_jar = jar
            return s.__of__(slots)



class Composite(Folder):
    """An HTML fragment composed from a template and fragments.
    """
    meta_type = "Composite"

    security = ClassSecurityInfo()

    manage_options = (
        Folder.manage_options[:1]
        + ({"label": "Design", "action": "manage_designForm",},
           {"label": "View", "action": "view",},)
        + Folder.manage_options[2:]
        )

    template_path = "template"
    _v_editing = 0
    _v_rendering = 0
    _v_generating = 0

    security.declarePublic("slots")
    slots = SlotGenerator()

    _properties = Folder._properties + (
        {"id": "template_path", "mode": "w", "type": "string",
         "label": "Path to template"},
        )

    def __init__(self):
        f = SlotCollection()
        f._setId("filled_slots")
        self._setObject(f.getId(), f)

    security.declareProtected(perm_names.view, "getTemplate")
    def getTemplate(self):
        return self.restrictedTraverse(self.template_path)

    security.declareProtected(perm_names.change_composites, "generateSlots")
    def generateSlots(self):
        """Creates the slots defined by the template.
        """
        self._v_generating = 1
        try:
            self()
        finally:
            self._v_generating = 0

    security.declareProtected(perm_names.view, "__call__")
    def __call__(self):
        """Renders the composite.
        """
        if self._v_rendering:
            raise CompositeError("Circular composite reference")
        self._v_rendering = 1
        try:
            template = self.getTemplate()
            return template()
        finally:
            self._v_rendering = 0

    view = __call__

    index_html = None

    security.declareProtected(perm_names.change_composites, "design")
    def design(self, transformer="common"):
        """Renders the composite with editing features.
        """
        tool = aq_get(self, "composite_tool", None, 1)
        if tool is None:
            raise CompositeError("No composite_tool found")

        # Never cache a design view.
        req = getattr(self, "REQUEST", None)
        if req is not None:
            req["RESPONSE"].setHeader("Cache-Control", "no-cache")

        self._v_editing = 1
        try:
            text = self()
        finally:
            self._v_editing = 0
        tf = guarded_getattr(tool.transformers, transformer)
        return tf.transform(self, text)

    security.declareProtected(perm_names.change_composites,
                              "manage_designForm")
    def manage_designForm(self):
        """Renders the composite with editing and ZMI features.
        """
        return self.design("zmi")

    security.declareProtected(perm_names.view, "isEditing")
    def isEditing(self):
        return self._v_editing

Globals.InitializeClass(Composite)



class SlotCollection(Folder):
    """Collection of composite slots.
    """
    meta_type = "Slot Collection"

    def all_meta_types(self):
        return Folder.all_meta_types(self, interfaces=(ISlot,))



class AddOnChangeJar:
    """Adds an object to a folder if the object changes.
    """

    def __init__(self, parent):
        self.parent = parent

    def register(self, obj):
        obj._p_jar = None
        self.parent._setObject(obj.getId(), obj)


addCompositeForm = PageTemplateFile("addCompositeForm", _www)

def manage_addComposite(dispatcher, id, title="", create_sample=0,
                        REQUEST=None):
    """Adds a composite to a folder.
    """
    ob = Composite()
    ob._setId(id)
    ob.title = string(title)
    dispatcher._setObject(ob.getId(), ob)
    if create_sample:
        ob = dispatcher.this()._getOb(ob.getId())
        f = open(os.path.join(_www, "sample_template.zpt"), "rt")
        try:
            text = f.read()
        finally:
            f.close()
        pt = ZopePageTemplate(id="template", text=text,
                              content_type="text/html")
        ob._setObject(pt.getId(), pt)
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST)


def string(s):
    """Ensures an object is either a string or a unicode.
    """
    try:
        return str(s)
    except UnicodeEncodeError:
        return unicode(s)

