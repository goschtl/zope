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

$Id: test_registerrequestfactory.py,v 1.3 2003/07/28 22:21:41 jim Exp $
"""

import unittest
from zope.configuration.xmlconfig import xmlconfig
from zope.app.process.requestfactoryregistry import getRequestFactory
from zope.testing.cleanup import CleanUp
from zope.app.interfaces.startup import IPublicationRequestFactoryFactory
from zope.interface import implements
from cStringIO import StringIO

class TF:
    "test request factory"
    implements(IPublicationRequestFactoryFactory)

tf = TF()

ns = 'http://www.zope.org/NS/Zope3/test'

def makeconfig(metadirectives,directives):
    return StringIO(
        '''<zopeConfigure
               xmlns="http://namespaces.zope.org/zope"
               xmlns:test="%(ns)s">
            <directives namespace="%(ns)s">
              %(metadirectives)s
            </directives>
            %(directives)s
            </zopeConfigure>''' % {
                'metadirectives': metadirectives,
                'directives': directives,
                'ns': ns})

class Test(CleanUp, unittest.TestCase):

    def testRegisterRequestFactory(self):

        xmlconfig(makeconfig(
            '''<directive
                   name="registerRequestFactory"
                   attributes="name publication request"
                   handler=
                   "zope.app.process.metaconfigure.registerRequestFactory"
                   />''',
            '''<test:registerRequestFactory
                   name="BrowserRequestFactory"
                   publication=
             "zope.app.publication.browser.BrowserPublication"
                   request = "zope.publisher.browser.BrowserRequest" />
            '''
            ))

        from zope.app.publication.browser import \
             BrowserPublication
        from zope.publisher.browser import BrowserRequest

        self.assertEqual(
            getRequestFactory('BrowserRequestFactory')._pubFactory,
            BrowserPublication)
        self.assertEqual(
            getRequestFactory('BrowserRequestFactory')._request,
            BrowserRequest)


    def testRegisterRequestFactory_w_factory(self):

        xmlconfig(makeconfig(
            '''<directive
                   name="registerRequestFactory"
                   attributes="name publication request factory"
                   handler=
                   "zope.app.process.metaconfigure.registerRequestFactory"
                   />''',
            '''<test:registerRequestFactory
                   name="BrowserRequestFactory"
                   factory="
                   zope.app.process.tests.test_registerrequestfactory.tf"
                   />
            '''
            ))

        import zope.app.process.tests.test_registerrequestfactory

        self.assertEqual(
            getRequestFactory('BrowserRequestFactory'),
            zope.app.process.tests.test_registerrequestfactory.tf
            )




def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
