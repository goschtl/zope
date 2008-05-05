##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#.
##############################################################################
"""RML document.

$Id: interfaces.py 74195 2007-04-16 22:41:24Z srichter $
"""

import lxml.etree
import sys
import z3c.rml.rml2pdf
import z3c.rmldocument.interfaces
import zope.interface
import zope.pagetemplate.pagetemplatefile


class DocumentPageTemplateFile(
    zope.pagetemplate.pagetemplatefile.PageTemplateFile):

    def __init__(self, *args, **kw):
        super(DocumentPageTemplateFile, self).__init__(*args, **kw)
        self.content_type = 'text/xml'

    def get_path_from_prefix(self, _prefix):
        # Had to copy this because of fixed _getframe implementation in the
        # base class.
        if isinstance(_prefix, str):
            path = _prefix
        else:
            if _prefix is None:
                _prefix = sys._getframe(3).f_globals
            path = zope.pagetemplate.pagetemplatefile.package_home(_prefix)
        return path

    def pt_getContext(self, args, kwargs):
        document = args[0]
        context = dict(
            document=document,
            fields=document.fields,
            blocks=document.blocks)
        return context


def preprocess_block(block, data):
    """Preprocess a given block of para-RML to RML.

    """
    if block is None:
        return ''
    root = lxml.etree.fromstring('<rmlblock xmlns:doc="http://xml.gocept.com/namespaces/rmldoc">'+block+'</rmlblock>')
    # Process all value substitutions
    for element in root.getiterator():
        if element.tag != "{http://xml.gocept.com/namespaces/rmldoc}data":
            continue

        value = getattr(data, element.get('field'))
        text = str(value) + (element.tail or '')

        previous = element.getprevious()
        parent = element.getparent()

        if previous is not None:
            previous.tail = (previous.tail or '') + text
        else:
            parent.text = (parent.text or '') + text

        parent.remove(element)
    # Remove artificial <rmlblock> tags
    xml = lxml.etree.tostring(root)
    xml = xml[xml.find('>')+1:]
    xml = xml[:xml.rfind('<')]
    return xml


class Bag(object):
    """An attribute bag."""
    pass


class Document(object):
    """An RML document definition."""

    zope.interface.implements(z3c.rmldocument.interfaces.IDocument)

    encoding = 'utf-8'

    field_schema = zope.interface.Interface
    block_schema = zope.interface.Interface

    def __init__(self, context):
        self.context = context
        self.fields = self.field_schema(context)
        self._setup_blocks()

    def _setup_blocks(self):
        raw_blocks = self.block_schema(self.context)
        self.blocks = Bag()
        for block_name in self.block_schema:
            block_text = getattr(raw_blocks, block_name)
            block_text = preprocess_block(block_text, self.fields)
            setattr(self.blocks, block_name, block_text)

    def __call__(self, raw=False):
        rml = self.template(self).encode(self.encoding)
        if raw:
            return rml
        return z3c.rml.rml2pdf.parseString(rml).getvalue()
