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
import unittest, sys, os
from tempfile import mktemp
import Zope.Configuration.tests.Directives
from Zope.Configuration.tests.Directives import protections, done
from Zope.Configuration.xmlconfig import XMLConfig
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup


template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:test='http://www.zope.org/NS/Zope3/test'>
   <directives namespace="http://www.zope.org/NS/Zope3/test">
   %s
   </directives>
   %s
   </zopeConfigure>"""

ns='http://www.zope.org/NS/Zope3/test'


class Test(CleanUp, unittest.TestCase):
        
    def testNormal(self):
        f2=tfile(template % ('',
            '''
            <test:protectClass
            name=".Contact" permission="splat" names="update"
            />
            <test:protectClass
            name=".Contact" permission="splat" names="update2"
            />            
            '''), 'f2')

        f1=tfile(template % (
            '''<directive name="protectClass" namespace="%s"
            handler="Zope.Configuration.tests.Directives.protectClass">
            <subdirective name="protect" namespace="%s" />
            </directive>
            <directive name="increment" namespace="%s"
            handler="Zope.Configuration.tests.Directives.increment">
            </directive>
            ''' % (ns, ns, ns),

            '''
            <test:protectClass
            name=".Contact" permission="splat" names="update"
            />
            <test:increment />
            <test:increment />
            <test:increment />
            <include file="%s"/>
            ''' % f2), 'f1')

        XMLConfig(str(f1))()
        
        self.assertEquals(protections, [
            (".Contact", "splat", 'update'),
            (".Contact", "splat", 'update2'),
            ])

        self.assertEquals(Zope.Configuration.tests.Directives.count, 3)
        
    def testConflicting(self):
        f2=tfile(template % ('',
            '''
            <test:protectClass
            name=".Contact" permission="splat" names="update"
            />
            <test:protectClass
            name=".Contact" permission="splat" names="update2"
            />            
            '''), 'f2')
        f3=tfile(template % ('',
            '''
            <test:protectClass
            name=".Contact" permission="splat" names="update2"
            />            
            '''), 'f3')

        f1=tfile(template % (
            '''<directive name="protectClass" namespace="%s"
            handler="Zope.Configuration.tests.Directives.protectClass">
            <subdirective name="protect" namespace="%s" />
            </directive>''' % (ns, ns),
            '''
            <test:protectClass
            name=".Contact" permission="splat" names="update"
            />
            <include file="%s"/>
            <include file="%s"/>
            ''' % (f2, f3)), 'f1')

        x=XMLConfig(str(f1))

        from Zope.Configuration.xmlconfig import ZopeConfigurationConflictError

        self.assertRaises(ZopeConfigurationConflictError, x)
        
        self.assertEquals(protections, [])
        
        
    def testConflicting_in_same_location(self):
        f1=tfile(template % (
            '''<directive name="protectClass" namespace="%s"
            handler="Zope.Configuration.tests.Directives.protectClass">
            <subdirective name="protect" namespace="%s" />
            </directive>''' % (ns, ns),
            '''
            <test:protectClass
            name=".Contact" permission="splat" names="update"
            />
            <test:protectClass
            name=".Contact" permission="splat" names="update"
            />
            '''), 'f1')

        x=XMLConfig(str(f1))

        from Zope.Configuration.xmlconfig import ZopeConfigurationConflictError

        self.assertRaises(ZopeConfigurationConflictError, x)
        
        self.assertEquals(protections, [])
        


class tfile:
    
    def __init__(self, string, suffix):
        self.name = mktemp(suffix)
        file = open(self.name, 'w')
        file.write(string)
        file.close()

    def __str__(self): return self.name

    def __del__(self): os.remove(self.name)

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
