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
"""Event Setup

$Id: eventsetup.py,v 1.2 2004/03/13 15:21:17 srichter Exp $
"""
from zope.app.site.tests.placefulsetup import PlacefulSetup

class EventSetup(PlacefulSetup):

    def setUp(self):
        super(EventSetup, self).setUp(site=True)
        self.createStandardServices()

