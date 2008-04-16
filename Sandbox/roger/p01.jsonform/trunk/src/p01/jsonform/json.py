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
"""
$Id: views.py 93 2006-07-22 22:57:31Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
from zope.publisher.interfaces.browser import IBrowserPage
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import IErrorViewSnippet
from z3c.form import util

from zif.jsonserver.interfaces import IJSONRPCPublisher
from zif.jsonserver.interfaces import IJSONRPCRequest
from zif.jsonserver.jsonrpc import MethodPublisher


class Validator(MethodPublisher):

    zope.component.adapts(IBrowserPage, IJSONRPCRequest)

    zope.interface.implements(IJSONRPCPublisher)

    def jsonValidate(self, id, value):
        """Validate the value for the witdget with the given DOM field id."""
        res = u'OK'
        data = {}
        errorView = None
        self.context.updateWidgets()
        widget = util.getWidgetById(self.context, id)
        if widget is not None: 
            content = self.context.widgets.content
            form = self.context.widgets.form
            try:
                value = IDataConverter(widget).toFieldValue(value)
                validator = zope.component.getMultiAdapter((content, self.request, 
                    self.context, getattr(widget, 'field', None), widget), IValidator)
                error = validator.validate(value)

            except (zope.schema.ValidationError, ValueError), error:
                errorView = zope.component.getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     form, content), IErrorViewSnippet)
                errorView.update()

        if errorView is not None:
            res = errorView.render()
        return {'id':id, 'result':res}
