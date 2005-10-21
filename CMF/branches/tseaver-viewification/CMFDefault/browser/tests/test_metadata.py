##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for CMFDefault's metadata views

$Id$
"""
import unittest
from Products.Five.traversable import FakeRequest
from DateTime.DateTime import DateTime

_DC_VALUES = {
    'Title': "Title",
    'Creators': ("Creator",),
    'Subject': ("Subject",),
    'Description': "Description",
    'Publisher': "Publisher",
    'Contributors': ("Contributors",),
    'created': DateTime('2005-10-21'),
    'effective': DateTime('2005-10-23'),
    'expires': DateTime('2005-10-24'),
    'modified': DateTime('2005-10-22'),
    'Type': "Type",
    'Format': "Format",
    'Identifier': "Identifier",
    'Language': "Language",
    'Rights': "Rights",
}

_DC_DATE_STRINGS = [
    ('created', 'CreationDate',),
    ('modified', 'ModificationDate',),
    ('effective', 'EffectiveDate',),
    ('expires', 'ExpirationDate',),
]

_EXAMPLE_URL = 'http://www.example.com/document'

class MetadataViewTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.CMFDefault.browser.metadata import MetadataView
        return MetadataView

    def _makeOne(self, context, request=None, *args, **kw):
        if request is None:
            request = FakeRequest()
        return self._getTargetClass()(context, request, *args, **kw)

    def _makeContext(self, **kw):
        from zope.interface import implements
        from Products.CMFCore.interfaces import IMutableDublinCore

        class _Dummy:
            implements(IMutableDublinCore)
            allow_discussion = None
            def __init__(self, kw):
                self.__dict__.update(dict([('_%s' % k, v)
                                           for k, v in _DC_VALUES.items()]))
                self.__dict__.update(kw)

            def Title(self):
                return self._Title

            def listCreators(self):
                return self._Creators

            def Creator(self):
                return self._Creators[0]

            def Subject(self):
                return self._Subject

            def Description(self):
                return self._Description

            def Publisher(self):
                return self._Publisher

            def listContributors(self):
                return self._Contributors

            def Date(self):
                return self._created.Date()

            def CreationDate(self):
                return self._created.Date()

            def EffectiveDate(self):
                return self._effective.Date()

            def ExpirationDate(self):
                return self._expires.Date()

            def ModificationDate(self):
                return self._modified.Date()

            def Type(self):
                return self._Type

            def Format(self):
                return self._Format

            def Identifier(self):
                return self._Identifier

            def Language(self):
                return self._Language

            def Rights(self):
                return self._Rights

            def created(self):
                return self._created

            def effective(self):
                return self._effective

            def expires(self):
                return self._expires

            def modified(self):
                return self._modified

            def absolute_url(self):
                return _EXAMPLE_URL

            def setTitle(self, value):
                self._Title = value

        return _Dummy(kw)

    def test_empty(self):
        context = self._makeContext()
        request = FakeRequest()
        view = self._makeOne(context, request)
        self.failUnless(view.context is context)
        self.failUnless(view.request is request)

    def test_getMetadataInfo(self):
        context = self._makeContext()
        view = self._makeOne(context)

        minfo = view.getMetadataInfo()

        for k, v in _DC_VALUES.items():
            self.assertEqual(minfo[k], v)

        for dn, sn in _DC_DATE_STRINGS:
            mapped = _DC_VALUES[dn].Date()
            self.assertEquals(minfo[sn], mapped)

    def test_getFormInfo_allow_discussion(self):
        context = self._makeContext()
        view = self._makeOne(context)

        finfo = view.getFormInfo()
        self.assertEqual(finfo['allow_discussion'], None)

        context.allow_discussion = False
        finfo = view.getFormInfo()
        self.assertEqual(finfo['allow_discussion'], False)

        context.allow_discussion = True
        finfo = view.getFormInfo()
        self.assertEqual(finfo['allow_discussion'], True)

    def test_getFormInfo_subject_lines(self):
        SUBJECTS = ('abc', 'def')
        context = self._makeContext()
        context._Subject = SUBJECTS
        view = self._makeOne(context)
        finfo = view.getFormInfo()
        self.assertEqual(finfo['subject_lines'], '\n'.join(SUBJECTS))

    def test_getFormInfo_contributor_lines(self):
        CONTRIBUTORS = ('abc', 'def')
        context = self._makeContext()
        context._Contributors = CONTRIBUTORS
        view = self._makeOne(context)
        finfo = view.getFormInfo()
        self.assertEqual(finfo['contributor_lines'], '\n'.join(CONTRIBUTORS))

    def test_getFormInfo_buttons(self):
        BUTTONS =(('change', 'Change'),
                  ('change_and_edit', 'Change and Edit'),
                  ('change_and_view', 'Change and View'),
                 )
        context = self._makeContext()
        view = self._makeOne(context)
        finfo = view.getFormInfo()
        buttons = finfo['buttons']

        self.assertEqual(len(buttons), len(BUTTONS))
        for found, expected in zip(buttons, BUTTONS):
            self.assertEqual(found['name'], expected[0])

    def test_controller_redirect(self):
        NEW_TITLE = 'New Title'

        class _DummyResponse:
            _redirected = None
            def redirect(self, target):
                self._redirected = target

        context = self._makeContext()
        request = FakeRequest()
        request.form = {'title': NEW_TITLE, 'change': 'Change'}
        response = _DummyResponse()

        view = self._makeOne(context, request)
        view.controller(response)
        self.assertEqual(response._redirected,
                         '%s/%s' % (_EXAMPLE_URL, 'metadata.html'))
        self.assertEqual(context._Title, NEW_TITLE)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(MetadataViewTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

