__rcs_id__ = '$Id'
__version__ = '$Revision: 1.1 $'[11:-2]

import unittest

from zope.component.view import provideView
from zope.app.browser.form.widget import TextWidget
from zope.schema.interfaces import ITextLine
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.browser import TestRequest
from zope.schema import Tuple, List, TextLine
from zope.app.browser.form.widget import TupleSequenceWidget, \
    ListSequenceWidget


from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest


class SequenceWidgetTest(BrowserWidgetTest):
    def _FieldFactory(self, **kw):
        kw.update({'__name__': u'foo',
            'value_types': (TextLine(__name__=u'bar'),)})
        return Tuple(**kw)
    _WidgetFactory = TupleSequenceWidget

    def verifyResult(self, result, check_list, inorder=False):
        pass
    def verifyResultMissing(self, result, check_list):
        pass

    def setUp(self):
        BrowserWidgetTest.setUp(self)
        self.field = Tuple(__name__=u'foo',
            value_types=(TextLine(__name__=u'bar'),))
        provideView(ITextLine, 'edit', IBrowserPresentation, [TextWidget])

    def test_haveNoData(self):
        self.failIf(self._widget.haveData())

    def test_haveData(self):
        self._widget.request.form['field.foo.0.bar'] = u'hi, mum'
        self.failUnless(self._widget.haveData())

    def test_list(self):
        self.field = List(__name__=u'foo',
            value_types=(TextLine(__name__=u'bar'),))
        request = TestRequest()
        widget = ListSequenceWidget(self.field, request)
        self.assertEquals(int(widget.haveData()), 0)
        self.assertEquals(widget.getData(), [])

        request = TestRequest(form={'field.foo.add': u'Add bar'})
        widget = ListSequenceWidget(self.field, request)
        self.assertEquals(int(widget.haveData()), 1)
        self.assertEquals(widget.getData(), [None])

        request = TestRequest(form={'field.foo.0.bar': u'Hello world!'})
        widget = ListSequenceWidget(self.field, request)
        self.assertEquals(int(widget.haveData()), 1)
        self.assertEquals(widget.getData(), [u'Hello world!'])

    def test_new(self):
        request = TestRequest()
        widget = TupleSequenceWidget(self.field, request)
        self.assertEquals(int(widget.haveData()), 0)
        self.assertEquals(widget.getData(), ())
        check_list = ('input', 'name="field.foo.add"')
        self.verifyResult(widget(), check_list)

    def test_add(self):
        request = TestRequest(form={'field.foo.add': u'Add bar'})
        widget = TupleSequenceWidget(self.field, request)
        self.assertEquals(int(widget.haveData()), 1)
        self.assertEquals(widget.getData(), (None,))
        check_list = (
            'checkbox', 'field.foo.remove_0', 'input', 'field.foo.0.bar'
            'submit', 'submit', 'field.foo.add'
        )
        self.verifyResult(widget(), check_list, inorder=True)

    def test_request(self):
        request = TestRequest(form={'field.foo.0.bar': u'Hello world!'})
        widget = TupleSequenceWidget(self.field, request)
        self.assertEquals(int(widget.haveData()), 1)
        self.assertEquals(widget.getData(), (u'Hello world!',))

    def test_existing(self):
        request = TestRequest()
        widget = TupleSequenceWidget(self.field, request)
        widget.setData(('existing',))
        self.assertEquals(int(widget.haveData()), 1)
        self.assertEquals(widget.getData(), ('existing',))
        check_list = (
            'checkbox', 'field.foo.remove_0', 'input', 'field.foo.0.bar',
                'existing',
            'submit', 'submit', 'field.foo.add'
        )
        self.verifyResult(widget(), check_list, inorder=True)
        widget.setData(('existing', 'second'))
        self.assertEquals(int(widget.haveData()), 1)
        self.assertEquals(widget.getData(), ('existing', 'second'))
        check_list = (
            'checkbox', 'field.foo.remove_0', 'input', 'field.foo.0.bar',
                'existing',
            'checkbox', 'field.foo.remove_1', 'input', 'field.foo.1.bar',
                'second',
            'submit', 'submit', 'field.foo.add'
        )
        self.verifyResult(widget(), check_list, inorder=True)

    def test_remove(self):
        request = TestRequest(form={'field.foo.remove_0': u'Hello world!',
            'field.foo.0.bar': u'existing', 'field.foo.1.bar': u'second'})
        widget = TupleSequenceWidget(self.field, request)
        widget.setData(('existing', 'second'))
        self.assertEquals(widget.getData(), (u'second',))
        check_list = (
            'checkbox', 'field.foo.remove_0', 'input', 'field.foo.0.bar',
                'second',
            'submit', 'submit', 'field.foo.add'
        )
        self.verifyResult(widget(), check_list, inorder=True)

    def test_min(self):
        request = TestRequest()
        self.field.min_length = 2
        widget = TupleSequenceWidget(self.field, request)
        widget.setData(('existing',))
        self.assertEquals(widget.getData(), (u'existing',))
        check_list = (
            'input', 'field.foo.0.bar', 'existing',
            'input', 'field.foo.0.bar', 'value=""',
            'submit', 'submit', 'field.foo.add'
        )
        s = widget()
        self.verifyResult(s, check_list, inorder=True)
        self.assertEquals(s.find('checkbox'), -1)

    def test_max(self):
        request = TestRequest()
        self.field.max_length = 1
        widget = TupleSequenceWidget(self.field, request)
        widget.setData(('existing',))
        self.assertEquals(widget.getData(), (u'existing',))
        s = widget()
        self.assertEquals(s.find('field.foo.add'), -1)


def test_suite():
    return unittest.makeSuite(SequenceWidgetTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
# vim: set filetype=python ts=4 sw=4 et si

