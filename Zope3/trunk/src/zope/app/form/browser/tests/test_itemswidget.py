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
"""Select Widget Tests

$Id$
"""
import unittest

from zope.interface import Interface, implements
from zope.schema import Choice, List
from zope.publisher.browser import TestRequest

from zope.app.form.interfaces import WidgetInputError
from zope.app.form.browser.itemswidgets import ItemsWidgetBase
from zope.app.form.browser.itemswidgets import ItemDisplayWidget
from zope.app.form.browser.itemswidgets import ItemsMultiDisplayWidget
from zope.app.form.browser.itemswidgets import ListDisplayWidget
from zope.app.form.browser.itemswidgets import SetDisplayWidget
from zope.app.form.browser.itemswidgets import ItemsEditWidgetBase
from zope.app.form.browser.itemswidgets import SelectWidget, DropdownWidget
from zope.app.form.browser.itemswidgets import RadioWidget
from zope.app.form.browser.itemswidgets import ItemsMultiEditWidgetBase
from zope.app.form.browser.itemswidgets import MultiSelectWidget
from zope.app.form.browser.itemswidgets import MultiCheckBoxWidget
from zope.app.form.browser.tests.support import VerifyResults
from zope.app.tests.placelesssetup import PlacelessSetup 

class ICollector(Interface):
    choice = Choice(
        title=u"Number",
        description=u"The Number",
        values=['one', 'two', 'three'],
        required=True)

    numbers = List(
        title=u"Numbers",
        description=u"The Numbers",
        value_type=choice,
        required=False)


class Collector(object):
    implements(ICollector)

    def __init__(self, numbers=None):
        self.numbers = numbers or []


class ItemsWidgetBaseTest(VerifyResults, PlacelessSetup, unittest.TestCase):

    _widget = ItemsWidgetBase
    _field = ICollector.get('choice')
    _vocabulary = _field.vocabulary

    def _makeWidget(self, form=None, nums=None):
        request = TestRequest(form=form or {})
        collector = Collector(nums)
        bound = self._field.bind(collector)
        return self._widget(bound, self._vocabulary, request) 

    def test_setPrefix(self):
        widget = self._makeWidget()
        name = self._field.getName()
        # Default prefix
        self.assertEqual(widget._prefix, 'field.')
        self.assertEqual(widget.name, 'field.%s' %name)
        self.assertEqual(widget.empty_marker_name,
                         'field.%s-empty-marker' %name)
        # Declaring custom prefix
        widget.setPrefix('foo')
        self.assertEqual(widget._prefix, 'foo.')
        self.assertEqual(widget.name, 'foo.%s' %name)
        self.assertEqual(widget.empty_marker_name,
                         'foo.%s-empty-marker' %name)

    def test_convertTokensToValues(self):
        widget = self._makeWidget()
        self.assertEqual(widget.convertTokensToValues(['one', 'two']),
                         ['one', 'two'])


class ItemDisplayWidgetTest(ItemsWidgetBaseTest):
    
    _widget = ItemDisplayWidget

    def test_setVocabulary(self):
        widget = self._makeWidget()
        self.assert_(widget.vocabulary is not None)
        self.assertEqual(widget.vocabulary, self._field.vocabulary)

    def test__call__(self):
        widget = self._makeWidget()
        self.assertEqual(widget(), '')        
        widget = self._makeWidget(form={'field.choice': 'one'})
        self.assertEqual(widget(), 'one')


class ItemsMultiDisplayWidgetTest(ItemsWidgetBaseTest):
    
    _widget = ItemsMultiDisplayWidget
    _field = ICollector.get('numbers')    
    _vocabulary = _field.value_type.vocabulary
    _tag = 'ol'

    def test__call__(self):
        widget = self._makeWidget()
        self.assertEqual(widget(), '')        
        widget = self._makeWidget(form={'field.numbers': ['one', 'two']})
        self.assertEqual(
            widget(),
            '<%s class="textType" '
            'id="field.numbers" '
            'name="field.numbers" '
            'type="text" >'
            '<li>one</li>\n<li>two</li>'
            '</%s>' %(self._tag, self._tag))
        
    def test_renderItems(self):
        widget = self._makeWidget()
        self.assertEqual(
            widget.renderItems(['one', 'two']),
            [u'<li>one</li>', u'<li>two</li>'])
        self.assertRaises(LookupError, widget.renderItems, 'one')
        self.assertRaises(TypeError, widget.renderItems, 1)


class ListDisplayWidgetTest(ItemsMultiDisplayWidgetTest):
    _widget = ListDisplayWidget
    _tag = 'ol'


class SetDisplayWidgetTest(ItemsMultiDisplayWidgetTest):
    _widget = SetDisplayWidget
    _tag = 'ul'


class ItemsEditWidgetBaseTest(ItemsWidgetBaseTest):

    _widget = ItemsEditWidgetBase

    def test_div(self):
        widget = self._makeWidget()
        self.assertEqual(widget._div('', ''), '')
        self.assertEqual(widget._div('foo', ''), '')
        self.assertEqual(widget._div('', 'bar'), '<div>\nbar\n</div>')
        self.assertEqual(widget._div('foo', 'bar'),
                         '<div class="foo">\nbar\n</div>')
        self.assertEqual(widget._div('foo', 'bar', style='blah'),
                         '<div class="foo" style="blah">\nbar\n</div>')

    def test_renderItem(self):
        widget = self._makeWidget()
        self.assertEqual(widget.renderItem('', 'Foo', 'foo', '', None),
                         '<option value="foo">Foo</option>')
        self.assertEqual(widget.renderItem('', 'Foo', 'foo', '', 'klass'),
                         '<option class="klass" value="foo">Foo</option>')

    def test_renderSelectedItem(self):
        widget = self._makeWidget()
        self.verifyResult(
          widget.renderSelectedItem('', 'Foo', 'foo', '', None),
          ['<option', 'value="foo"', 'selected="selected"', '>Foo</option>'])
        self.verifyResult(
          widget.renderSelectedItem('', 'Foo', 'foo', '', 'klass'),
          ['<option', 'class="klass"', 'value="foo"', 'selected="selected"',
           '>Foo</option>'])

    def test_renderItemsWithValues(self):
        widget = self._makeWidget()
        self.assertEqual(
            widget.renderItemsWithValues(['one', 'two']),
            [u'<option selected="selected" value="one">one</option>',
             u'<option selected="selected" value="two">two</option>',
             u'<option value="three">three</option>'])             
        self.assertEqual(
            widget.renderItemsWithValues([]),
            [u'<option value="one">one</option>',
             u'<option value="two">two</option>',
             u'<option value="three">three</option>'])             

    def test_error(self):
        widget = self._makeWidget(form={'field.choice': 'ten'})
        widget.setPrefix('field.')
        widget._getFormValue()
        self.assert_(isinstance(widget._error, WidgetInputError))

class SelectWidgetTest(ItemsEditWidgetBaseTest):

    _widget = SelectWidget
    _size = 5

    def test__call__(self):
        widget = self._makeWidget(form={'field.choice': 'one'})
        widget.setPrefix('field.')
        widget.context.required = False
        self.assertEqual(
            widget(),
            '<div id="field.choice">\n'
            '<div class="value">\n'
            '<select name="field.choice" size="%i" >\n'
            '<option value="">(no value)</option>\n'
            '<option selected="selected" value="one">one</option>\n'
            '<option value="two">two</option>\n'
            '<option value="three">three</option>\n'
            '</select>\n</div>\n'
            '<input name="field.choice-empty-marker" '
            'type="hidden" value="1" />\n</div>' %self._size)

    def test_renderValue(self):
        widget = self._makeWidget()
        widget.setPrefix('field.')
        self.assertEqual(
            widget.renderValue('one'),
            '<select name="field.choice" size="%i" >\n'
            '<option selected="selected" value="one">one</option>\n'
            '<option value="two">two</option>\n'
            '<option value="three">three</option>\n'
            '</select>' %self._size)

    def test_renderItems(self):
        widget = self._makeWidget()
        widget.setPrefix('field.')
        self.assertEqual(
            widget.renderItems('one'),
            [u'<option selected="selected" value="one">one</option>',
             u'<option value="two">two</option>',
             u'<option value="three">three</option>'])
        self.assertEqual(
            widget.renderItems('two'),
            [u'<option value="one">one</option>',
             u'<option selected="selected" value="two">two</option>',
             u'<option value="three">three</option>'])
        self.assertEqual(
            widget.renderItems(None),
            [u'<option value="one">one</option>',
             u'<option value="two">two</option>',
             u'<option value="three">three</option>'])

    def test_renderItems_notRequired(self):
        widget = self._makeWidget()
        widget.setPrefix('field.')
        widget.context.required = False
        self.assertEqual(
            widget.renderItems([]),
            [u'<option value="">(no value)</option>',
             u'<option value="one">one</option>',
             u'<option value="two">two</option>',
             u'<option value="three">three</option>'])

    def test_renderItems_firstItem(self):
        widget = self._makeWidget()
        widget.setPrefix('field.')
        widget.firstItem = True
        self.assertEqual(
            widget.renderItems(None),
            [u'<option selected="selected" value="one">one</option>',
             u'<option value="two">two</option>',
             u'<option value="three">three</option>'])


class DropdownWidgetTest(SelectWidgetTest):

    _widget = DropdownWidget
    _size = 1


class RadioWidgetTest(ItemsEditWidgetBaseTest):

    _widget = RadioWidget

    def test_renderItem(self):
        widget = self._makeWidget()
        self.verifyResult(
            widget.renderItem('', 'Foo', 'foo', 'bar', None),
            ['<input', 'type="radio"', 'name="bar"', 'value="foo"',
             'class="radioType"', '>&nbsp;Foo'])
        self.verifyResult(
            widget.renderItem('bar', 'Foo', 'foo', 'bar', 'klass'),
            ['<input', 'type="radio"', 'name="bar"', 'value="foo"',
             'class="klass radioType"', '>&nbsp;Foo'])

    def test_renderSelectedItem(self):
        widget = self._makeWidget()
        self.verifyResult(
            widget.renderSelectedItem('', 'Foo', 'foo', 'bar', 'klass'),
            ['<input', 'type="radio"', 'name="bar"', 'value="foo"',
             'checked="checked"', '>&nbsp;Foo'])
        self.verifyResult(
            widget.renderSelectedItem('', 'Foo', 'foo', 'bar', 'klass'),
            ['<input', 'type="radio"', 'name="bar"', 'value="foo"',
             'class="klass radioType"', 'checked="checked"', '>&nbsp;Foo'])

    def test_renderItemsWithValues(self):
        widget = self._makeWidget()
        items = widget.renderItemsWithValues(['one'])
        values = ['one', 'two', 'three']
        for item in items:
            index = items.index(item)
            self.verifyResult(
                item,
                ['<input', 'class="radioType"', 'name="field.choice"',
                 'id="field.choice.%i' %index, 'type="radio"',
                 'value="%s"' %values[index], '&nbsp;%s' %values[index]])
        self.verifyResult(items[0], ['checked="checked"'])

    def test_renderItems(self):
        widget = self._makeWidget()
        items = widget.renderItems('one')
        values = ['one', 'two', 'three']
        for item in items:
            index = items.index(item)
            self.verifyResult(
                item,
                ['<input', 'class="radioType"', 'name="field.choice"',
                 'id="field.choice.%i' %index, 'type="radio"',
                 'value="%s"' %values[index], '&nbsp;%s' %values[index]])
        self.verifyResult(items[0], ['checked="checked"'])

    def test_renderItems_notRequired(self):
        widget = self._makeWidget()
        widget.context.required = False
        items = widget.renderItems([])
        values = ['(no value)', 'one', 'two', 'three']
        for item in items:
            index = items.index(item)
            self.verifyResult(
                item,
                ['<input', 'class="radioType"', 'name="field.choice"',
                 'type="radio"', '&nbsp;%s' %values[index]])

    def test_renderItems_firstItem(self):
        widget = self._makeWidget()
        widget.firstItem = True
        items = widget.renderItems(None)
        values = ['one', 'two', 'three']
        for item in items:
            index = items.index(item)
            self.verifyResult(
                item,
                ['<input', 'class="radioType"', 'name="field.choice"',
                 'id="field.choice.%i"' %index, 'type="radio"',
                 '&nbsp;%s' %values[index]])
        self.verifyResult(items[0], ['checked="checked"'])

    def test_renderValue(self):
        widget = self._makeWidget()
        self.verifyResult(widget.renderValue(None), ['<br /><input'])
        widget.orientation='horizontal'
        self.verifyResult(widget.renderValue(None), ['&nbsp;&nbsp;<input'])


class ItemsMultiEditWidgetBaseTest(ItemsEditWidgetBaseTest):

    _widget = ItemsMultiEditWidgetBase
    _field = ICollector.get('numbers')
    _vocabulary = _field.value_type.vocabulary

    def test_renderValue(self):
        widget = self._makeWidget()
        self.verifyResult(
            widget.renderValue(['one', 'two']),
            ['<select', 'multiple="multiple"', 'name="field.numbers:list"',
             'size="5"', '><option', 'selected="selected"', 'value="one"',
             '>one</option>\n', 'value="two"', '>two</option>\n',
             'value="three"', '>three</option>', '</select>'])

    def test_error(self):
        widget = self._makeWidget(form={'field.numbers': ['ten']})
        widget.setPrefix('field.')
        widget._getFormValue()
        self.assert_(isinstance(widget._error, WidgetInputError))


class MultiSelectWidgetTest(ItemsMultiEditWidgetBaseTest):

    _widget = MultiSelectWidget


class MultiCheckBoxWidgetTest(ItemsMultiEditWidgetBaseTest):

    _widget = MultiCheckBoxWidget

    def test_renderItem(self):
        widget = self._makeWidget()
        self.verifyResult(
            widget.renderItem('', 'Foo', 'foo', 'bar', None),
            ['<input', 'type="checkbox"', 'name="bar"', 'value="foo"',
             'class="checkboxType"', '>&nbsp;Foo'])
        self.verifyResult(
            widget.renderItem('bar', 'Foo', 'foo', 'bar', 'klass'),
            ['<input', 'type="checkbox"', 'name="bar"', 'value="foo"',
             'class="klass checkboxType"', '>&nbsp;Foo'])

    def test_renderSelectedItem(self):
        widget = self._makeWidget()
        self.verifyResult(
            widget.renderSelectedItem('', 'Foo', 'foo', 'bar', 'klass'),
            ['<input', 'type="checkbox"', 'name="bar"', 'value="foo"',
             'checked="checked"', '>&nbsp;Foo'])
        self.verifyResult(
            widget.renderSelectedItem('', 'Foo', 'foo', 'bar', 'klass'),
            ['<input', 'type="checkbox"', 'name="bar"', 'value="foo"',
             'class="klass checkboxType"', 'checked="checked"', '>&nbsp;Foo'])

    def test_renderValue(self):
        widget = self._makeWidget()
        self.verifyResult(widget.renderValue(None), ['<br /><input'])
        widget.orientation='horizontal'
        self.verifyResult(widget.renderValue(None), ['&nbsp;&nbsp;<input'])

    def test_renderItemsWithValues(self):
        widget = self._makeWidget()
        items = widget.renderItemsWithValues(['one'])
        for item in items:
            index = items.index(item)
            self.verifyResult(
                item,
                ['<input', 'class="checkboxType',
                 'id="field.numbers.%i"' %index, 'type="checkbox"', '/>&nbsp;'])

        self.verifyResult(items[0],
                          ['checked="checked"', '/>&nbsp;one'])


def test_suite():
    suite = unittest.makeSuite(ItemDisplayWidgetTest)
    suite.addTest(unittest.makeSuite(ItemsMultiDisplayWidgetTest))
    suite.addTest(unittest.makeSuite(ListDisplayWidgetTest))
    suite.addTest(unittest.makeSuite(SetDisplayWidgetTest))
    suite.addTest(unittest.makeSuite(ItemsEditWidgetBaseTest))
    suite.addTest(unittest.makeSuite(SelectWidgetTest))
    suite.addTest(unittest.makeSuite(DropdownWidgetTest))
    suite.addTest(unittest.makeSuite(RadioWidgetTest))
    suite.addTest(unittest.makeSuite(ItemsMultiEditWidgetBaseTest))
    suite.addTest(unittest.makeSuite(MultiSelectWidgetTest))
    suite.addTest(unittest.makeSuite(MultiCheckBoxWidgetTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
