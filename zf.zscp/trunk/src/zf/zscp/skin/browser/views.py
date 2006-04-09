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
from zope.app.pagetemplate import ViewPageTemplateFile

from zf.zscp.website.browser.site import ISiteIndex



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

