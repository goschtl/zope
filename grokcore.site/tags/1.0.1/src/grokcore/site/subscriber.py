##############################################################################
#
# Copyright (c) 2006-2009 Zope Corporation and Contributors.
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
from zope.app.component.site import LocalSiteManager
from zope.app.container.interfaces import IObjectAddedEvent

from grokcore.site.components import Site

@grokcore.component.subscribe(Site, IObjectAddedEvent)
def addSiteHandler(site, event):
    """Add a local site manager to a Grok site object upon its creation.

    Grok registers this function so that it gets called each time a
    `grok.Site` instance is added to a container.  It creates a local
    site manager and installs it on the newly created site.

    """

    sitemanager = LocalSiteManager(site)
    # LocalSiteManager creates the 'default' folder in its __init__.
    # It's not needed anymore in new versions of Zope 3, therefore we
    # remove it
    del sitemanager['default']
    site.setSiteManager(sitemanager)
