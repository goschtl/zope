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
from Zope.Configuration.meta import InvalidDirective, BrokenDirective
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
            '''<directive name="doit" namespace="%s"
                          handler="Zope.Configuration.tests.Directives.doit" />
                          ''' % ns,
            '<test:doit name="splat" />'
            )))

        self.assertEqual(done, ['splat'])
        
    def testSimpleComplexDirective(self):
        xmlconfig(StringIO(
            template % (
            '''<directive name="protectClass" namespace="%s"
            handler="Zope.Configuration.tests.Directives.protectClass">
                  <subdirective name="protect" namespace="%s" />
               </directive>
                          ''' % (ns, ns),
            '''<test:protectClass
              name=".Contact" permission="splat" names="update"
              />'''
            )))

        self.assertEquals(protections, [(".Contact", "splat", 'update')])
        
    def testComplexDirective(self):
        xmlconfig(StringIO(
            template % (
            '''<directive name="protectClass" namespace="%s"
            handler="Zope.Configuration.tests.Directives.protectClass">
                  <subdirective name="protect" namespace="%s" />
               </directive>
                          ''' % (ns, ns),
            '''<test:protectClass name=".Contact">
              <test:protect permission="edit" names='update' />
              <test:protect permission="view" names='name email' />
            </test:protectClass>'''
            )))

        self.assertEquals(protections, [
            (".Contact", "edit", 'update'),
            (".Contact", "view", 'name email'),
            ])
        
    def testBadNoPrefixComplexDirective(self):

        self.assertRaises(
            InvalidDirective,
            testxmlconfig,
            StringIO(
            template % (
            '''<directive name="protectClass" namespace="%s"
                   handler="Zope.Configuration.tests.Directives.protectClass">
                  <subdirective name="protect" namespace="%s" />
               </directive>
                          ''' % (ns, ns),

            '''<test:protectClass name=".Contact">
              <test:protect permission="edit" names='update' />
              <protect permission="view" names='name email' />
              </test:protectClass>'''
            )))
        
    def testBadPrefixComplexDirective(self):

        try:
            testxmlconfig(
                StringIO(
                template % (
            '''<directive name="protectClass" namespace="%s"
                   handler="Zope.Configuration.tests.Directives.protectClass">
                  <subdirective name="protect" namespace="%s" />
               </directive>
                          ''' % (ns, ns),

                '''<test:protectClass name=".Contact">
                <test2:protect permission="edit" names='update' />
                </test:protectClass>'''
                )))
        except InvalidDirective, v:
            self.assertEqual(str(v), "(None, u'test2:protect')")
        else:
            self.fail('Should have raised ZopeXMLConfigurationError')


    def testInclude(self):
        from tempfile import mktemp
        name = mktemp()
        open(name, 'w').write(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
            <include package="Zope.Configuration.tests.Contact"
                     file="contact.zcml" />
            </zopeConfigure>""")

        from Zope.Configuration.xmlconfig import XMLConfig
        x = XMLConfig(name)
        x()
        import os
        os.remove(name)

    def testIncludeNoPackageAndIncluderNoPackage(self):
        from tempfile import mktemp
        from os.path import split
        full_name = mktemp()
        full_name1 = mktemp()
        name1 = split(full_name1)[-1]
        
        open(full_name, 'w').write(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
            <include file="%s" />
            </zopeConfigure>""" % name1)
        open(full_name1, 'w').write(
            """<zopeConfigure xmlns='http://namespaces.zope.org/zope'>
            <include package="Zope.Configuration.tests.Contact"
                     file="contact.zcml" />
            </zopeConfigure>""")
        from Zope.Configuration.xmlconfig import XMLConfig
        x = XMLConfig(full_name)
        x()
        import os
        os.remove(full_name)
        os.remove(full_name1)
        

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
