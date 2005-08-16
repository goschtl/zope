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
"""Default service names

$Id: servicenames.py,v 1.3 2004/04/29 15:15:09 fdrake Exp $
"""

# XXX should check that all of the names are still used

from zope.component.servicenames import *

Authentication = 'Authentication'
BrowserMenu = 'BrowserMenu'
EventPublication = 'EventPublication'
EventSubscription = 'Subscription'
ErrorLogging = 'ErrorLogging'
HubIds = 'HubIds'
PrincipalAnnotation = 'PrincipalAnnotation'
