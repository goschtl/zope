##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""A widget for ComponentPath field.

$Id: field.py,v 1.7 2003/03/21 20:59:24 jim Exp $
"""
__metaclass__ = type

from zope.app.browser.form.widget import BrowserWidget
from zope.app.interfaces.browser.form import IBrowserWidget
from zope.component import getServiceManager, getView
from zope.app.form.widget import Widget
from zope.publisher.browser import BrowserView
from xml.sax.saxutils import quoteattr
from zope.app.interfaces.form import WidgetInputError
from zope.app.traversing import traverse, canonicalPath

class ComponentPathWidget(BrowserWidget):

    def haveData(self):
        value = self.request.form.get(self.name, None)
        if not value:
            return False
        else:
            return super(ComponentPathWidget, self).haveData()

    def _convert(self, value):
        return value or None

    def __call__(self):
        selected = self._showData()
        field = self.context
        return renderPathSelect(field.context, field.type,
                                self.name, selected)

class ComponentPathDisplayWidget(ComponentPathWidget):

    def __call__(self):
        path = self._showData()
        path = canonicalPath(path)
        ob = traverse(self.context.context, path)
        url = str(getView(ob, 'absolute_url', self.request))
        url += "/@@SelectedManagementView.html"
        return '<a href="%s">%s</a>' % (url, path)

class ComponentLocationWidget(Widget, BrowserView):

    __implements__ = IBrowserWidget

    # Names used:
    #
    #  name.p  the value of the path
    #  name.d  the value of the dotted module name

    def haveData(self):
        # do I have name.p xor name.m ?
        form = self.request.form

        has_p = self.name+'.p' in form
        has_d = self.name+'.d' in form

        return bool((has_p or has_d) and not (has_p and has_d))

    def getData(self, optional=0):
        field = self.context
        form = self.request.form
        name_p = self.name+'.p'
        name_d = self.name+'.d'

        path = form.get(self.name+'.p', '').strip()
        dottedname = form.get(self.name+'.d', '').strip()

        if path and not path.startswith('/'):
            raise WidgetInputError(
                self.context.__name__, self.title,
                'The component path must start with a "/"')

        if dottedname and '/' in dottedname:
            raise WidgetInputError(
                self.context.__name__, self.title,
                'A dotted module name cannot contain a "/"')

        if path and dottedname:
            location = ''
        else:
            location = path or dottedname

        if not location:
            if path and dottedname:
                raise WidgetInputError(
                        self.context.__name__, self.title,
                        'Either give a module or select a component')
            # No user input
            if field.required and not optional:
                raise MissingInputError(field.__name__, field.title,
                                        'the field is required')
            return field.default

        location = unicode(location)

        if not optional:
            try:
                field.validate(location)
            except ValidationError, v:
                raise WidgetInputError(self.context.__name__,
                                       self.title, str(v))
        return location

    def __call__(self):
        'See IBrowserWidget'
        field = self.context
        form = self.request.form
        name = self.name

        if self._data is None:  # no data has been set with Widget.setData(),
                                # so use the data in the form

            path = form.get(name+'.p', '').strip()
            dottedname = form.get(name+'.d', '').strip()

            if path or dottedname:
                location = path or dottedname
                # XXX is validation here really needed?
                #field.validate(location)
            else:  # otherwise, use the default
                location = field.default or ''
                if location.startswith('/'):
                    path = location
                    dottedname = ''
                else:
                    dottedname = location
                    path = ''
        else:
            # data has been set with Widget.setData()
            location = self._data
            if location.startswith('/'):
                path = location
                dottedname = ''
            else:
                dottedname = location
                path = ''

        selectmarkup = renderPathSelect(field.context, field.type,
                                        name+'.p', path)
        inputmarkup = '<input type="text" name="%s.d" value="%s">' % (
                      name, dottedname)
        HTML = 'path: %s<br>dotted name: %s' % (selectmarkup, inputmarkup)
        return HTML

    def hidden(self):
        'See IBrowserWidget'
        if self._data is None:
            data = self.getData(1)
        else:
            data = self._data

        if not data:
            return ''

        if data.startswith('/'):
            name = self.name+'.p'
        else:
            name = self.name+'.d'

        return '<input type="hidden" name="%s" value=%s />' % (
               name, quoteattr(data))

    def label(self):
        return '<label for="%s">%s</label>' % (self.name, self.title)

    def row(self):
        return '<div class="label">%s</div><div class="field">%s</div>"' % (
                self.label(), self())

    # --- deprecated methods of IBrowserWidget

    def renderHidden(self, value):
        'See IBrowserWidget'
        raise NotImplementedError

    def render(self, value):
        'See IBrowserWidget'
        raise NotImplementedError

class ComponentLocationDisplayWidget(ComponentLocationWidget):
    def __call__(self):
        if self._data is None:
            data = self.getData(1)
        else:
            data = self._data
        # location = data
        return data

def renderPathSelect(context, type, name, selected, empty_message=''):
    service_manager = getServiceManager(context)
    info = service_manager.queryComponent(type)
    result = []

    result.append('<select name="%s">' % name)
    result.append('<option>%s</option>' % empty_message)

    for item in info:
        item = item['path']
        if item == selected:
            result.append('<option selected>%s</option>' % item)
        else:
            result.append('<option>%s</option>' % item)

    result.append('</select>')
    return ''.join(result)

