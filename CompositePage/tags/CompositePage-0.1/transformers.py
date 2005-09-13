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
"""Editable page transformation classes.

$Id: transformers.py,v 1.2 2003/10/01 18:59:31 shane Exp $
"""

import os
import re

import Globals
from Acquisition import aq_base, aq_inner, aq_parent
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.ZopeGuards import guarded_getattr

from rawfile import RawFile


_common = os.path.join(os.path.dirname(__file__), "common")
_zmi = os.path.join(os.path.dirname(__file__), "zmi")

start_of_head_search = re.compile("(<head[^>]*>)", re.IGNORECASE).search
start_of_body_search = re.compile("(<body[^>]*>)", re.IGNORECASE).search
end_of_body_search = re.compile("(</body[^>]*>)", re.IGNORECASE).search

DEFAULT_HTML_PAGE = """
<html>
<head>
<title>Composite Page</title>
</head>
<body>
%s
</body>
</html>
"""


class CommonTransformer (SimpleItem):
    """Basic page transformer.

    Adds editing features to a rendered composite.
    """

    security = ClassSecurityInfo()

    security.declarePublic(
        "pdlib_js", "design_js", "pdstyles_css", "designstyles_css",
        "transform")
    pdlib_js = RawFile("pdlib.js", "text/javascript", _common)
    edit_js = RawFile("edit.js", "text/javascript", _common)
    pdstyles_css = RawFile("pdstyles.css", "text/css", _common)
    editstyles_css = RawFile("editstyles.css", "text/css", _common)

    header_templates = (PageTemplateFile("header.pt", _common),)
    top_templates = ()
    bottom_templates = (PageTemplateFile("bottom.pt", _common),)


    security.declarePublic("transform")
    def transform(self, composite, text):
        """Adds scripts to a rendered composite.
        """
        params = {
            "tool": aq_parent(aq_inner(self)),
            "transformer": self,
            "composite": composite,
            }
        header = ""
        top = ""
        bottom = ""
        for t in self.header_templates:
            header += t.__of__(self)(**params)
        for t in self.top_templates:
            top += t.__of__(self)(**params)
        for t in self.bottom_templates:
            bottom += t.__of__(self)(**params)
            
        match = start_of_head_search(text)
        if match is None:
            # Turn it into a page.
            text = DEFAULT_HTML_PAGE % text
            match = start_of_head_search(text)
            if match is None:
                raise CompositeError("Could not find header")
        if header:
            index = match.end(0)
            text = "%s%s%s" % (text[:index], header, text[index:])
        if top:
            match = start_of_body_search(text)
            if match is None:
                raise CompositeError("No 'body' tag found")
            index = match.end(0)
            text = "%s%s%s" % (text[:index], top, text[index:])
        if bottom:
            match = end_of_body_search(text)
            if match is None:
                raise CompositeError("No 'body' end tag found")
            m = match
            while m is not None:
                # Find the *last* occurrence of "</body>".
                match = m
                m = end_of_body_search(text, match.end(0))
            index = match.start(0)
            text = "%s%s%s" % (text[:index], bottom, text[index:])

        return text

Globals.InitializeClass(CommonTransformer)



class ZMITransformer (CommonTransformer):
    """Zope management interface page transformer.

    Adds editing features to a rendered composite.
    """
    security = ClassSecurityInfo()

    security.declarePublic("zmi_edit_js")
    zmi_edit_js = RawFile("zmi_edit.js", "text/javascript", _zmi)

    header_templates = CommonTransformer.header_templates + (
        PageTemplateFile("header.pt", _zmi),)
    top_templates = CommonTransformer.top_templates + (
        PageTemplateFile("top.pt", _zmi),)
    bottom_templates = (PageTemplateFile("bottom.pt", _zmi),
                        ) + CommonTransformer.bottom_templates

    security.declarePublic("showElement")
    def showElement(self, path, RESPONSE):
        """Redirects to the workspace for an element.
        """
        root = self.getPhysicalRoot()
        obj = root.restrictedTraverse(path)
        RESPONSE.redirect(obj.absolute_url() + "/manage_workspace")

    security.declarePublic("showSlot")
    def showSlot(self, path, RESPONSE):
        """Redirects to (and possibly creates) the workspace for a slot.
        """
        from composite import Composite

        obj = self.getPhysicalRoot()
        parts = path.split('/')
        for name in parts:
            obj = obj.restrictedTraverse(name)
            try:
                is_comp = isinstance(obj, Composite)
            except TypeError:
                is_comp = 0  # Python 2.1 bug
            if is_comp:
                gen = guarded_getattr(obj, "generateSlots")
                gen()
        RESPONSE.redirect(obj.absolute_url() + "/manage_workspace")

Globals.InitializeClass(ZMITransformer)

