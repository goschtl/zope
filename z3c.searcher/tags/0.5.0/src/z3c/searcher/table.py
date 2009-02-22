##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

from z3c.i18n import MessageFactory as _

import z3c.formui.form
from z3c.table import table
from z3c.form import button
from z3c.searcher import interfaces
from z3c.searcher import filter
from z3c.searcher import form


# conditions
def hasContent(form):
    return form.hasContent


def canCancel(form):
    return form.supportsCancel


class SearchTable(table.Table, z3c.formui.form.Form):
    """Search form with result table."""

    zope.interface.implements(interfaces.ISearchTable)

    template = getPageTemplate()

    prefix = 'formTable'

    # internal defaults
    hasContent = False
    nextURL = None
    ignoreContext = False
    filterForm = None

    # table defaults
    cssClasses = {'table': 'contents'}
    cssClassEven = u'even'
    cssClassOdd = u'odd'
    cssClassSelected = u'selected'
    
    batchSize = 25
    startBatchingAt = 25
    
    # customize this part
    allowCancel = True

    filterFactory = filter.SearchFilter

    def setupFilterForm(self):
        """Setup filter form before super form get updated."""
        self.filterForm = form.FilterForm(self.context, self.request)
        self.filterForm.filterFactory = self.filterFactory

    def updateFilterForm(self):
        """Update filter form after super form get updated."""
        self.filterForm.update()

    def setupConditions(self):
        self.hasContent = bool(self.rows)
        if self.allowCancel:
            self.supportsCancel = self.hasContent

    def updateAfterActionExecution(self):
        """Update table data if subform changes soemthing."""
        # first update table data which probably changed
        super(SearchTable, self).update()
        # second setup conditions
        self.setupConditions()
        # third update action which we have probably different conditions for
        self.updateActions()

    def update(self):
        # 1 .setup filter form
        self.setupFilterForm()
        # 2. process filter form
        self.updateFilterForm()
        # 3. setup widgets
        self.updateWidgets()
        # 4. setup search values, generate rows, setup headers and columns
        super(SearchTable, self).update()
        # 5. setup conditions
        self.setupConditions()
        # 6. setup form part
        self.updateActions()
        self.actions.execute()

    @property
    def values(self):
        return self.filterForm.values()

    @button.buttonAndHandler(_('Cancel'), name='cancel', condition=canCancel)
    def handleCancel(self, action):
        self.nextURL = self.request.getURL()

    def render(self):
        """Render the template."""
        if self.nextURL is not None:
            self.request.response.redirect(self.nextURL)
            return ""
        return self.template()
