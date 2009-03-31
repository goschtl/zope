##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""ExtJS Component representation.

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.i18n import translate
from zope.security.proxy import removeSecurityProxy
from rwproperty import setproperty, getproperty

from z3c.formext import interfaces

from z3c.form import group


class ExtJSGroup(group.Group):

    @getproperty
    def scriptDependencies(self):
        return self.parentForm.scriptDependencies

    @setproperty
    def scriptDependencies(self, value):
        self.parentForm.scriptDependencies = value


class ExtJSGroupForm(group.GroupForm):
    """A mix-in class for extjs add and edit forms to support groups.

    See z3c.form.group.GroupForm
    """

    zope.interface.implements(interfaces.IExtJSGroupForm)

    def extractData(self, setErrors=True):
        """See z3c.form.interfaces.IForm
        """
        data, errors = super(ExtJSGroupForm, self).extractData(setErrors)
        self.jsonResponse = dict(success=True)
        if errors:
            self.jsonResponse = dict(
                success=False,
                # I shouldn't need the below security proxy
                errors={},
                formErrors=[])
            for error in errors:
                error = removeSecurityProxy(error)
                message = translate(error.message, context=self.request)
                if error.widget:
                    self.jsonResponse['errors'][error.widget.id] = message
                else:
                    self.jsonResponse['formErrors'].append(message)
        return data, errors
