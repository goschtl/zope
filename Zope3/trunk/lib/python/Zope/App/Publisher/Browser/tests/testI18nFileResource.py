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
"""

Revision information:
$Id: testI18nFileResource.py,v 1.3 2002/10/04 18:37:23 jim Exp $
"""

from unittest import TestSuite, main, makeSuite

import os

from Zope.Exceptions import NotFoundError

from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalResourceService import provideResource
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter

from Zope.I18n.IUserPreferredCharsets import IUserPreferredCharsets
from Zope.I18n.IUserPreferredLanguages import IUserPreferredLanguages

from Zope.Publisher.HTTP.HTTPRequest import IHTTPRequest
from Zope.Publisher.HTTP.HTTPCharsets import HTTPCharsets
from Zope.Publisher.Browser.BrowserLanguages import BrowserLanguages
from Zope.Publisher.Browser.BrowserRequest import TestRequest

from Zope.App.Publisher.Browser.I18nFileResource import I18nFileResource, \
     I18nFileResourceFactory
from Zope.App.Publisher.FileResource import File, Image
import Zope.App.Publisher.Browser.tests as p

from Zope.App.ComponentArchitecture.metaConfigure import \
     provideService, managerHandler
from Zope.I18n.INegotiator import INegotiator
from Zope.I18n.Negotiator import negotiator

from Zope.I18n.tests.testII18nAware import TestII18nAware

test_directory = os.path.split(p.__file__)[0]


class Test(PlacelessSetup, TestII18nAware):

    def setUp(self):
        PlacelessSetup.setUp(self)
        TestII18nAware.setUp(self)
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)
        provideAdapter(IHTTPRequest, IUserPreferredLanguages, BrowserLanguages)
        # Setup the negotiator service registry entry
        managerHandler('defineService', 'LanguageNegotiation', INegotiator)
        provideService('LanguageNegotiation', negotiator, 'Zope.Public')


    def _createObject(self):
        obj = I18nFileResource({'en':None, 'lt':None, 'fr':None},
                               TestRequest(), 'fr')
        return obj


    def _createDict(self, filename1='test.pt', filename2='test2.pt'):
        path1 = os.path.join(test_directory, filename1)
        path2 = os.path.join(test_directory, filename2)
        return { 'en': File(path1),
                 'fr': File(path2) }


    def testNoTraversal(self):

        resource = I18nFileResourceFactory(self._createDict(), 'en')\
                                          (TestRequest())

        self.assertRaises(NotFoundError,
                          resource.publishTraverse,
                          resource.request,
                          '_testData')

    def testFileGET(self):

        # case 1: no language preference, should get en
        path = os.path.join(test_directory, 'test.txt')

        resource = I18nFileResourceFactory(self._createDict('test.txt'), 'en')\
                                          (TestRequest())


        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

        # case 2: prefer lt, have only en and fr, should get en
        resource = I18nFileResourceFactory(
                        self._createDict('test.txt'), 'en')\
                        (TestRequest(HTTP_ACCEPT_LANGUAGE='lt'))

        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

        # case 3: prefer fr, have it, should get fr
        path = os.path.join(test_directory, 'test2.pt')
        resource = I18nFileResourceFactory(
                        self._createDict('test.pt', 'test2.pt'), 'en')\
                        (TestRequest(HTTP_ACCEPT_LANGUAGE='fr'))

        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/html')


    def testFileHEAD(self):

        # case 1: no language preference, should get en
        resource = I18nFileResourceFactory(self._createDict('test.txt'), 'en')\
                                          (TestRequest())

        self.assertEqual(resource.HEAD(), '')

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

        # case 2: prefer lt, have only en and fr, should get en
        resource = I18nFileResourceFactory(
                        self._createDict('test.txt'), 'en')\
                        (TestRequest(HTTP_ACCEPT_LANGUAGE='lt'))

        self.assertEqual(resource.HEAD(), '')

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

        # case 3: prefer fr, have it, should get fr
        resource = I18nFileResourceFactory(
                        self._createDict('test.pt', 'test2.pt'), 'en')\
                        (TestRequest(HTTP_ACCEPT_LANGUAGE='fr'))

        self.assertEqual(resource.HEAD(), '')

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/html')


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
