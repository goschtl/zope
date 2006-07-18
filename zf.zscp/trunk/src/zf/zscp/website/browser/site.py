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
from zope.publisher.browser import BrowserPage
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app import zapi
from zope.app.pagetemplate import ViewPageTemplateFile
from zc.table import table, column

from zf.zscp import interfaces

class ISiteIndex(Interface):
    """Marker interface for Site index.

    Provider like logo provider need this for show up at the index view.
    """


class SiteIndex(object):
    """Index for IZSCPSite"""

    implements(ISiteIndex)


class NameColumn(column.SortingColumn):

    def renderCell(self, item, formatter):
        url = zapi.absoluteURL(item, formatter.request)
        return '<a href="%s">%s</a>' %(url, item.name)

    def getSortKey(self, item, formatter):
        return item.name

def getCertification(item, formatter):
    return interfaces.CERTIFICATION_LEVELS.getTerm(
        item.publication.certificationLevel).title


class PackageList(BrowserPage):
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


    def table(self):

        columns = [
            NameColumn(u'Package Name', name='packageName'),
            column.GetterColumn(u'Name', name='name',
                                getter=lambda i,f: i.publication.name),
            column.GetterColumn(u'Certification', getCertification,
                                name='certification'),
            ]

        formatter = table.FormSortFormatter(
            self.context, self.request, self.context['packages'].values(),
            columns=columns,
            sort_on=(('certification', True), ('packageName', False))
            )
        return formatter()
