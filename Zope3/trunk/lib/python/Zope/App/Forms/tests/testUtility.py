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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: testUtility.py,v 1.2 2002/10/28 23:52:31 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Interface import Interface
from Zope.Schema import Text
from Zope.App.Forms.Views.Browser.Widget import TextWidget
from Zope.ComponentArchitecture.GlobalViewService \
     import provideView, setDefaultViewName
from Zope.Schema.IField import IText
from Zope.App.Forms.Exceptions import WidgetsError
from Zope.App.Forms.Utility import setUpWidget, setUpWidgets, setUpEditWidgets
from Zope.App.Forms.Utility import getWidgetsData, getWidgetsDataForContent
from Zope.Schema.Exceptions import ValidationError


class I(Interface):
    title = Text(title=u"Title")
    description = Text(title=u"Description")

class I2(Interface):
    title = Text(title=u"Title", required=True)
    description = Text(title=u"Description", required=True)

class C:
    __implements__ = I

class C2:
    __implements__ = I2

class W(TextWidget):

    def setData(self, v):
        self.context.validate(v)
        self._data = v

    def __call__(self):
        name = self.getName()
        if name in self.request:
            v = self.request[name]
        else:
            v = getattr(self, '_data', None) or ''

        return unicode(name) + u': ' + v

    def getData(self):
        v = self.request.get(self.getName())
        if not v and self.context.required:
            raise ValidationError("%s required" % self.getName())
        return v

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        setDefaultViewName(IText, IBrowserPresentation, 'normal')
        provideView(IText, 'normal', IBrowserPresentation, W)

    def test_setUpWidget(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        setUpWidget(view, 'title', I['title'])
        self.assertEqual(view.title(), u'title: ')
        self.assertEqual(view.title.getData(), None)

    def test_setUpWidget_w_request_data(self):
        c = C()
        request = TestRequest()
        request.form['title'] = u'xxx'
        view = BrowserView(c, request)
        setUpWidget(view, 'title', I['title'])
        self.assertEqual(view.title(), u'title: xxx')
        self.assertEqual(view.title.getData(), u'xxx')

    def test_setUpWidget_w_request_data_and_initial_data(self):
        c = C()
        request = TestRequest()
        request.form['title'] = u'xxx'
        view = BrowserView(c, request)
        setUpWidget(view, 'title', I['title'], u'yyy')
        self.assertEqual(view.title(), u'title: xxx')
        self.assertEqual(view.title.getData(), u'xxx')

    def test_setUpWidget_w_initial_data(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        setUpWidget(view, 'title', I['title'], u'yyy')
        self.assertEqual(view.title(), u'title: yyy')
        self.assertEqual(view.title.getData(), None)

    def test_setUpWidget_w_bad_initial_data(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        self.assertRaises(ValidationError,
                          setUpWidget, view, 'title', I['title'], 'yyy')

    def test_setUpWidget_w_custom_widget(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        view.title = w = W(I['title'], request) 
        setUpWidget(view, 'title', I['title'], u'yyy')
        self.assertEqual(view.title(), u'title: yyy')
        self.assertEqual(view.title.getData(), None)
        self.assertEqual(view.title, w) 
    
    def test_setupWidgets(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        setUpWidgets(view, I)
        self.assertEqual(view.title(), u'title: ')
        self.assertEqual(view.description(), u'description: ')
    
    def test_setupWidgets_w_initial_data_and_custom_widget(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        view.title = w = W(I['title'], request) 
        setUpWidgets(view, I, title=u"ttt", description=u"ddd")
        self.assertEqual(view.title(), u'title: ttt')
        self.assertEqual(view.description(), u'description: ddd')
        self.assertEqual(view.title, w) 

    def test_setupEditWidgets_w_custom_widget(self):
        c = C()
        c.title = u'ct'
        c.description = u'cd'
        request = TestRequest()
        view = BrowserView(c, request)
        view.title = w = W(I['title'], request) 
        setUpEditWidgets(view, I)
        self.assertEqual(view.title(), u'title: ct')
        self.assertEqual(view.description(), u'description: cd')
        self.assertEqual(view.title, w) 

    def test_setupEditWidgets_w_other_data(self):
        c = C()
        c2 = C()
        c2.title = u'ct'
        c2.description = u'cd'
        request = TestRequest()
        view = BrowserView(c, request)
        setUpEditWidgets(view, I)
        self.assertEqual(view.title(), u'title: ')
        self.assertEqual(view.description(), u'description: ')
        setUpEditWidgets(view, I, c2)
        self.assertEqual(view.title(), u'title: ct')
        self.assertEqual(view.description(), u'description: cd')
        
        view = BrowserView(c2, request)
        setUpEditWidgets(view, I)
        self.assertEqual(view.title(), u'title: ct')
        self.assertEqual(view.description(), u'description: cd')

    def test_getSetupWidgets_w_form_data(self):
        c = C()
        request = TestRequest()
        request.form['title'] = u'ft'
        view = BrowserView(c, request)
        setUpWidgets(view, I, title=u"ttt", description=u"ddd")
        self.assertEqual(view.title(), u'title: ft')
        self.assertEqual(view.description(), u'description: ddd')
        

    def test_getWidgetsData(self):
        c = C()
        request = TestRequest()
        request.form['title'] = u'ft'
        request.form['description'] = u'fd'
        view = BrowserView(c, request)
        setUpWidgets(view, I, title=u"ttt", description=u"ddd")
        self.assertEqual(getWidgetsData(view, I),
                         {'title': u'ft',
                          'description': u'fd'})

    def test_getWidgetsDataForContent(self):
        c = C()
        request = TestRequest()
        request.form['title'] = u'ft'
        request.form['description'] = u'fd'
        view = BrowserView(c, request)
        setUpWidgets(view, I, title=u"ttt", description=u"ddd")
        getWidgetsDataForContent(view, I)
        
        self.assertEqual(c.title, u'ft')
        self.assertEqual(c.description, u'fd')

        c2 = C()
        request.form['title'] = u'ftt'
        request.form['description'] = u'fdd'
        getWidgetsDataForContent(view, I, c2)
        
        self.assertEqual(c.title, u'ft')
        self.assertEqual(c.description, u'fd')
        
        self.assertEqual(c2.title, u'ftt')
        self.assertEqual(c2.description, u'fdd')

    def testErrors(self):
        c = C2()
        c.title = u'old title'
        c.description = u'old description'
        request = TestRequest()
        request.form['title'] = u'ft'
        view = BrowserView(c, request)
        setUpWidgets(view, I2, title=u"ttt", description=u"ddd")
        try:
            getWidgetsDataForContent(view, I2)
        except WidgetsError, v:
            self.assertEqual(str(v), "description required")
        else:
            self.assert_(0, "No errors were raised")

        self.assertEqual(c.title, u'old title') 
        self.assertEqual(c.description, u'old description') 

        request = TestRequest()
        view = BrowserView(c, request)
        setUpWidgets(view, I2, title=u"ttt", description=u"ddd")
        try:
            getWidgetsDataForContent(view, I2)
        except WidgetsError, v:
            self.assertEqual(len(v), 2)

        self.assertEqual(c.title, u'old title') 
        self.assertEqual(c.description, u'old description') 
            
        


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
