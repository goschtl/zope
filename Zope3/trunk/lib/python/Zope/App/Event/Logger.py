##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Helper class to log all events sent out by an event service.

$Id: Logger.py,v 1.1 2002/12/21 15:32:45 poster Exp $
"""

import logging
import pprint
from StringIO import StringIO

from Zope.Event.ISubscriber import ISubscriber

class Logger:

    """Helper class to log all events sent out by an event service.

    This is an event subscriber that you can add via ZCML to log all
    events sent out by Zope.
    """

    __implements__ = ISubscriber

    def __init__(self, severity=logging.INFO):
        self.severity = severity
        self.logger = logging.getLogger("Event.Logger")

    def notify(self, event):
        c = event.__class__
        detail = StringIO()
        if 0:
            # XXX Apparently this doesn't work; why not?
            data = event.__dict__.items()
            data.sort()
            pprint(data, detail)
        else:
            print >>detail, 'XXX detail temporarily disabled'
        self.logger.log(self.severity, "%s.%s: %s",
                        c.__module__, c.__name__, detail.getvalue())
