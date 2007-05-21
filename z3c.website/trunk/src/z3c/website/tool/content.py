##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Resource License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: app.py 44 2007-02-21 09:43:39Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
from zope.traversing.browser import absoluteURL
from zope.app.component import hooks
from zope.viewlet import viewlet

import z3c.website.layer


class Content(viewlet.ViewletBase):
    """Content tool."""

    sampleViewNames = ['table.html']

    def samples(self):
        res = []
        append = res.append
        try:
            site = hooks.getSite()
            samples = site['samples']
            baseURL = absoluteURL(samples, self.request)
            for name in self.sampleViewNames:
                info = {}
                info['url'] = baseURL+'/'+name
                info['title'] = u'undefined'
                append(info)
        except KeyError:
            # site does not exist right now
            pass
        return res
