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

$Id: servicenames.py,v 1.9 2003/07/08 19:57:56 srichter Exp $
"""

from zope.component.servicenames import *

HubIds = 'HubIds'
EventPublication = 'EventPublication'
EventSubscription = 'Subscription'
ErrorLogging = 'ErrorLogging'
Roles = 'Roles'
Permissions = 'Permissions'
Authentication = 'Authentication'
Workflows = 'Workflows'
Translation = 'Translation'
DAVSchema = 'DAVSchema'
PrincipalAnnotation = 'PrincipalAnnotation'
SQLDatabaseConnections = 'SQLDatabaseConnections'
