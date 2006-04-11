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

from zope.formlib import form
from zope.formlib import page
from zf.zscp.interfaces import IPublication
from zf.zscp.interfaces import IRelease
from zf.zscp.interfaces import ICertification
from zope.app.pagetemplate import ViewPageTemplateFile


def listToString(inList):
    outStr = u''
    for item in inList:
        outStr += item
        outStr += u', '
    if len(outStr) > 2:
        # remove the last separator
        outStr = outStr[:-2]
    return outStr


class PackageEditForm(form.EditForm):
    """Edit a package and it's sub forms."""

    form_fields = form.Fields(IPublication, prefix='publication')

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context.publication, 
            self.request, adapters=self.adapters, ignore_request=ignore_request
            )

    def update(self):
        result = super(PackageEditForm, self).update()
        if result is None:
            self.context.__parent__.update(self.context)



class PackageInfo(page.Page):
    """Package info view."""

    template = ViewPageTemplateFile('package_info.pt')

    def update(self):
        publication = self.context.publication
        info = {}
        info['packageName'] = publication.packageName
        info['name'] = publication.name
        info['summary'] = publication.summary
        info['description'] = publication.description
        info['homePage'] = publication.homePage
        info['developersMailinglist'] = publication.developersMailinglist
        info['usersMailinglist'] = publication.usersMailinglist
        info['issueTracker'] = publication.issueTracker
        info['repositoryLocation'] = publication.repositoryLocation
        info['repositoryWebLocation'] = publication.repositoryWebLocation
        info['certificationLevel'] = publication.certificationLevel
        info['certificationDate'] = publication.certificationDate
        info['metadataVersion'] = publication.metadataVersion

        # list of strings converted to strings
        info['author'] = listToString(publication.author)
        info['authorEmail'] = listToString(publication.authorEmail)
        info['license'] = listToString(publication.license)
        info['platform'] = listToString(publication.platform)
        info['classifier'] = listToString(publication.classifier)

        self._info = info

    @property
    def info(self):
        return self._info

    def __call__(self):
        self.update()
        return self.template()



class PackageReleases(page.Page):
    """Release view."""

    template = ViewPageTemplateFile('package_releases.pt')

    def update(self):
        releases = self.context.releases
        info = {}
        self._info = info

    @property
    def info(self):
        return self._info

    def __call__(self):
        self.update()
        return self.template()



class PackageClassifiers(page.Page):
    """Classifier view."""

    template = ViewPageTemplateFile('package_classifiers.pt')

    def update(self):
        certifications = self.context.certifications
        info = {}
        self._info = info

    @property
    def info(self):
        return self._info

    def __call__(self):
        self.update()
        return self.template()



class PackageCertifications(page.Page):
    """Certification view."""

    template = ViewPageTemplateFile('package_certifications.pt')

    def update(self):
        info = {}

        # publication info
        publication = self.context.publication
        info['packageName'] = publication.packageName
        info['name'] = publication.name
        self._info = info

        # certification info
        certifications = []
        certs = self.context.certifications
        for cert in certs:
            info = {}
            info['action'] = cert.action
            info['sourceLevel'] = cert.sourceLevel
            info['targetLevel'] = cert.targetLevel
            info['date'] = cert.date
            info['certificationManger'] = cert.certificationManger
            info['comments'] = cert.comments
            certifications.append(info)
        self._certifications = certifications

    @property
    def info(self):
        return self._info

    @property
    def certifications(self):
        return self._certifications

    def __call__(self):
        self.update()
        return self.template()
