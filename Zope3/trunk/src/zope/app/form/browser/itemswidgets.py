##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Browser widgets for items

$Id: itemswidgets.py,v 1.1 2004/03/17 17:35:02 philikon Exp $
"""
from zope.interface import implements
from zope.i18n import translate
from zope.proxy import removeAllProxies

from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser.widget import BrowserWidget, renderElement

ListTypes = list, tuple

class CheckBoxWidget(BrowserWidget):
    """A checkbox widget used to display Bool fields.
    
    For more detailed documentation, including sample code, see
    tests/test_checkboxwidget.py.
    """
    
    implements(IInputWidget)
    
    type = 'checkbox'
    default = 0
    extra = ''

    def __call__(self):
        data = self._showData()
        if data:
            kw = {'checked': None}
        else:
            kw = {}
        return "%s %s" % (
            renderElement(self.tag,
                          type='hidden',
                          name=self.name+".used",
                          id=self.name+".used",
                          value=""
                          ),
            renderElement(self.tag,
                             type=self.type,
                             name=self.name,
                             id=self.name,
                             cssClass=self.cssClass,
                             extra=self.extra,
                             **kw),
            )

    def _convert(self, value):
        return value == 'on'

    def _unconvert(self, value):
        return value and "on" or ""
        return value == 'on'

    def hasInput(self):
        return self.name + ".used" in self.request.form or \
            super(CheckBoxWidget, self).hasInput()

    def getInputValue(self):
        # When it's checked, its value is 'on'.
        # When a checkbox is unchecked, it does not appear in the form data.
        value = self.request.form.get(self.name, 'off')
        return value == 'on'

class ItemsWidget(BrowserWidget):
    """A widget that has a number of items in it."""
    implements(IInputWidget)

class SingleItemsWidget(ItemsWidget):
    """A widget with a number of items that has only a single
    selectable item."""
    
    default = ""
    firstItem = False

    def textForValue(self, value):
        '''Returns the text for the given value.

        Override this in subclasses.'''
        # The text could be a MessageID, in which case we should try to
        # translate it.
        return translate(self.context, value, context=self.request,
                         default=value)

    def renderItems(self, value):
        name = self.name
        # get items
        items = self.context.allowed_values

        # check if we want to select first item
        if (not value and getattr(self.context, 'firstItem', False)
            and len(items) > 0):
            value = items[0]

        cssClass = self.cssClass

        # FIXME: what if we run into multiple items with same value?
        rendered_items = []
        count = 0
        for item_value in items:
            item_text = self.textForValue(item_value)

            if item_value == value:
                rendered_item = self.renderSelectedItem(count,
                                                        item_text,
                                                        item_value,
                                                        name,
                                                        cssClass)
            else:
                rendered_item = self.renderItem(count,
                                                item_text,
                                                item_value,
                                                name,
                                                cssClass)

            rendered_items.append(rendered_item)
            count += 1

        return rendered_items

class ListWidget(SingleItemsWidget):
    """List widget."""
    
    size = 5

    def __call__(self):
        renderedItems = self.renderItems(self._showData())
        return renderElement('select',
                              name=self.name,
                              id=self.name,
                              cssClass=self.cssClass,
                              size=self.size,
                              contents="\n".join(renderedItems),
                              extra=self.extra)

    def renderItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              cssClass=cssClass)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              cssClass=cssClass, selected=None)


class RadioWidget(SingleItemsWidget):
    """Radio buttons widget."""
    
    orientation = "vertical"

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
        orientation = self.orientation
        if orientation == 'horizontal':
            return "&nbsp;&nbsp;".join(rendered_items)
        else:
            return '<br />'.join(rendered_items)

    def _renderItem(self, index, text, value, name, cssClass, checked):
        id = '%s.%s' % (name, index)
        if checked:
            element = renderElement('input',
                                    type="radio",
                                    cssClass=cssClass,
                                    name=name,
                                    id=id,
                                    value=value,
                                    checked=None)
        else:
            element = renderElement('input',
                                    type="radio",
                                    cssClass=cssClass,
                                    name=name,
                                    id=id,
                                    value=value)

        return '%s<label for="%s">%s</label>' % (element, id, text)

    def renderItem(self, index, text, value, name, cssClass):
        return self._renderItem(index, text, value, name, cssClass, False)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return self._renderItem(index, text, value, name, cssClass, True)

    def label(self):
        return translate(self.context, self.title, context=self.request,
                         default=self.title)

    def row(self):
        return ('<div class="%s"><label for="%s">%s</label></div>'
                '<div class="field" id="%s">%s</div>' % (
                self.labelClass(), self.name, self.label(), self.name, self()))
                

class MultiItemsWidget(ItemsWidget):
    """A widget with a number of items that has multiple selectable items."""
        
    default = []

    def _convert(self, value):
        if not value:
            return []
        if isinstance(value, ListTypes):
            return value
        return [value]

    def renderItems(self, value):
        # need to deal with single item selects
        value = removeAllProxies(value)

        if not isinstance(value, ListTypes):
            value = [value]
        name = self.name
        items = self.context.allowed_values
        cssClass = self.cssClass
        rendered_items = []
        count = 0
        for item in items:
            try:
                item_value, item_text = item
            except ValueError:
                item_value = item
                item_text = item

            if item_value in value:
                rendered_item = self.renderSelectedItem(count,
                                                        item_text,
                                                        item_value,
                                                        name,
                                                        cssClass)
            else:
                rendered_item = self.renderItem(count,
                                                item_text,
                                                item_value,
                                                name,
                                                cssClass)

            rendered_items.append(rendered_item)
            count += 1

        return rendered_items


class MultiListWidget(MultiItemsWidget):
    """List widget with multiple select."""

    size = 5

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
        return renderElement('select',
                              name=self.name,
                              id=self.name,
                              multiple=None,
                              cssClass=self.cssClass,
                              size=self.size,
                              contents="\n".join(rendered_items),
                              extra=self.extra)

    def renderItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              selected=None)


class MultiCheckBoxWidget(MultiItemsWidget):
    """Multiple checkbox widget."""

    orientation = "vertical"

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
        orientation = self.orientation
        if orientation == 'horizontal':
            return "&nbsp;&nbsp;".join(rendered_items)
        else:
            return "<br />".join(rendered_items)

    def renderItem(self, index, text, value, name, cssClass):
        return renderElement('input',
                              type="checkbox",
                              cssClass=cssClass,
                              name=name,
                              id=name,
                              value=value) + text

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return renderElement('input',
                              type="checkbox",
                              cssClass=cssClass,
                              name=name,
                              id=name,
                              value=value,
                              checked=None) + text
