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
import unittest
from Zope.Configuration.tests.Directives \
     import protectClass, protections, doit, done
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup
from Zope.Configuration import name

ns='http://www.zope.org/NS/Zope3/test'

class MetaTest(CleanUp, unittest.TestCase):

    def testImport(self):
        import Zope.Configuration.meta
        
    def testDirective(self):
        from Zope.Configuration.meta \
             import register, registersub, begin, end, InvalidDirective

        self.assertRaises(InvalidDirective, begin, None, name, (ns, 'doit'))

        register((ns, 'doit'), doit)

        subs = begin(None, (ns, 'doit'), name, name='splat')
        (des, callable, args, kw), = end(subs)
        self.assertEqual(des, 'd')
        callable(*args)

        self.failUnless(done==['splat'])
        
    def testSimpleComplexDirective(self):
        from Zope.Configuration.meta \
             import register, registersub, begin, end, InvalidDirective

        subs = register((ns, 'protectClass'), protectClass)
        registersub(subs, (ns, 'protect'))

        subs=begin(None, (ns, 'protectClass'), name,
                   name=".Contact", permission="splat", names='update')

        (des, callable, args, kw), = end(subs)
        self.assertEqual(des, ('.Contact', 'update'))
        callable(*args)

        self.assertEquals(protections, [(".Contact", "splat", 'update')])
        
    def testComplexDirective(self):
        from Zope.Configuration.meta \
             import register, registersub, begin, sub, end, InvalidDirective

        subs = register((ns, 'protectClass'), protectClass)
        registersub(subs, (ns, 'protect'))

        subs = begin(None, (ns, 'protectClass'), name, name=".Contact")

        actions = end(sub(subs, (ns, 'protect'), name,
                          permission='edit', names='update'))
        (des, callable, args, kw), = actions
        self.assertEqual(des, ('.Contact', 'update'))
        callable(*args)

        actions = end(sub(subs, (ns, 'protect'), name,
                          permission='view', names='name email'))
        (des, callable, args, kw), = actions
        self.assertEqual(des, ('.Contact', 'name email'))
        callable(*args)

        self.assertEqual(tuple(end(subs)), ())

        self.assertEquals(protections, [
            (".Contact", "edit", 'update'),
            (".Contact", "view", 'name email'),
            ])

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(MetaTest)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
