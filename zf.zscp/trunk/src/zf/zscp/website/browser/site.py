##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""

$Id$
"""

from zope.interface import Interface
from zope.interface import implements
from zope.formlib import page
from zope.app.traversing.browser.absoluteurl import absoluteURL
from zope.app.pagetemplate import ViewPageTemplateFile


class ISiteIndex(Interface):
    """Marker interface for Site index.
    
    Provider like logo provider need this for show up at the index view.
    """


class SiteIndex(page.Page):
    """Index for IZSCPSite"""

    implements(ISiteIndex)



class PackageList(page.Page):
    """Show a list of packages."""

    template = ViewPageTemplateFile('site_packages.pt')

    def __init__(self, context, request):
        super(PackageList, self).__init__(context, request)
        self.packageInfos = []

    def __call__(self):
        self.update()
        return self.template()

    def update(self):
        for repos in self.context.values():
            reposURL = absoluteURL(repos, self.request)
            for name in repos.keys():
                info = {}
                info['name'] = name
                info['url'] = reposURL + '/' + name
                self.packageInfos.append(info)

    def getPackageInfo(self):
        return self.packageInfos
