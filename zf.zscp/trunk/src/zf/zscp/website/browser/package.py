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



class PackageIndex(page.Page):
    """Detail view for a single package."""

    template = ViewPageTemplateFile('package_index.pt')

    def update(self):
        pass

    def __call__(self):
        self.update()
        return self.template()
