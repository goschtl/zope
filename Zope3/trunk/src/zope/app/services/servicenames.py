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
"""
Default service names

$Id: servicenames.py,v 1.2 2003/03/08 00:51:43 seanb Exp $
"""

from zope.component.servicenames import *

HubIds = 'HubIds'
EventDispatch = 'Events'
EventSubscription = 'Subscription'
ErrorLogging = 'ErrorReportingService'
Roles = 'Roles'
Permissions = 'Permissions'
Authentication = 'Authentication'
Workflows = 'Workflows'

