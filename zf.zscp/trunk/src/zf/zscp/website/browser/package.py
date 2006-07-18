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
import zope.schema
from zope.formlib import form
from zope.publisher.browser import BrowserPage
from zf.zscp.interfaces import IPublication
from zf.zscp.interfaces import IRelease
from zf.zscp.interfaces import ICertification
from zf.zscp.interfaces import CERTIFICATION_LEVELS
from zf.zscp.interfaces import CERTIFICATION_ACTIONS
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



class PackageInfo(BrowserPage):
    """Package info view."""

    template = ViewPageTemplateFile('package_info.pt')

    def update(self):
        formatter = self.request.locale.dates.getFormatter('date', 'medium')
        publication = self.context.publication
        info = {}
        for name, field in zope.schema.getFieldsInOrder(IPublication):
            info[name] = getattr(publication, name)

        info['certificationLevel'] = CERTIFICATION_LEVELS.getTerm(
            publication.certificationLevel).title
        info['certificationDate'] = formatter.format(
            publication.certificationDate)

        info['author'] = [
            {'name': name, 'email': email}
            for name, email in zip(publication.author, publication.authorEmail)]

        # list of strings converted to strings
        info['license'] = listToString(publication.license)
        info['platform'] = listToString(publication.platform)

        self._info = info

    @property
    def info(self):
        return self._info

    def __call__(self):
        self.update()
        return self.template()


class PackageCommunity(PackageInfo):

    template = ViewPageTemplateFile('package_community.pt')


class PackageReleases(BrowserPage):
    """Release view."""

    template = ViewPageTemplateFile('package_releases.pt')

    def update(self):
        pass

    def releases(self):
        releases = []
        formatter = self.request.locale.dates.getFormatter('date', 'medium')
        for release in self.context.releases:
            info = {}
            for name, field in zope.schema.getFieldsInOrder(IRelease):
                info[name] = getattr(release, name)

            info['date'] = formatter.format(release.date)
            level = CERTIFICATION_LEVELS.getTerm(release.certification)
            info['certification'] = level.title
            releases.append(info)

        return releases

    def __call__(self):
        self.update()
        return self.template()



class PackageClassifiers(BrowserPage):
    """Classifier view."""

    template = ViewPageTemplateFile('package_classifiers.pt')

    def update(self):
        info = {'classifier': self.context.publication.classifier}
        self._info = info

    def render(self):
        return self.template()

    @property
    def info(self):
        return self._info

    def __call__(self):
        self.update()
        return self.render()


class PackageCertifications(BrowserPage):
    """Certification view."""

    template = ViewPageTemplateFile('package_certifications.pt')

    def update(self):
        pass

    def info(self):
        return {'packageName': self.context.publication.packageName,
                'name': self.context.publication.name}

    def certifications(self):
        certifications = []
        certs = self.context.certifications
        formatter = self.request.locale.dates.getFormatter('date', 'medium')
        levels = CERTIFICATION_LEVELS
        actions = CERTIFICATION_ACTIONS
        for cert in certs:
            info = {}
            info['action'] = actions.getTerm(cert.action).title
            info['sourceLevel'] = levels.getTerm(cert.sourceLevel).title
            info['targetLevel'] = levels.getTerm(cert.targetLevel).title
            info['date'] = formatter.format(cert.date)
            info['certificationManager'] = cert.certificationManager
            info['comments'] = cert.comments
            certifications.append(info)
        return certifications

    def __call__(self):
        self.update()
        return self.template()
