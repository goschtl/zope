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
import unittest, os
from tempfile import mktemp
import zope.configuration.tests.directives
from zope.configuration.tests.directives import protections
from zope.configuration.xmlconfig import XMLConfig
from zope.testing.cleanup import CleanUp # Base class w registry cleanup


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

    def testNormal_because_of_overrides(self):
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
            handler="zope.configuration.tests.directives.protectClass">
            <subdirective name="protect" namespace="%s" />
            </directive>
            <directive name="increment" namespace="%s"
            handler="zope.configuration.tests.directives.increment">
            </directive>
            ''' % (ns, ns, ns),

            '''
            <test:protectClass
            name=".Contact" permission="splat1" names="update"
            />
            <test:increment />
            <test:increment />
            <test:increment />
            <include file="%s"/>
            ''' % f2), 'f1')

        XMLConfig(str(f1))()

        self.assertEquals(protections, [
            (".Contact", "splat1", 'update'),
            (".Contact", "splat", 'update2'),
            ])

        self.assertEquals(zope.configuration.tests.directives.count, 3)

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
            handler="zope.configuration.tests.directives.protectClass">
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

        from zope.configuration.xmlconfig import ZopeConfigurationConflictError

        self.assertRaises(ZopeConfigurationConflictError, x)

        self.assertEquals(protections, [])

    def testConflicting_not_due_to_extra_override(self):
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
            handler="zope.configuration.tests.directives.protectClass">
            <subdirective name="protect" namespace="%s" />
            </directive>''' % (ns, ns),
            '''
            <test:protectClass
            name=".Contact" permission="splat1" names="update"
            />
            <include file="%s"/>
            <include file="%s"/>
            <test:protectClass
              name=".Contact" permission="splat2" names="update2"
            />
            ''' % (f2, f3)), 'f1')

        x=XMLConfig(str(f1))

        x()

        self.assertEquals(protections, [
            (".Contact", "splat1", 'update'),
            (".Contact", "splat2", 'update2'),
            ])


    def testConflicting_in_same_location(self):
        f1=tfile(template % (
            '''<directive name="protectClass" namespace="%s"
            handler="zope.configuration.tests.directives.protectClass">
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

        from zope.configuration.xmlconfig import ZopeConfigurationConflictError

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
