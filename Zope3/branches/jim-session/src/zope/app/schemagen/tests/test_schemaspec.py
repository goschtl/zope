##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id$
"""

from unittest import TestCase, makeSuite, TestSuite
from zope.app.schemagen.schemaspec import SchemaSpec
from zope.schema import Text
import os

def openInTests(name, mode):
    return open(os.path.join(os.path.dirname(__file__), name), mode)

class SchemaSpecTests(TestCase):

    def setUp(self):
        self.s = SchemaSpec('IFoo')
        self.alpha = Text(title=u"alpha")

    def test_addField(self):
        s = self.s
        s.addField('alpha', self.alpha)
        self.assertEquals(
            [('alpha', self.alpha)],
            s.getFieldsInOrder())

    def test_removeField(self):
        s = self.s
        s.addField('alpha', self.alpha)
        s.removeField('alpha')
        self.assertEquals(
            [],
            s.getFieldsInOrder())

    def test_addFieldCollision(self):
        s = self.s
        s.addField('alpha', self.alpha)
        self.assertRaises(KeyError, s.addField, 'alpha', self.alpha)

    def test_removeFieldNotPresent(self):
        self.assertRaises(KeyError, self.s.removeField, 'alpha')

    def test_renameField(self):
        s = self.s
        s.addField('alpha', self.alpha)
        s.renameField('alpha', 'beta')
        self.assertEquals(
            [('beta', self.alpha)],
            s.getFieldsInOrder())

    def test_renameFieldCollision(self):
        s = self.s
        s.addField('alpha', self.alpha)
        s.addField('beta', Text(title=u"Beta"))
        self.assertRaises(KeyError, s.renameField, 'alpha', 'beta')

    def test_renameFieldNotPresent(self):
        self.assertRaises(KeyError, self.s.renameField, 'alpha', 'beta')

    def test_insertField(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        s.insertField('beta', beta, 0)
        self.assertEquals(
            [('beta', beta),
             ('alpha', self.alpha)],
            s.getFieldsInOrder())

    def test_insertFieldCollision(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        self.assertRaises(KeyError, s.insertField, 'alpha', beta, 0)

    def test_insertFieldCornerCases(self):
        s = self.s
        gamma = Text(title=u"Gamma")
        # it's still possible to insert at beginning
        s.insertField('gamma', gamma, 0)
        self.assertEquals(
            [('gamma', gamma)],
            s.getFieldsInOrder())
        # should be allowed to insert field at the end
        s.insertField('alpha', self.alpha, 1)
        self.assertEquals(
            [('gamma', gamma),
             ('alpha', self.alpha)],
            s.getFieldsInOrder())
        # should be allowed to insert field at the beginning still
        delta = Text(title=u"Delta")
        s.insertField('delta', delta, 0)
        self.assertEquals(
            [('delta', delta),
             ('gamma', gamma),
             ('alpha', self.alpha)],
            s.getFieldsInOrder())

    def test_insertFieldBeyondEnd(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        self.assertRaises(IndexError, s.insertField,
                          'beta', beta, 100)

    def test_insertFieldBeforeBeginning(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        self.assertRaises(IndexError, s.insertField,
                          'beta', beta, -1)

    def test_moveField(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u'Beta')
        s.addField('beta', beta)
        gamma = Text(title=u'Gamma')
        s.addField('gamma', gamma)
        s.moveField('beta', 3)
        self.assertEquals(
            [('alpha', self.alpha),
             ('gamma', gamma),
             ('beta', beta)],
            s.getFieldsInOrder())

    def test_moveFieldBeyondEnd(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        s.addField('beta', beta)
        self.assertRaises(IndexError, s.moveField,
                          'beta', 100)

    def test_moveFieldBeforeBeginning(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        s.addField('beta', beta)
        self.assertRaises(IndexError, s.moveField,
                          'beta', -1)

    # XXX the following tests compare python source text
    # this is very dependent on whitespace issues, which we really
    # don't care about. Is there a better way? (compare some form of AST?)
    def test_history(self):
        s = self.s
        alpha = Text(title=u'Alpha')
        beta = Text(title=u'Beta')
        gamma = Text(title=u'Gamma')
        delta = Text(title=u'Delta')

        history = []
        self.assertEquals(0, s.getCurrentVersion())
        history.append(s.addField('alpha', alpha))
        self.assertEquals(1, s.getCurrentVersion())
        history.append(s.removeField('alpha'))
        self.assertEquals(2, s.getCurrentVersion())
        history.append(s.addField('beta', beta))
        self.assertEquals(3, s.getCurrentVersion())
        history.append(s.insertField('gamma', gamma, 0))
        self.assertEquals(4, s.getCurrentVersion())
        history.append(s.moveField('gamma', 2))
        self.assertEquals(5, s.getCurrentVersion())
        history.append(s.renameField('gamma', 'gamma2'))
        self.assertEquals(6, s.getCurrentVersion())

        # just to verify we know what happened
        self.assertEquals(
            [('beta', beta),
             ('gamma2', gamma)],
            s.getFieldsInOrder())
        # now compare history
        self.assertEquals(history, s.getHistory())

        # check whether generated source is as we expect
        f = openInTests('setstate.py.txt', 'r')
        source = f.read()
        f.close()
        self.assertEquals(source, s.generateSetstateSource())

    def test_generateModuleSource(self):
        s = self.s
        s.addField('alpha', self.alpha)

        f = openInTests('setstatemodule.py.txt', 'r')
        source = f.read()
        f.close()
        self.assertEquals(source, s.generateModuleSource())

    def test_generateModuleSourceNoHistory(self):
        # no history, so expect no setstate
        f = openInTests('setstatemodule_no_history.py.txt', 'r')
        source = f.read()
        f.close()
        self.assertEquals(source.strip(),
                          self.s.generateModuleSource().strip())

    def test_prepareSetstate(self):
        from zope.app.schemagen.schemaspec import prepareSetstate
        class DummySchemaClass(object):
            pass
        obj = DummySchemaClass()
        state = { '__schema_version__': 1, 'foo': 'baz' }
        version = 2
        d = prepareSetstate(obj, state, version)
        self.assertEquals({ 1: 1}, d)
        self.assertEquals(obj.foo, 'baz')
        self.assertEquals(obj.__schema_version__, 2)

class ModuleUsageTests(TestCase):

    def executeModule(self, s):
        source = s.generateModuleSource()
        g = {}
        exec source in g
        del g['__builtins__'] # to ease inspection during debugging
        return g

    def test_setstate(self):
        s = SchemaSpec('IFoo', 'Foo')
        s.addField('alpha', Text(title=u'Alpha'))
        s.addField('beta', Text(title=u'Beta', default=u"default"))
        g = self.executeModule(s)
        foo = g['Foo']()
        self.assertEquals(foo.__schema_version__, 2)
        self.assertEquals(foo.beta, u"default")

        foo.beta = u"Frog"
        # this is evil, but we do this for testing
        foo.__schema_version__ = 1
        # do the automatical upgrade according to schema
        foo.__setstate__(foo.__getstate__())
        self.assertEquals(foo.beta, u"default")
        self.assertEquals(foo.__schema_version__, 2)

def test_suite():
    return TestSuite(
        (makeSuite(SchemaSpecTests),
         makeSuite(ModuleUsageTests),
         ))
