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
"""Spreadsheet Implementation

$Id$
"""
__docformat__ = "reStructuredText"
from zope.viewlet.viewlet import CSSViewlet
from z3c.form import field

from z3c.formdemo.spreadsheet import content, spreadsheet


SpreadsheetCSSViewlet = CSSViewlet('spreadsheet.css')

class CandidateSpreadsheet(spreadsheet.Spreadsheet):

    sessionKey = 'z3c.formdemo.spreadsheet.candidate'
    rowFields = field.Fields(content.ICandidate)
    columnWidths = (200, 200, 150)

    def getContent(self):
        return [obj for obj in self.context.values()
                if content.ICandidate.providedBy(obj)]
