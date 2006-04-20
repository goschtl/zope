##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Error logging utility

$Id$
"""
from zope.app.error.error import RootErrorReportingUtility
from zope.app.error.error import ErrorReportingUtility
from zope.app.error.error import globalErrorReportingUtility

###############################################################################
# BBB: 12/14/2004
import sys
sys.modules['zope.app.errorservice'] = sys.modules[__name__]

RootErrorReportingService = RootErrorReportingUtility
ErrorReportingService = ErrorReportingUtility
globalErrorReportingService = globalErrorReportingUtility

###############################################################################
