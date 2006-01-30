##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser views for documents.

$Id$
"""

from Products.CMFDefault.exceptions import EditingConflict
from Products.CMFDefault.exceptions import IllegalHTML
from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFDefault.utils import MessageID as _
from Products.CMFDefault.utils import scrubHTML

from utils import FormViewBase


class DocumentEditView(FormViewBase):

    """ Edit view for IMutableDocument.
    """

    _BUTTONS = ({'name': 'change',
                 'value': _(u'Change'),
                 'transform': ('validateTextFile', 'validateHTML', 'update'),
                 'redirect': ('context', 'object/edit')},
                {'name': 'change_and_view',
                 'value': _(u'Change and View'),
                 'transform': ('validateTextFile', 'validateHTML', 'update'),
                 'redirect': ('context', 'object/view')})

    def title(self):
        return self.context.Title()

    def description(self):
        return self.context.Description()

    def SafetyBelt(self):
        return self.request.form.get('SafetyBelt', self.context.SafetyBelt())

    def text_format(self):
        return self.request.form.get('text_format', self.context.text_format)

    def text(self):
        return self.request.form.get('text', self.context.EditableBody())

    def validateTextFile(self, file='', **kw):
        try:
            upload = file.read()
        except AttributeError:
            return self.setStatus(True)
        else:
            if upload:
                return self.setStatus(True, text=upload)
            else:
                return self.setStatus(True)

    def validateHTML(self, text, description='', **kw):
        try:
            description = scrubHTML(description)
            text = scrubHTML(text)
            return self.setStatus(True, text=text, description=description)
        except IllegalHTML, errmsg:
            return self.setStatus(False, errmsg)

    def update(self, text_format, text, SafetyBelt='', **kw):
        context = self.context
        if text_format != context.text_format or text != context.text:
            try:
                context.edit(text_format, text, safety_belt=SafetyBelt)
                return self.setStatus(True, _(u'Document changed.'))
            except (ResourceLockedError, EditingConflict), errmsg:
                return self.setStatus(False, errmsg)
        else:
            return self.setStatus(False, _(u'Nothing to change.'))
