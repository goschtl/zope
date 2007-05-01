##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tagging Views

$Id$
"""
__docformat__ = "reStructuredText"

try:
    from zope.publisher.browser import BrowserView
except ImportError:
    from zope.app.publisher.browser import BrowserView
from zope import schema
from zope.formlib import form
from lovely.tag import _
from zope.formlib import form
import csv
import cStringIO

class ManageView(form.PageForm):

    label=_(u"Manage Tagging Engine")
    
    form_fields = form.Fields(
        schema.DottedName(__name__=u'normalizer',
                          title=_(u'Normalizer Function'),
                          required=False),
        schema.TextLine(__name__=u'oldName',
                        title=_(u'Old Name'),
                        required=False),
        schema.TextLine(__name__=u'newName',
                        title=_(u'New Name'),
                        required=False),
        )
    
    @form.action(label=_(u'Clean Stale Items'))
    def cleanStale(self, action, data):
        cleaned = self.context.cleanStaleItems()
        self.status = u'Cleaned out %s items' % len(cleaned)
        

    @form.action(label=_(u'Normalize'))
    def normalize(self, action, data):
        normalizer = data.get('normalizer')
        if not normalizer:
            self.status=_(u'No normalizer function defined')
            return
        count = self.context.normalize(normalizer)
        self.status = u'Normalized %s tag objects' % count

    @form.action(label=_(u'Rename Tag'))
    def renameTag(self, action, data):
        oldName = data.get('oldName')
        newName = data.get('newName')
        if not (oldName and newName):
            self.status=_(u'Please define old and new name.')
            return
        count = self.context.rename(oldName, newName)
        self.status = u'Renamed %s tag objects' % count


class CSVExportView(BrowserView):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/csv')
        res = cStringIO.StringIO()
        writer = csv.writer(res, dialect=csv.excel)
        encoding = 'utf-8'
        writer.writerow(('Name', 'User', 'Item', 'Timestamp'))
        for tag in self.context.getTagObjects():
            row = [tag.name.encode(encoding)]
            row.append(tag.user.encode(encoding))
            row.append(tag.item)
            row.append(tag.timestamp)
            writer.writerow(row)
        return res.getvalue()

        
        
