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

$Id: test_utility.py,v 1.12 2003/04/18 22:12:26 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.publisher.browser import BrowserView
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.interface import Interface, directlyProvides
from zope.schema import Text, accessors
from zope.app.browser.form.widget import TextWidget
from zope.component.view import provideView, setDefaultViewName
from zope.schema.interfaces import IText
from zope.app.interfaces.form import WidgetsError, MissingInputError
from zope.app.form.utility import setUpWidget, setUpWidgets, setUpEditWidgets
from zope.app.form.utility import getWidgetsData, getWidgetsDataForContent
from zope.app.form.utility import haveWidgetsData
from zope.schema.interfaces import ValidationError
from zope.component.interfaces import IViewFactory



class I(Interface):
    title = Text(title=u"Title", required = False)
    description = Text(title=u"Description",
                       default = u'No description', required = False)
    def foo():
        """Does foo things"""

class I2(Interface):
    title = Text(title = u"Title", required = True)
    description = Text(title = u"Description", required = True)

class I3(Interface):
    title = Text(title = u"Title", required = True)
    description = Text(title=u"Description", required = False)

class C:
    __implements__ = I

class C2:
    __implements__ = I2


class Ia(Interface):
    getTitle, setTitle = accessors(Text(title=u"Title", required = False))
    getDescription, setDescription = accessors(Text(
        title=u"Description",
        default = u'No description', required = False)
                                               )

class Ca:
    __implements__ = Ia

    def getTitle(self): return self._t
    def setTitle(self, v): self._t = v
    def getDescription(self): return self._d
    def setDescription(self, v): self._d = v

class ViewWithCustomTitleWidgetFactory(BrowserView):

    def title(self, context, request):
        w = W(context, request)
        w.custom = 1
        return w

    directlyProvides(title, IViewFactory)

def kw(**kw):
    return kw

class W(TextWidget):

    def setData(self, v):
        self.context.validate(v)
        self._data = v

    def setPrefix(self, prefix):
        self.prefix = prefix

    def __call__(self):
        name = self.name
        v = getattr(self, '_data', None)
        if (v is None) and (name in self.request):
            v = self.request[name]


        return unicode(self.context.__name__) + u': ' + (v or '')

    def getData(self):
        v = self.request.get(self.name, self)
        if v is self:
            if self.context.required:
                raise ValidationError("%s required" % self.name)
            v = self.context.default
        return v

    def haveData(self):
        if self.name in self.request and self.request[self.name]:
            return True
        return False

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        setDefaultViewName(IText, IBrowserPresentation, 'edit')
        provideView(IText, 'edit', IBrowserPresentation, W)


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
        request.form['field.title'] = u'xxx'
        view = BrowserView(c, request)
        setUpWidget(view, 'title', I['title'])
        self.assertEqual(view.title(), u'title: xxx')
        self.assertEqual(view.title.getData(), u'xxx')

    def test_setUpWidget_w_request_data_and_initial_data(self):
        c = C()
        request = TestRequest()
        request.form['field.title'] = u'xxx'
        view = BrowserView(c, request)
        setUpWidget(view, 'title', I['title'], u'yyy')
        self.assertEqual(view.title(), u'title: xxx')
        self.assertEqual(view.title.getData(), u'xxx')

    def test_setUpWidget_w_request_data_and_initial_data_force(self):
        c = C()
        request = TestRequest()
        request.form['field.title'] = u'xxx'
        view = BrowserView(c, request)
        setUpWidget(view, 'title', I['title'], u'yyy', force=1)
        self.assertEqual(view.title(), u'title: yyy')
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

    def test_setUpWidget_w_Custom_widget(self):
        c = C()
        request = TestRequest()
        view = ViewWithCustomTitleWidgetFactory(c, request)
        setUpWidget(view, 'title', I['title'], u'yyy')
        self.assertEqual(view.title(), u'title: yyy')
        self.assertEqual(view.title.getData(), None)
        self.assertEqual(view.title.custom, 1)

    def test_setupWidgets(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        setUpWidgets(view, I)
        self.assertEqual(view.title(), u'title: ')
        self.assertEqual(view.description(), u'description: ')

    def test_setupWidgets_via_names(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        setUpWidgets(view, I, names=['title'])
        self.assertEqual(view.title(), u'title: ')
        self.failIf(hasattr(view, 'description'))

    def test_setupWidgets_bad_field_name(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        self.assertRaises(KeyError, setUpWidgets, view, I, names=['bar'])
        #This AttributeError occurs when setUpWidget tries to call
        #bind on the non-Field (Method) object.  The point is that
        #that *some* error should occur, not necessarily this specific one.
        self.assertRaises(AttributeError, setUpWidgets, view, I, names=['foo'])

    def test_setupWidgets_w_prefix(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        setUpWidgets(view, I, prefix='spam')
        self.assertEqual(view.title.prefix, 'spam')
        self.assertEqual(view.description.prefix, 'spam')

    def test_setupWidgets_w_initial_data_and_custom_widget(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        view.title = w = W(I['title'], request)
        setUpWidgets(view, I, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(view.title(), u'title: ttt')
        self.assertEqual(view.description(), u'description: ddd')
        self.assertEqual(view.title, w)

    def test_setupWidgets_w_initial_data_and_request_data(self):
        c = C()
        request = TestRequest()
        request.form['field.title'] = u'yyy'
        view = BrowserView(c, request)
        setUpWidgets(view, I, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(view.title(), u'title: yyy')

    def test_setupWidgets_w_initial_data_forced_and_request_data(self):
        c = C()
        request = TestRequest()
        request.form['field.title'] = u'yyy'
        view = BrowserView(c, request)
        setUpWidgets(view, I, force=1,
                     initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(view.title(), u'title: ttt')

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

    def test_setupEditWidgets_w_form_data(self):
        c = C()
        c.title = u'ct'
        c.description = u'cd'
        request = TestRequest()
        request.form['field.title'] = u'ft'
        request.form['field.description'] = u'fd'
        view = BrowserView(c, request)
        setUpEditWidgets(view, I)
        self.assertEqual(view.title(), u'title: ft')
        self.assertEqual(view.description(), u'description: fd')

    def test_setupEditWidgets_via_names(self):
        c = C()
        c.title = u'ct'
        request = TestRequest()
        request.form['field.title'] = u'ft'
        view = BrowserView(c, request)
        setUpEditWidgets(view, I, names=['title'])
        self.assertEqual(view.title(), u'title: ft')
        self.failIf(hasattr(view, 'description'))

    def test_setupEditWidgets_and_accessors(self):
        c = Ca()
        c.setTitle(u'ct')
        c.setDescription(u'cd')
        request = TestRequest()
        view = BrowserView(c, request)
        setUpEditWidgets(view, Ia)
        self.assertEqual(view.getTitle(), u'getTitle: ct')
        self.assertEqual(view.getDescription(), u'getDescription: cd')

    def test_setupWidgets_bad_field_name(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        self.assertRaises(KeyError, setUpEditWidgets, view, I, names=['bar'])
        #This AttributeError occurs when setUpEditWidget tries to call
        #bind on the non-Field (Method) object.  The point is that
        #that *some* error should occur, not necessarily this specific one.
        self.assertRaises(AttributeError, setUpEditWidgets, view,
                          I, names=['foo'])

    def test_setupEditWidgets_w_form_data_force(self):
        c = C()
        c.title = u'ct'
        c.description = u'cd'
        request = TestRequest()
        request.form['field.title'] = u'ft'
        request.form['field.description'] = u'ft'
        view = BrowserView(c, request)
        setUpEditWidgets(view, I, force=1)
        self.assertEqual(view.title(), u'title: ct')
        self.assertEqual(view.description(), u'description: cd')

    def test_setupEditWidgets_w_custom_widget_and_prefix(self):
        c = C()
        c.title = u'ct'
        c.description = u'cd'
        request = TestRequest()
        view = BrowserView(c, request)
        view.title = w = W(I['title'], request)
        setUpEditWidgets(view, I, prefix='eggs')
        self.assertEqual(view.title.prefix, 'eggs')
        self.assertEqual(view.description.prefix, 'eggs')
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

    def test_setupEditWidgets_w_bad_data(self):
        class Forbidden(AttributeError): pass

        class C(object):
            title = u'foo'

            def d(self):
                raise Forbidden()

            description = property(d)

        c = C()

        request = TestRequest()
        view = BrowserView(c, request)
        self.assertRaises(Forbidden, setUpEditWidgets, view, I)

    def test_getSetupWidgets_w_form_data(self):
        c = C()
        request = TestRequest()
        request.form['field.title'] = u'ft'
        view = BrowserView(c, request)
        setUpWidgets(view, I, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(view.title(), u'title: ft')
        self.assertEqual(view.description(), u'description: ddd')


    def test_getWidgetsData(self):
        c = C()
        request = TestRequest()
        request.form['field.title'] = u'ft'
        request.form['field.description'] = u'fd'
        view = BrowserView(c, request)
        setUpWidgets(view, I, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(getWidgetsData(view, I),
                         {'title': u'ft',
                          'description': u'fd'})


        setUpWidgets(view, I3, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(getWidgetsData(view, I3),
                         {'title': u'ft',
                          'description': u'fd'})

        request.form['field.description'] = ''
        setUpWidgets(view, I3, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(getWidgetsData(view, I3),
                         {'title': u'ft',
                          'description': None})

        request.form['field.description'] = u''
        setUpWidgets(view, I, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(getWidgetsData(view, I),
                         {'title': u'ft',
                          'description': None})

    def test_getWidgetsData_w_names(self):
        c = C()
        request = TestRequest()
        request.form['field.title'] = u'ft'
        request.form['field.description'] = u'fd'
        view = BrowserView(c, request)
        setUpWidgets(view, I, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(getWidgetsData(view, I, names=['title']),
                         {'title': u'ft'})
        self.assertRaises(KeyError, getWidgetsData, view, I, names=['bar'])
        self.assertRaises(AttributeError, getWidgetsData, view, I,
                          names=['foo'])

    def test_getWidgetsData_w_readonly_fields(self):
        class ITest(I):
            name = Text(title=u"Title", readonly=True)

        c = C()
        request = TestRequest()
        request.form['field.name'] = u'foo'
        request.form['field.title'] = u'ft'
        request.form['field.description'] = u'fd'
        view = BrowserView(c, request)
        setUpWidgets(view, ITest, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(getWidgetsData(view, ITest, names=['name', 'title']),
                         {'title': u'ft', 'name': 'foo'})

    def test_getWidgetsData_w_readonly_fields_but_exclude_anyway(self):
        class ITest(I):
            name = Text(title=u"Title", readonly=True)

        c = C()
        request = TestRequest()
        request.form['field.name'] = u'foo'
        request.form['field.title'] = u'ft'
        request.form['field.description'] = u'fd'
        view = BrowserView(c, request)
        setUpWidgets(view, ITest, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(
            getWidgetsData(view, ITest, names=['name', 'title'],
                           exclude_readonly=True),
            {'title': u'ft'})

    def test_haveWidgetsData(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        setUpWidgets(view, I, initial=kw(title=u"ttt", description=u"ddd"))
        self.failIf(haveWidgetsData(view, I))

        request.form['field.description'] = u'fd'
        self.failUnless(haveWidgetsData(view, I))

    def test_haveWidgetsData_w_names(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        setUpWidgets(view, I, initial=kw(title=u"ttt", description=u"ddd"))
        self.failIf(haveWidgetsData(view, I))

        request.form['field.description'] = u'fd'
        self.failUnless(haveWidgetsData(view, I))
        self.failIf(haveWidgetsData(view, I, names=['title']))
        self.assertRaises(KeyError, haveWidgetsData, view, I, names=['bar'])
        self.assertRaises(AttributeError, haveWidgetsData, view, I,
                          names=['foo'])

    def test_getWidgetsData_w_default(self):
        c = C()
        request = TestRequest()
        view = BrowserView(c, request)
        setUpWidgets(view, I, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(
            getWidgetsData(view, I, strict=False, set_missing=False),
            {})

        self.assertEqual(
            getWidgetsData(view, I, strict=False, set_missing=True),
            {'description': None,  'title': None})

        # XXX check that the WidgetsError contains a MissingInputError
        self.assertRaises(WidgetsError,
                          getWidgetsData, view, I2, strict=True)

        self.assertEqual(getWidgetsData(view, I),
                         {'description': None, 'title': None})

        request.form['field.description'] = u'fd'
        self.assertEqual(getWidgetsData(view, I2, strict=False,
                                        set_missing=False),
                         {'description': u'fd'})

        self.assertEqual(getWidgetsData(view, I2, strict=False,
                                        set_missing=True),
                         {'description': u'fd', 'title': None})

        # XXX check that the WidgetsError contains a MissingInputError
        self.assertRaises(WidgetsError, getWidgetsData, view, I2)
        self.assertEqual(getWidgetsData(view, I), {'description': u'fd',
                                                   'title': None})

    def test_getWidgetsDataForContent(self):
        c = C()
        request = TestRequest()
        request.form['field.title'] = u'ft'
        request.form['field.description'] = u'fd'
        view = BrowserView(c, request)
        setUpWidgets(view, I, initial=kw(title=u"ttt", description=u"ddd"))
        getWidgetsDataForContent(view, I)

        self.assertEqual(c.title, u'ft')
        self.assertEqual(c.description, u'fd')

        c2 = C()
        request.form['field.title'] = u'ftt'
        request.form['field.description'] = u'fdd'
        getWidgetsDataForContent(view, I, c2)

        self.assertEqual(c.title, u'ft')
        self.assertEqual(c.description, u'fd')

        self.assertEqual(c2.title, u'ftt')
        self.assertEqual(c2.description, u'fdd')

    def test_getWidgetsDataForContent_accessors(self):
        c = Ca()
        request = TestRequest()
        request.form['field.getTitle'] = u'ft'
        request.form['field.getDescription'] = u'fd'
        view = BrowserView(c, request)
        setUpWidgets(view, Ia, initial=kw(title=u"ttt", description=u"ddd"))
        getWidgetsDataForContent(view, Ia)

        self.assertEqual(c.getTitle(), u'ft')
        self.assertEqual(c.getDescription(), u'fd')

        c2 = Ca()
        request.form['field.getTitle'] = u'ftt'
        request.form['field.getDescription'] = u'fdd'
        getWidgetsDataForContent(view, Ia, c2)

        self.assertEqual(c.getTitle(), u'ft')
        self.assertEqual(c.getDescription(), u'fd')

        self.assertEqual(c2.getTitle(), u'ftt')
        self.assertEqual(c2.getDescription(), u'fdd')

    def testErrors(self):
        c = C2()
        c.title = u'old title'
        c.description = u'old description'
        request = TestRequest()
        request.form['field.title'] = u'ft'
        view = BrowserView(c, request)
        setUpWidgets(view, I2, initial=kw(title=u"ttt", description=u"ddd"))
        getWidgetsDataForContent(view, I2, names=("title",))
        self.assertEqual(c.title, u'ft')
        self.assertEqual(c.description, u'old description')

        request = TestRequest()
        c.title = u'old title'
        view = BrowserView(c, request)
        setUpWidgets(view, I2, initial=kw(title=u"ttt", description=u"ddd"))
        self.assertEqual(c.title, u'old title')
        self.assertEqual(c.description, u'old description')

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
