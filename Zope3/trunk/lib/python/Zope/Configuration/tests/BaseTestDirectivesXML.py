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
"""Tests of the XML parsing machinery

This mixin passes a series of sets of configuration directives
to xmlconfig to make sure the right things happen.  The
directives first define one or or more new directives, implemented
by code in the Directives.py module, and then use those
directives.  The tests check to make sure the expected actions
were taken, or the expected errors raised.

These tests test only the capabilities of the meta-directives
implemented by the bootstrap versions.

$Id: BaseTestDirectivesXML.py,v 1.3 2002/11/06 22:35:42 rdmurray Exp $
"""

from cStringIO import StringIO
from Zope.Configuration.meta import InvalidDirective
from Zope.Configuration.xmlconfig import xmlconfig, testxmlconfig
from Zope.Configuration.tests.Directives import protections, done

ns = 'http://www.zope.org/NS/Zope3/test'

def makeconfig(metadirectives,directives):
    return StringIO(
        '''<zopeConfigure
               xmlns="http://namespaces.zope.org/zope"
               xmlns:test="%(ns)s">
            <directives namespace="%(ns)s">
              %(metadirectives)s
            </directives>
            %(directives)s
            </zopeConfigure>''' % {
                'metadirectives': metadirectives,
                'directives': directives,
                'ns': ns})


class directiveTests:

    def testDirective(self):
        xmlconfig(makeconfig(
            '''<directive
                   name="doit"
                   handler="Zope.Configuration.tests.Directives.doit" />''',
            '''<test:doit name="splat" />'''
            ))
        self.assertEqual(done, ['splat'])
        
    def testSimpleComplexDirective(self):
        xmlconfig(makeconfig(
            '''<directive
                   name="protectClass"
                   handler="Zope.Configuration.tests.Directives.protectClass">
                 <subdirective name="protect" namespace="%s" />
               </directive>''',
            '''<test:protectClass
                   name=".Contact" permission="splat" names="update" />'''
            ))
        self.assertEquals(protections, [(".Contact", "splat", 'update')])
        
    def testComplexDirective(self):
        xmlconfig(makeconfig(
            '''<directive
                   name="protectClass"
                   handler="Zope.Configuration.tests.Directives.protectClass">
                 <subdirective name="protect" />
               </directive>''',
            '''<test:protectClass name=".Contact">
               <test:protect permission="edit" names='update' />
               <test:protect permission="view" names='name email' />
               </test:protectClass>'''
            ))
        self.assertEquals(protections, [
            (".Contact", "edit", 'update'),
            (".Contact", "view", 'name email'),
            ])

    def testSubSubdirective(self):
        xmlconfig(makeconfig(
            '''<directive name="protectClass"
                   handler="Zope.Configuration.tests.Directives.protectClass">
                 <subdirective name="subsub">
                   <subdirective name="subsub">
                     <subdirective name="subsub">
                       <subdirective name="subsub">
                         <subdirective name="protect"/>
                       </subdirective>
                     </subdirective>
                   </subdirective>
                 </subdirective>
               </directive>''',
            '''<test:protectClass
                   name=".Contact" permission="splat" names="update"
               >
                 <test:subsub>
                   <test:subsub>
                     <test:subsub>
                       <test:subsub> 
                         <test:protect permission="beep" names="update" />
                       </test:subsub>
                     </test:subsub>
                   </test:subsub>
                 </test:subsub>
               </test:protectClass>'''
            ))
        self.assertEquals(protections, [(".Contact", "beep", 'update')])

    def testHandlerMethod(self):
        xmlconfig(makeconfig(
            '''<directive name="protectClass"
                   handler="Zope.Configuration.tests.Directives.protectClass">
                 <subdirective
                     name="fish"
                     handler_method="protect" />
               </directive>''',
            '''<test:protectClass name=".Contact">
                 <test:fish permission="edit" names='update' />
                 <test:fish permission="view" names='name email' />
              </test:protectClass>'''
            ))
        self.assertEquals(protections, [
            (".Contact", "edit", 'update'),
            (".Contact", "view", 'name email'),
            ])

    def testBadNoPrefixComplexDirective(self):
        self.assertRaises(
            InvalidDirective,
            testxmlconfig,
            makeconfig(
              '''<directive
                     name="protectClass"
                     handler="Zope.Configuration.tests.Directives.protectClass">
                   <subdirective name="protect" namespace="%s" />
                 </directive>''',
              '''<test:protectClass name=".Contact">
                 <test:protect permission="edit" names='update' />
                 <protect permission="view" names='name email' />
                 </test:protectClass>
              '''))
        
    def testBadPrefixComplexDirective(self):
        try: testxmlconfig(makeconfig(
            '''<directive
                   name="protectClass"
                   handler="Zope.Configuration.tests.Directives.protectClass">
                 <subdirective name="protect" namespace="%s" />
               </directive>''',
            '''<test:protectClass name=".Contact">
               <test2:protect permission="edit" names='update' />
               </test:protectClass>''')),
        except InvalidDirective, v:
            self.assertEqual(str(v), "(None, u'test2:protect')")
        else:
            self.fail('Should have raised InvalidDirective')
