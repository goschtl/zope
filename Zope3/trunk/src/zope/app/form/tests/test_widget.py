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
"""Generic Widget Tests

$Id: test_widget.py,v 1.8 2004/03/13 21:37:25 srichter Exp $
"""
from zope.testing.doctestunit import DocTestSuite
from unittest import TestSuite, main, makeSuite
from zope.app.form.widget import Widget, CustomWidgetFactory
from zope.app.form.interfaces import IWidget
from zope.interface.verify import verifyClass, verifyObject
from zope.schema import Text
from zope.publisher.browser import TestRequest
from zope.component.interfaces import IViewFactory
from zope.app.tests.placelesssetup import setUp, tearDown

class TestContext:
    __name__ = 'Test'
    title = 'My Test Context'
    description = 'A test context.'

class FooWidget(Widget):
    pass
    
context = TestContext()
request = TestRequest()

class TestWidget:
    """Tests basic widget characteristics.
    
    Widget implements IWidget:

        >>> verifyClass(IWidget, Widget)
        True
        >>> widget = Widget(context, request)
        >>> verifyObject(IWidget, widget)
        True
        
    The default values for widget are:
        
        >>> widget.name
        'field.Test'
        >>> widget.title
        'My Test Context'
        >>> widget.description
        'A test context.'
        >>> widget.visible
        True
        
    In the last example, the widget name consists of a prefix, a dot, and the
    field name. You can change the prefix used by the widget as follows:
        
        >>> widget.setPrefix('newprefix')
        >>> widget.name
        'newprefix.Test'
        
    To configure a widget, call setRenderedValue with a value that the
    widget should display:
        
        >>> widget.setRenderedValue('Render Me')
        
    The way a widget renders a value depends on the type of widget. E.g. a
    browser widget will render the specified value in HTML.
    """

class TestCustomWidgetFactory:
    """Tests the custom widget factory.
    
    Custom widgets can be created using a custom widget factory. Factories
    are used to assign attribute values to widgets they create:
        
        >>> factory = CustomWidgetFactory(FooWidget, bar='baz')
        >>> widget = factory(context, request)
        >>> isinstance(widget, FooWidget)
        True
        >>> widget.bar
        'baz'
    """

def test_suite():
    return TestSuite((
        DocTestSuite(setUp=setUp, tearDown=tearDown),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
