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
"""Browser widgets for sequences

$Id$
"""
__docformat__ = 'restructuredtext'

import re
from zope.interface import implements
from zope.i18n import translate

from zope.app import zapi
from zope.app.form.interfaces import IInputWidget
from zope.app.form import InputWidget
from zope.app.form.browser.widget import BrowserWidget
from zope.app.i18n import ZopeMessageIDFactory as _

class SequenceWidget(BrowserWidget, InputWidget):
    """A widget baseclass for a sequence of fields.

    subwidget  - Optional CustomWidget used to generate widgets for the
                 items in the sequence
    """

    implements(IInputWidget)

    _type = tuple    
    _data = () # pre-existing sequence items (from setRenderedValue)

    def __init__(self, context, value_type, request, subwidget=None):
        super(SequenceWidget, self).__init__(context, request)

        self.subwidget = None

    def __call__(self):
        """Render the widget
        """
        assert self.context.value_type is not None

        render = []

        # length of sequence info
        sequence = list(self._generateSequence())
        num_items = len(sequence)
        min_length = self.context.min_length
        max_length = self.context.max_length

        # ensure minimum number of items in the form
        if num_items < min_length:
            for i in range(min_length - num_items):
                sequence.append(None)
        num_items = len(sequence)

        # generate each widget from items in the sequence - adding a
        # "remove" button for each one
        for i in range(num_items):
            value = sequence[i]
            render.append('<tr><td>')
            if num_items > min_length:
                render.append(
                    '<input type="checkbox" name="%s.remove_%d" />' % (
                    self.name, i)
                    )
            widget = self._getWidget(i)
            widget.setRenderedValue(value)
            render.append(widget() + '</td></tr>')

        # possibly generate the "remove" and "add" buttons
        buttons = ''
        if render and num_items > min_length:
            remove_botton_name = 'remove-selected-items-of-seq-' + self.name
            button_label = _('remove-selected-items', "Remove selected items")
            button_label = translate(button_label, context=self.request,
                                     default=button_label)
            buttons += '<input type="submit" value="%s" name="%s"/>' % (
                button_label, remove_botton_name)
        if max_length is None or num_items < max_length:
            field = self.context.value_type
            button_label = _('Add %s')
            button_label = translate(button_label, context=self.request,
                                     default=button_label)
            button_label = button_label % (field.title or field.__name__)
            buttons += '<input type="submit" name="%s.add" value="%s" />' % (
                self.name, button_label)
        if buttons:
            render.append('<tr><td>%s</td></tr>' % buttons)

        return '<table border="0">' + ''.join(render) + '</table>'

    def _getWidget(self, i):
        field = self.context.value_type
        if self.subwidget:
            widget = self.subwidget(field, self.request)
        else:
            widget = zapi.getViewProviding(field, IInputWidget, self.request)
        widget.setPrefix('%s.%d.'%(self.name, i))
        return widget

    def hidden(self):
        ''' Render the list as hidden fields '''
        # length of sequence info
        sequence = self._generateSequence()
        num_items = len(sequence)
        min_length = self.context.min_length

        # ensure minimum number of items in the form
        if num_items < min_length:
            for i in range(min_length - num_items):
                sequence.append(None)
        num_items = len(sequence)

        # generate hidden fields for each value
        s = ''
        for i in range(num_items):
            value = sequence[i]
            widget = self._getWidget(i)
            widget.setRenderedValue(value)
            s += widget.hidden()
        return s

    def getInputValue(self):
        """Return converted and validated widget data.

        If there is no user input and the field is required, then a
        ``MissingInputError`` will be raised.

        If there is no user input and the field is not required, then
        the field default value will be returned.

        A ``WidgetInputError`` is returned in the case of one or more
        errors encountered, inputting, converting, or validating the data.
        """
        sequence = self._generateSequence()
        # validate the input values
        for value in sequence:
            self.context.value_type.validate(value)
        return self._type(sequence)

    # TODO: applyChanges isn't reporting "change" correctly (we're
    # re-generating the sequence with every edit, and need to be smarter)
    def applyChanges(self, content):
        field = self.context
        value = self.getInputValue()
        change = field.query(content, self) != value
        if change:
            field.set(content, value)
        return change

    def hasInput(self):
        """Is there input data for the field

        Return ``True`` if there is data and ``False`` otherwise.
        """
        return len(self._generateSequence()) != 0

    def setRenderedValue(self, value):
        """Set the default data for the widget.

        The given value should be used even if the user has entered
        data.
        """
        # the current list of values derived from the "value" parameter
        self._data = value

    def _generateSequence(self):
        """Take sequence info in the self.request and _data.
        """
        len_prefix = len(self.name)
        adding = False
        removing = []
        subprefix = re.compile(r'(\d+)\.(.*)$')
        remove_botton_name = 'remove-selected-items-of-seq-' + self.name
        if self.context.value_type is None:
            return []

        # pre-populate
        found = {}
        if self._data is not None:
            found = dict(enumerate(self._data))

        # now look through the request for interesting values
        for key in self.request.keys():
            if not key.startswith(self.name):
                continue
            token = key[len_prefix+1:]        # skip the '.'
            if token == 'add':
                # append a new blank field to the sequence
                adding = True
            elif token.startswith('remove_') and \
                    remove_botton_name in self.request:
                # remove the index indicated if we press 
                # the "Remove selected items" button.
                # Otherwise we delete the items if we check
                # the box and push the "Change" button.
                removing.append(int(token[7:]))
            else:
                match = subprefix.match(token)
                if match is None:
                    continue
                # key refers to a sub field
                i = int(match.group(1))

                # find a widget for the sub-field and use that to parse the
                # request data
                widget = self._getWidget(i)
                value = widget.getInputValue()
                found[i] = value

        # remove the indicated indexes
        for i in removing:
            del found[i]

        # generate the list, sorting the dict's contents by key
        items = found.items()
        items.sort()
        sequence = [value for key, value in items]

        # add an entry to the list if the add button has been pressed
        if adding:
            sequence.append(None)

        return sequence

class TupleSequenceWidget(SequenceWidget):
    pass

class ListSequenceWidget(SequenceWidget):
    _type = list
