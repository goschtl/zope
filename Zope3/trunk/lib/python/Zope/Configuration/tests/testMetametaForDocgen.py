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
from Zope.Configuration.meta import _directives
from Zope.Configuration.metametaConfigureForDocgen import _metadataKey
from Zope.Configuration.tests.Directives import done
from Zope.Configuration.tests.BaseTestDirectivesXML import directiveTests
from Zope.Configuration.tests.BaseTestDirectivesXML import makeconfig, ns
import Zope.Configuration

class Test(CleanUp, unittest.TestCase, directiveTests):

    def setUp(self):
        XMLConfig('metameta.zcml', Zope.Configuration)()
        XMLConfig('metametaForDocgen.zcml', Zope.Configuration)()


    def testDescription(self):
        xmlconfig(makeconfig(
            '''<directive
                   name="doit"
                   description="Just Do It"
                   handler="Zope.Configuration.tests.Directives.doit" />''',
            '''<test:doit name="splat" />'''
            ))
        self.assertEqual(done, ['splat'])
        md = _directives[(ns, 'doit')][1][_metadataKey]
        self.assertEqual(md['description'], "Just Do It")

    def testAttribute(self):
        xmlconfig(makeconfig(
            '''<directive
                   name="doit"
                   handler="Zope.Configuration.tests.Directives.doit"
               >
                 <attribute
                     name="name"
                     required="Yes"
                     description="Just Do It" />
                 <attribute
                     name="opt1"
                     required="no"
                     description="ho hum" />
                 <attribute
                     name="opt2"
                     description="ho hummer" />
               </directive>''',
            '''<test:doit name="splat" />'''
            ))
        self.assertEqual(done, ['splat'])
        md = _directives[(ns, 'doit')][1][_metadataKey]['attributes']['name']
        self.assertEqual(md['description'],'Just Do It')
        self.assertEqual(md['required'],'yes')
        md = _directives[(ns, 'doit')][1][_metadataKey]['attributes']['opt1']
        self.assertEqual(md['description'],'ho hum')
        self.assertEqual(md['required'],'no')
        md = _directives[(ns, 'doit')][1][_metadataKey]['attributes']['opt2']
        self.assertEqual(md['description'],'ho hummer')
        self.assertEqual(md['required'],'')

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
