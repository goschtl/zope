##############################################################################
#
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
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

import grokcore.component
from grokcore.component.interfaces import IContext

from persistent import Persistent

from zope.interface import implements

from zope.app.component.site import SiteManagerContainer,  LocalSiteManager

from zope.app.container.contained import Contained

class Site(SiteManagerContainer):
    pass

class LocalUtility(Contained, Persistent):
    implements(IContext)
