##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Python Page Browser Views 

$Id$
"""
from zope.app.form.browser.editview import EditView
from zope.app.i18n import ZopeMessageIDFactory as _

class PythonPageEval(object):
    """Evaluate the Python Page."""

    def index(self, **kw):
        """Call a Python Page"""

        self.request.response.setHeader('content-type',
                                        self.context.contentType)

        return self.context(self.request, **kw)

class PythonPageEditView(EditView):
    """Edit View Class for Python Page."""

    syntaxError = None

    def update(self):
        """Update the content with the HTML form data."""
        try:
            status = super(PythonPageEditView, self).update()
        except SyntaxError, err:
            self.syntaxError = err
            status = _('A syntax error occured.')
            self.update_status = status

        return status
