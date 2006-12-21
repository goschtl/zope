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

from zope.publisher.browser import BrowserView
from zope import component, schema
from zope.cachedescriptors.property import Lazy
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib import form
from lovely.tag import _

from zope.formlib import form

class ManageView(form.PageForm):

    label=_(u"Manage Tagging Engine")
    
    form_fields = form.Fields()
    
    @form.action(label=_(u'Clean Stale Items'))
    def cleanStale(self, action, data):
        cleaned = self.context.cleanStaleItems()
        self.status = u'Cleaned out %s items' % len(cleaned)
