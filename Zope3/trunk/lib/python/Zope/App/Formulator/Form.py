##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""

$Id: Form.py,v 1.2 2002/06/10 23:27:46 jim Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
#from IForm import IForm
from Zope.ComponentArchitecture import getView
from Zope.App.Formulator.IPropertyFieldAdapter import IPropertyFieldAdapter
from Zope.App.Formulator.Errors import ValidationError
from Zope.ComponentArchitecture import getAdapter


class Form(BrowserView):
    """Form base class.
    """

    name = 'Form Name'     # for use by javascript
    title = 'This is a form'
    description = ''
    method = 'post'
    enctype = ''

    _fieldViewNames = []
    template = None


    def __init__(self, *args):
        """Initialize form.
        """
        super(Form, self).__init__(*args)
        self._widgets = []
        

    def index(self, REQUEST, **kw):
        """ """
        return apply(self.template, (REQUEST,), kw)


    def action(self, REQUEST):
        """ """
        errors = []
        values = {}
        for widget in self.getFieldViews(REQUEST):
            value = widget.getValueFromRequest(REQUEST)
            field = widget.context
            try:
                values[field.id] = field.getValidator().validate(field, value)
            except ValidationError, err:
                errors.append(err)

        if errors == []:
            for widget in self.getFieldViews(REQUEST):
                field = widget.context
                getAdapter(field, IPropertyFieldAdapter
                           ).setPropertyInContext(values[field.id])

        return self.index(REQUEST, errors=errors)


    def getFieldViews(self, REQUEST):
        """ """
        views = []
        context = self.context
        for name in self._fieldViewNames:
            views.append(getView(context, name, REQUEST))
        return views
