##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
""" default IFormatterConfiglet utility

$Id$
"""

from zope import interface, component
from zope.component import getGlobalSiteManager
from zope.app.appsetup.product import getProductConfiguration
from zope.app.appsetup.interfaces import IDatabaseOpenedEvent

import vocabulary
from interfaces import IFormatterConfiglet


@component.adapter(IDatabaseOpenedEvent)
def initFormatter(event):
    config = getProductConfiguration('z3ext.formatter')
    if config is None:
        config = {}

    sm = getGlobalSiteManager()

    try:
        timezone = vocabulary.timezones.getTermByToken(
            config.get('timezone', u'US/Pacific')).value
    except LookupError:
        timezone = u'US/Pacific'

    principalTimezone = config.get('principalTimezone', u'true').lower()
    if principalTimezone == 'true':
        principalTimezone = True
    else:
        principalTimezone = False

    try:
        timezoneFormat = vocabulary.timezonesOptions.getTermByToken(
            config.get('timezoneFormat', u'2')).value
    except LookupError:
        timezoneFormat = 2

    IFormatterConfiglet['timezone'].default = timezone
    IFormatterConfiglet['timezoneFormat'].default = timezoneFormat
    IFormatterConfiglet['principalTimezone'].default = principalTimezone
