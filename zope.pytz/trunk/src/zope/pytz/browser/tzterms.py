##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Time-zone selection support

$Id$
"""

import pytz
from zope import component, interface
import zope.publisher.interfaces.browser
import zope.pytz.source
import zope.schema.interfaces
import zope.app.form.browser.interfaces
import zope.i18nmessageid

message = zope.i18nmessageid.MessageFactory('pytz')

class Term:
    interface.implements(zope.schema.interfaces.ITitledTokenizedTerm)

    def __init__(self, title, token):
        self.title = title
        self.token = token

class TimeZoneTerms:
    """Term and value support needed by query widgets."""

    interface.implements(zope.app.form.browser.interfaces.ITerms)
    component.adapts(zope.pytz.source.AvailableTimeZones,
                     zope.publisher.interfaces.browser.IBrowserRequest)

    def __init__(self, source, request):
        self.request = request

    def getTerm(self, value):
        token = value.zone
        title = token.replace('_', ' ')
        return Term(message(token, title), token)

    def getValue(self, token):
        return pytz.timezone(token)
