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
"""These are the interfaces for the common fields.

$Id: interfacewidget.py,v 1.9 2003/01/07 17:56:01 stevea Exp $
"""

import sys
from zope.interface import Interface
from zope.app.interfaces.browser.form import IBrowserWidget
from zope.app.interfaces.forms import WidgetInputError, ConversionError
from zope.app.form.widget import Widget
from zope.publisher.browser import BrowserView
from zope.component import getService
from zope.schema.interfaces import ValidationError
from zope.component.exceptions import ComponentLookupError
from xml.sax.saxutils import quoteattr

class InterfaceWidget(Widget, BrowserView):
    __implements__ = IBrowserWidget

    def haveData(self):
        if self.name in self.request.form:
            v = self.request.form[self.name]
            return v and (v == 'None' or nameToInterface(self.context, v))
        return False
   
    def getData(self, optional=0):
        field = self.context
        value = self.request.form.get(self.name, self) # self used as marker
        if value is self or value == '':
            # No user input
            if field.required and not optional:
                raise MissingInputError(field.__name__, field.title,
                                        'the field is required')
            return field.default
        if value == 'None':
            value = None
        else:
            try:
                value = nameToInterface(field, value)
            except ComponentLookupError:
                # XXX this code path needs a test!
                # Convert to conversion error
                exc = ConversionError(sys.exc_info()[1])
                raise ConversionError, exc, sys.exc_info()[2]

        if not optional:
            try:
                field.validate(value)
            except ValidationError, v:
                raise WidgetInputError(self.context.__name__,
                                       self.title, str(v))

        return value
        
    def __call__(self):
        name = self.name
        search_name = name + ".search"
        search_string = self.request.form.get(search_name, '')

        value = self.request.form.get(self.name, self) # self used as marker
        
        field = self.context
        service = getService(field.context, "Interfaces")
        base = field.basetype
        include_none = base is None
        if base == Interface:
            base = None
        interfaces = list(service.searchInterface(search_string, base=base))
        interfaces.sort()
        interfaces = map(interfaceToName, interfaces)
        # Only include None if there is no search string, and include_none
        # is True
        # XXX need test for this
        if include_none and not search_string:
            interfaces = ['None'] + interfaces

        if self._data is None:
            selected = self.getData(1)
        else:
            selected = self._data

        # if nothing selected in the form...
        if value is self:
            selected = None
        else:
            selected = interfaceToName(selected)

        return renderInterfaceSelect(
                interfaces, selected, search_name, search_string, name)

    def hidden(self):
        'See IBrowserWidget'
        if self._data is None:
            data = self.getData(1)
        else:
            data = self._data
        if data is None:
            data = 'None'
        return ('<input type="hidden" name="%s" value="%s" />'
                        % (self.name, interfaceToName(data))
                        )
       
    def label(self):
        return '<label for="%s">%s</label>' % (
            self.name,
            self.title,
            )

    def row(self):
        return "<td>%s</td><td>%s</td>" % (self.label(), self())

    # --- deprecated methods of IBrowserWidget

    def renderHidden(self, value):
        'See IBrowserWidget'
        raise NotImplementedError

    def render(self, value):
        'See IBrowserWidget'
        raise NotImplementedError


class MultiInterfaceWidget(Widget, BrowserView):

    __implements__ = IBrowserWidget

    # Names used:
    #
    #  name.i0, name.i1, ...  the value of the interfaces
    #  name.search.i0, ...    the search box for that interface
    #  
    def haveData(self):
        name_i = self.name+'.i'
        field = self.context
        for k,v in self.request.form.iteritems():
            if k.startswith(name_i):
                if v and (v == 'None' or nameToInterface(field, v)):
                    return True
        return False

    def getData(self, optional=0):
        field = self.context
        name_i = self.name+'.i'
        items_sorted = self.request.form.items()
        items_sorted.sort()
        # values will be sorted in key order
        values = [v
                  for k,v in items_sorted
                  if k.startswith(name_i)]
        if not values:
            # No user input
            if field.required and not optional:
                raise MissingInputError(field.__name__, field.title,
                                        'the field is required')
            return field.default

        try:
            values = tuple([nameToInterface(field, value) for value in values])
        except ComponentLookupError:
            # Convert to conversion error
            # XXX this code path needs to be tested!
            exc = ConversionError(sys.exc_info()[1])
            raise ConversionError, exc, sys.exc_info()[2]

        if not optional:
            try:
                field.validate(values)
            except ValidationError, v:
                raise WidgetInputError(self.context.__name__,
                                       self.title, str(v))
        return values

    def __call__(self):
        'See IBrowserWidget'
        field = self.context
        form = self.request.form
        name = self.name
        name_i = name+'.i'
        name_search_i = name+'.search.i'
        
        service = getService(field.context, "Interfaces")
        base = field.basetype
        include_none = base is None
        if base == Interface:
            base = None

        if self._data is None:  # no data has been set with Widget.setData(),
                                # so use the data in the form
            
            # If a search term is entered, that interface selection remains.
            # If an interface is selected, that interface selection remains.
            # Remove all others.
            # Make sure there is at least one empty selection.
            # Make sure there are at least two selections in total.

            selections = {}  # index:[search, value]
            for k,v in form.iteritems():
                if k.startswith(name_i):
                    index = int(k[len(name_i):])
                    selection = selections.setdefault(index, ['', ''])
                    selection[1] = v
                elif k.startswith(name_search_i):
                    index = int(k[len(name_search_i):])
                    selection = selections.setdefault(index, ['', ''])
                    selection[0] = v.strip()

            first_is_blank = False
            # remove all of the selections that have no search and no value
            for k,(s,v) in selections.items():
                if s == v == '':
                    del selections[k]

            if selections:
                selections = selections.items()
                selections.sort()

                # If the first selection really was blank, then remember this
                # fact. We'll use it later if we need to add in an extra
                # selection box: we can add it at the beginning to preserve
                # the order as the user might expect.
                if selections[0][0] != 0:
                    first_is_blank = True
                
                # get just [search, value], and discard the keys
                selections = [v for k,v in selections]
                # XXX is validation here really needed?
                field.validate(tuple([nameToInterface(field, v)
                                      for s,v in selections
                                      if v != '']))
            else:  # otherwise, use the default
                selections = [('', interfaceToName(interface))
                              for interface in field.default]
        else:
            # data has been set with Widget.setData()
            selections = [('', interfaceToName(interface))
                          for interface in self._data]
                          
        # If there are no empty values, add one extra empty selection
        if not [1 for s,v in selections if v == '']:
            # if first_is_blank, put the empty selection at the start
            if first_is_blank:
                selections = [['', None]] + selections
            else:
                selections.append(['', None])
        # If there is only one value, add another one. We want at least
        # two values so that it is obvious this is a multi-value selection.
        if len(selections) == 1:
            selections.append(['', None])
        rendered_selections = []
        count = 0
        for search, value in selections:
            interfaces = list(service.searchInterface(search, base=base))
            interfaces.sort()
            interfaces = map(interfaceToName, interfaces)
            if include_none and not search:
                interfaces = ['None'] + interfaces
            search_name = '%s.search.i%s' % (name, count)
            rendered_selections.append(
                renderInterfaceSelect(interfaces, value, search_name,
                                      search, '%s.i%s' % (name, count))
                )
            count += 1

        HTML = ('Use refresh to enter more interfaces<br>' +
                '<br>'.join(rendered_selections))
        return HTML

    def hidden(self):
        'See IBrowserWidget'
        if self._data is None:
            data = self.getData(1)
        else:
            data = self._data
        name = self.name
        elements = ['<input type="hidden" name="%s" value="%s" />'
                        % (name, interfaceToName(interface))
                    for interface in data]
        return ''.join(elements)
       
    def label(self):
        return '<label for="%s">%s</label>' % (
            self.name,
            self.title,
            )

    def row(self):
        return "<td>%s</td><td>%s</td>" % (self.label(), self())

    # --- deprecated methods of IBrowserWidget

    def renderHidden(self, value):
        'See IBrowserWidget'
        raise NotImplementedError

    def render(self, value):
        'See IBrowserWidget'
        raise NotImplementedError

            
class InterfaceDisplayWidget(InterfaceWidget):
    def __call__(self):
        if self._data is None:
            data = self.getData(1)
        else:
            data = self._data
        return interfaceToName(data)

class MultiInterfaceDisplayWidget(MultiInterfaceWidget):
    def __call__(self):
        if self._data is None:
            data = self.getData(1)
        else:
            data = self._data
        return ', '.join([interfaceToName(interface) for interface in data])

def renderInterfaceSelect(
        interfaces, selected, search_name, search_string, select_name):
    """interfaces is a sequence, all of the other args are strings"""
    options = ['<option value="">---select interface---</option>']
    for interface in interfaces:
        if interface == 'None':
            options.append('<option value="None"%s>Anything</option>'
                           % (interface == selected and ' selected' or '')
                           )
        else:
            options.append('<option value="%s"%s>%s</option>'
                           % (interface,
                              interface == selected and ' selected' or '',
                              interface)
                           )
    # XXX need unit test for use of quoteattr for search string
    search_field = '<input type="text" name="%s" value=%s>' % (
        search_name, quoteattr(search_string))
    select_field = '<select name="%s">%s</select>'  % (
        select_name, ''.join(options))

    HTML = search_field + select_field
    return HTML

def nameToInterface(context, name):
    if name is 'None':
        return None
    service = getService(context, "Interfaces")
    return service.getInterface(name)

def interfaceToName(interface):
    if interface is None:
        return 'None'
    return interface.__module__ + '.' + interface.__name__
