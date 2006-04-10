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
from zf.zscp.interfaces import IPublication
from zf.zscp.interfaces import IRelease
from zf.zscp.interfaces import ICertification


class PackageEditForm(form.EditForm):
    """Edit a package and it's sub forms."""

    form_fields = form.Fields(IPublication, prefix='publication')
    form_fields += form.Fields(IRelease, prefix='release')
    form_fields += form.Fields(ICertification, prefix='certification')

    def update(self):
        result = super(PackageEditForm, self).update()
        if result is None:
            self.context.__parent__.update()
