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

$Id: testRegisterRequestFactory.py,v 1.2 2002/06/10 23:29:43 jim Exp $
"""

import unittest
from Zope.StartUp.RequestFactoryRegistry import getRequestFactory

from Zope.Configuration.xmlconfig import xmlconfig
from cStringIO import StringIO


template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:startup='http://namespaces.zope.org/startup'>
   %s
   </zopeConfigure>"""


class Test( unittest.TestCase ):


    def testRegisterRequestFactory(self):

        xmlconfig(StringIO(template % (
            '''
            <directive name="registerRequestFactory"
               attributes="name publication request"
               handler="Zope.StartUp.metaConfigure.registerRequestFactory"
               namespace="http://namespaces.zope.org/startup" />

            <startup:registerRequestFactory name="BrowserRequestFactory"
              publication = 
              "Zope.App.ZopePublication.Browser.Publication.BrowserPublication"
              request = "Zope.Publisher.Browser.BrowserRequest." />
            '''
            )))

        from Zope.App.ZopePublication.Browser.Publication import \
             BrowserPublication
        from Zope.Publisher.Browser.BrowserRequest import BrowserRequest

        self.assertEqual(
            getRequestFactory('BrowserRequestFactory')._pubFactory,
            BrowserPublication)
        self.assertEqual(
            getRequestFactory('BrowserRequestFactory')._request,
            BrowserRequest)



def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )


if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )
