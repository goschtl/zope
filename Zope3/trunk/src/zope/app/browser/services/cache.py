##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Cache configuration adding view

$Id: cache.py,v 1.3 2003/02/21 14:53:34 alga Exp $
"""
__metaclass__ = type

from zope.component import getServiceManager
from zope.publisher.browser import BrowserView
from zope.app.form.utility import setUpWidgets, getWidgetsDataForContent
from zope.app.interfaces.services.cache \
     import ICacheConfiguration
from zope.app.services.cache \
     import CacheConfiguration
from zope.app.interfaces.cache.cache import ICache

class AddCacheConfiguration(BrowserView):

    def __init__(self, *args):
        super(AddCacheConfiguration, self).__init__(*args)
        setUpWidgets(self, ICacheConfiguration)

    def components(self):
        service = getServiceManager(self.context.context)
        paths = [info['path'] for info in service.queryComponent(type=ICache)]
        paths.sort()
        return paths

    def action(self, cache_name, component_path):
        if not cache_name:
            raise ValueError, 'You must specify a cache name'
        cd = CacheConfiguration(cache_name, component_path)
        cd = self.context.add(cd)
        getWidgetsDataForContent(self, ICacheConfiguration, content=cd,
                                 strict=False)
        self.request.response.redirect(self.context.nextURL())
