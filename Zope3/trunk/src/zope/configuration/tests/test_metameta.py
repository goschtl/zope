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
import sys, unittest
from zope.testing.cleanup import CleanUp
from zope.configuration.xmlconfig import xmlconfig, testxmlconfig, XMLConfig
from zope.configuration.tests.directives import done
from zope.configuration.tests.basetestdirectivesxml import directiveTests
from zope.configuration.tests.basetestdirectivesxml import makeconfig
import zope.configuration

class Test(CleanUp, unittest.TestCase, directiveTests):

    def setUp(self):
        XMLConfig('metameta.zcml', zope.configuration)()


    def testDescription(self):
        xmlconfig(makeconfig(
            '''<directive
                   name="doit"
                   description="Something to Do"
                   handler="zope.configuration.tests.directives.doit" />''',
            '''<test:doit name="splat" />'''
            ))
        self.assertEqual(done, ['splat'])

    def testAttribute(self):
        xmlconfig(makeconfig(
            '''<directive
                   name="doit"
                   handler="zope.configuration.tests.directives.doit"
                   description="Something to Do"
               >
                 <attribute
                     name="name"
                     required="yes"
                     description="Just Do It" />
               </directive>''',
            '''<test:doit name="splat" />'''
            ))
        self.assertEqual(done, ['splat'])

    def testBadRequired(self):
        self.assertRaises(
            ValueError,
            testxmlconfig,
            makeconfig(
                '''<directive
                       name="doit"
                       handler="zope.configuration.tests.directives.doit"
                   >
                     <attribute
                         name="name"
                         required="badvalue"
                         description="Just Do It" />
                   </directive>''',
                '''<test:doit name="splat" />'''
                ))

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

def run():
    unittest.TextTestRunner().run(test_suite())

def debug():
    test_suite().debug()

def pdb():
    import pdb
    pdb.run('debug()')

if __name__=='__main__':
    if len(sys.argv) < 2:
        run()
    else:
        globals()[sys.argv[1]]()
