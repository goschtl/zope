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
from cStringIO import StringIO
from Zope.Configuration.xmlconfig import xmlconfig, ZopeXMLConfigurationError
from Zope.Configuration.xmlconfig import testxmlconfig
from Zope.Configuration.meta import InvalidDirective
from Zope.Configuration.tests.Directives import protections, done
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:test='http://www.zope.org/NS/Zope3/test'>
   %s
   %s
   </zopeConfigure>"""


ns='http://www.zope.org/NS/Zope3/test'

class Test(CleanUp, unittest.TestCase):
        
    def testDirective(self):
        xmlconfig(StringIO(
            template % (
            '''<directives  namespace="%s">
                   <directive name="doit"
                    handler="Zope.Configuration.tests.Directives.doit" />
               </directives>''' % ns,
            '<test:doit name="splat" />'
            )))

        self.assertEqual(done, ['splat'])
        
    def testSimpleComplexDirective(self):
        xmlconfig(StringIO(
            template % (
            '''<directives  namespace="%s">
                   <directive name="protectClass"
                    handler="Zope.Configuration.tests.Directives.protectClass">
                       <subdirective name="protect"/>
               </directive>
               </directives>
                          ''' % ns,
            '''<test:protectClass
                   name=".Contact" permission="splat" names="update"
               >
                 <test:protect permission="beep" names="update" />
               </test:protectClass>'''
            )))
        
        self.assertEquals(protections, [(".Contact", "beep", 'update')])

    def testDirectiveDirective(self):
        xmlconfig(StringIO(
            template % (
            '''<directive name="protectClass" namespace="%s"
                    handler="Zope.Configuration.tests.Directives.protectClass">
                       <subdirective name="protect"/>
               </directive>
                          ''' % ns,
            '''<test:protectClass
                   name=".Contact" permission="splat" names="update"
               >
                 <test:protect permission="beep" names="update" />
               </test:protectClass>'''
            )))

        self.assertEquals(protections, [(".Contact", "beep", 'update')])
        
    def testComplexDirective(self):
        xmlconfig(StringIO(
            template % (
            '''<directives  namespace="%s">
                   <directive name="protectClass"
                    handler="Zope.Configuration.tests.Directives.protectClass">
                      <subdirective name="protect" />
                   </directive>
               </directives>''' % ns,
            '''<test:protectClass name=".Contact">
                <test:protect permission="edit" names='update' />
                <test:protect permission="view" names='name email' />
              </test:protectClass>'''
            )))

        self.assertEquals(protections, [
            (".Contact", "edit", 'update'),
            (".Contact", "view", 'name email'),
            ])
        
    def testSubSubdirective(self):
        xmlconfig(StringIO(
            template % (
            '''<directives  namespace="%s">
                 <directive name="protectClass"
                    handler="Zope.Configuration.tests.Directives.protectClass">
                       <subdirective name="subsub">
                           <subdirective name="protect"/>
                       </subdirective>
                 </directive>
               </directives>
                          ''' % ns,
            '''<test:protectClass
                   name=".Contact" permission="splat" names="update"
               >
                 <test:subsub>
                   <test:protect permission="beep" names="update" />
                 </test:subsub>
               </test:protectClass>'''
            )))
        
        self.assertEquals(protections, [(".Contact", "beep", 'update')])

    def testHandlerMethod(self):
        xmlconfig(StringIO(
            template % (
            '''<directives  namespace="%s">
                   <directive name="protectClass"
                    handler="Zope.Configuration.tests.Directives.protectClass">
                      <subdirective name="fish"
                                    handler_method="protect" />
                   </directive>
               </directives>''' % ns,
            '''<test:protectClass name=".Contact">
                <test:fish permission="edit" names='update' />
                <test:fish permission="view" names='name email' />
              </test:protectClass>'''
            )))

        self.assertEquals(protections, [
            (".Contact", "edit", 'update'),
            (".Contact", "view", 'name email'),
            ])
        
        
    def testBadNoPrefixComplexDirective(self):

        self.assertRaises(
            InvalidDirective,
            xmlconfig,
            StringIO(
            template % (
            '''<directives  namespace="%s">
                   <directive name="protectClass"
                    handler="Zope.Configuration.tests.Directives.protectClass">
                  <subdirective name="protect" />
               </directive>
               </directives>''' % ns,

            '''<test:protectClass name=".Contact">
              <test:protect permission="edit" names='update' />
              <protect permission="view" names='name email' />
              </test:protectClass>'''
            )),
            testing=1)
        
    def testBadPrefixComplexDirective(self):

        try:
            testxmlconfig(
                StringIO(
                template % (
            '''<directives  namespace="%s">
                   <directive name="protectClass"
                    handler="Zope.Configuration.tests.Directives.protectClass">
                  <subdirective name="protect" />
               </directive>
               </directives>''' % ns,

                '''<test:protectClass name=".Contact">
                <test2:protect permission="edit" names='update' />
                </test:protectClass>'''
                )))
        except InvalidDirective, v:
            self.assertEqual(str(v), "(None, u'test2:protect')")
        else:
            self.fail('Should have raised ZopeXMLConfigurationError')
        

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
