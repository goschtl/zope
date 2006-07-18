##############################################################################
#
# Copyright (c) 2005, 2006 Perse Engineering GmbH and Contributors.
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

from zope.interface import implements
from zope.contentprovider.interfaces import IContentProvider
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.viewlet.viewlet import ViewletBase
from zope.app.component.hooks import getSite
from zope.app.pagetemplate import ViewPageTemplateFile

from zf.zscp.website.browser.site import ISiteIndex
from zf.zscp.website.interfaces import IZSCPSite


def siteURL(context, request):
    site = None
    if IZSCPSite.providedBy(context):
        site = context
    elif site is None:
        site = getSite()
    
    if site is not None:
        return absoluteURL(site, request)
    else:
        # fallback if the skin get called above the IZSCPSite
        return u""


class BreadcrumbProvider(object):
    """Provides a breadcrumb."""

    implements(IContentProvider)

    template = ViewPageTemplateFile('breadcrumb.pt')

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def update(self):
        """Update."""
        pass

    def render(self):
        """Returns the template."""
        if ISiteIndex.providedBy(self.view):
            return u""
        return self.template()


class LogoProvider(object):
    """Provides a logo."""

    implements(IContentProvider)

    template = ViewPageTemplateFile('logo.pt')

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def update(self):
        """Update."""
        pass

    def render(self):
        """Returns the template."""
        if ISiteIndex.providedBy(self.view):
            return self.template()
        return u""


class MenuViewlet(ViewletBase):
    """Provides info for the menu box."""

    template = ViewPageTemplateFile('menu.pt')

    def update(self):
        """Update."""
        pass

    def render(self):
        return self.template()

    def siteURL(self):
        return siteURL(self.context, self.request)


class SearchViewlet(ViewletBase):
    """Provides info for the search box."""

    template = ViewPageTemplateFile('search.pt')

    def update(self):
        """Update."""
        pass

    def render(self):
        return self.template()

    def siteURL(self):
        return siteURL(self.context, self.request)


class ReleaseViewlet(ViewletBase):
    """Provides info for the release box."""

    template = ViewPageTemplateFile('releases.pt')

    def update(self):
        """Update."""
        pass

    def render(self):
        return self.template()

    def siteURL(self):
        return siteURL(self.context, self.request)
