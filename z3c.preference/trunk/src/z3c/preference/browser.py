##############################################################################
#
# Copyright (c) 2010, 2012 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
#############################################################################

import z3c.form.field
import z3c.formui.form
import zope.security.proxy


class EditForm(z3c.formui.form.EditForm):

    def __init__(self, *args, **kw):
        super(EditForm, self).__init__(*args, **kw)
        self.label = self.context.__title__

    @property
    def fields(self):
        schema = zope.security.proxy.getObject(self.context.__schema__)
        if schema is None:
            # no schema set on prefence group, so we have no fields
            return z3c.form.field.Fields()
        return z3c.form.field.Fields(schema)
