##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
$Id: test_w3cschemalocations.py,v 1.1 2003/04/10 10:33:31 faassen Exp $
"""

import unittest
from zope.app.xml.w3cschemalocations import getW3CXMLSchemaLocations

class W3CSchemaLocationsTests(unittest.TestCase):
    def test_getW3CXMLSchemaLocations1(self):
        xml = '''\
<?xml version="1.0" ?>
<foo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://namespaces.zope.org/hypothetical/alpha">
<p>There is more stuff here.</p>
</foo>
'''
        # a single schema location
        self.assertEquals(['http://namespaces.zope.org/hypothetical/alpha'],
                          getW3CXMLSchemaLocations(xml))

    
    def test_getW3CXMLSchemaLocations2(self):
        xml = '''\
<?xml version="1.0" ?>
<foo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://namespaces.zope.org/hypothetical/alpha
                         http://namespaces.zope.org/hypothetical/beta">
<p>There is more stuff here.</p>
</foo>
'''
        # two schema locations
        self.assertEquals(['http://namespaces.zope.org/hypothetical/alpha',
                           'http://namespaces.zope.org/hypothetical/beta'],
                          getW3CXMLSchemaLocations(xml))

    def test_getW3CSchemaLocations3(self):
        xml = '''\
<?xml version="1.0" ?>
<foo>
<p>Bar</p>
</foo>
'''
        # no schema location info at all
        self.assertEquals([], getW3CXMLSchemaLocations(xml))

    def test_getW3CXMLSchemaLocations4(self):
        xml = '''\
<?xml version="1.0" ?>
<foo xmlns:xsi="http://www.w3.org/the/wrong/thing"
     xsi:schemaLocation="http://namespaces.zope.org/hypothetical/alpha
                         http://namespaces.zope.org/hypothetical/beta">
<p>There is more stuff here.</p>
</foo>
'''
        # wrong name of the xsi: namespace
        self.assertEquals([], getW3CXMLSchemaLocations(xml))

    def test_getW3CXMLSchemaLocations5(self):
        xml = '''\
<?xml version="1.0" ?>
<foo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaFoobars="http://namespaces.zope.org/hypothetical/alpha
                        http://namespaces.zope.org/hypothetical/beta">
<p>There is more stuff here.</p>
</foo>
'''
        # wrong name of the xsi: attr
        self.assertEquals([], getW3CXMLSchemaLocations(xml))

    def test_getW3CXMLSchemaLocations6(self):
        xml = '''\
<?xml version="1.0" ?>
<doc>
<foo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://namespaces.zope.org/hypothetical/alpha">
<p>There is more stuff here.</p>
</foo>
</doc>
'''
        # don't check schema locations outside of document element
        self.assertEquals([],
                          getW3CXMLSchemaLocations(xml))
        
def test_suite():
    return unittest.makeSuite(W3CSchemaLocationsTests)
