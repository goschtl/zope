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
__docformat__ = "reStructuredText"

import zope.event
from zope.formlib import form

from zope.app.event import objectevent
#from zope.app.pagetemplate import ViewPageTemplateFile

from zf.zscp.interfaces import IPublication
from zf.zscp.package import Package
from zf.zscp.publication import Publication



class AddPackageForm(form.AddForm):
    """Add a package to the repository."""

    form_fields = form.Fields(IPublication).select('packageName', 'name', 
        'summary', 'author', 'authorEmail', 'license', 'metadataVersion')

#    template = ViewPageTemplateFile('package_add.pt')

    def createAndAdd(self, data):

        # the object name
        packageName = data.get('packageName', u'')

        # create the package instance
        package = Package(packageName)
        publication = Publication()
        publication.name = data.get('name', u'')
        publication.packageName = data.get('packageName', u'')
        publication.summary = data.get('summary', u'')
        publication.author = data.get('author', [])
        publication.authorEmail = data.get('authorEmail', [])
        publication.license = data.get('license', [])
        publication.metadataVersion = data.get('metadataVersion', u'')
        package.publication = publication
        zope.event.notify(objectevent.ObjectCreatedEvent(package))

        # Add the register the package with the register method
        self.context.register(package)

        self._finished_add = True
        return package

    def nextURL(self):
        return self.request.URL[-1]
