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
from Zope.Testing.CleanUp import CleanUp
from Zope.Configuration.xmlconfig import xmlconfig, testxmlconfig, XMLConfig
from Zope.Configuration.tests.Directives import done
from Zope.Configuration.tests.BaseTestDirectivesXML import directiveTests
from Zope.Configuration.tests.BaseTestDirectivesXML import makeconfig
import Zope.Configuration

class Test(CleanUp, unittest.TestCase, directiveTests):

    def setUp(self):
        XMLConfig('metameta.zcml', Zope.Configuration)()


    def testDescription(self):
        xmlconfig(makeconfig(
            '''<directive
                   name="doit"
                   description="Something to Do"
                   handler="Zope.Configuration.tests.Directives.doit" />''',
            '''<test:doit name="splat" />'''
            ))
        self.assertEqual(done, ['splat'])

    def testAttribute(self):
        xmlconfig(makeconfig(
            '''<directive
                   name="doit"
                   handler="Zope.Configuration.tests.Directives.doit"
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
                       handler="Zope.Configuration.tests.Directives.doit"
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
