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
"""terServerType.py,v 1.1.2.2 2002/04/02 02:20:40 srichter Exp $
"""

import unittest
from Zope.StartUp.ServerTypeRegistry import getServerType

from Zope.Configuration.xmlconfig import xmlconfig
from cStringIO import StringIO


template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:startup='http://namespaces.zope.org/startup'>
   %s
   </zopeConfigure>"""


class Test( unittest.TestCase ):


    def testRegisterServerType(self):

        xmlconfig(StringIO(template % (
            '''<directive name="registerServerType"
                 attributes="name publication request"
                 handler="Zope.StartUp.metaConfigure.registerServerType"
                 namespace="http://namespaces.zope.org/startup" />

               <startup:registerServerType 
                 name = "Browser"
                 factory = "Zope.Server.HTTP.PublisherHTTPServer."
                 requestFactory="BrowserRequestFactory"
                 logFactory = "Zope.Server.HTTP.CommonHitLogger."
                 defaultPort="8080"
                 defaultVerbose="true" />
            '''
            )))

        from Zope.Server.HTTP.PublisherHTTPServer import PublisherHTTPServer
        from Zope.Server.HTTP.CommonHitLogger import CommonHitLogger

        self.assertEqual(getServerType('Browser')._factory,
                         PublisherHTTPServer)
        self.assertEqual(getServerType('Browser')._logFactory, CommonHitLogger)
        self.assertEqual(getServerType('Browser')._requestFactory,
                         "BrowserRequestFactory")
        self.assertEqual(getServerType('Browser')._defaultPort, 8080)
        self.assertEqual(getServerType('Browser')._defaultVerbose, 1)



def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )


if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )

