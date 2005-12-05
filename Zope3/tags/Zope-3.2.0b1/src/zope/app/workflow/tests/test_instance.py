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
"""Process Instance Tests

$Id$
"""
import unittest
from zope.interface.verify import verifyClass

from zope.app.annotation.interfaces import IAnnotations
from zope.app.testing.placelesssetup import PlacelessSetup

from zope.app.workflow.interfaces import IProcessInstance
from zope.app.workflow.instance import ProcessInstance

from zope.app.workflow.interfaces import IProcessInstanceContainer
from zope.app.workflow.instance import ProcessInstanceContainerAdapter, WFKey
from zope.interface import implements

class TestAnnotations(dict):
    implements(IAnnotations)

class DummyInstance(object):
    pass


class ProcessInstanceTests(unittest.TestCase):

    def testInterface(self):
        verifyClass(IProcessInstance, ProcessInstance)


class ProcessInstanceContainerAdapterTests(PlacelessSetup, unittest.TestCase):

    def testInterface(self):
        verifyClass(IProcessInstanceContainer,
                    ProcessInstanceContainerAdapter)

    def testAdapter(self):

        annotations = TestAnnotations()
        di = DummyInstance()
        pica = ProcessInstanceContainerAdapter(annotations)

        self.assertEqual(annotations.keys(), [WFKey,])
        self.assertEqual(len(pica), 0)
        self.assertEqual(pica.keys(), [])
        self.assertEqual(pica.items(), [])
        self.assertEqual(pica.values(), [])
        self.assertEqual(pica.get('nothing', 1), 1)
        self.assertRaises(TypeError, pica.__setitem__, 123, None)

        pica['dummy'] = di
        self.assertEqual(len(pica), 1)
        self.assertEqual(pica.keys(), ['dummy'])
        self.assertEqual(pica.values(), [di])
        self.assertEqual(pica.items(), [('dummy', di,),])
        self.assertEqual(pica['dummy'], di)
        self.assertEqual(pica.get('dummy', 1), di)
        self.failUnless('dummy' in pica)

        del pica['dummy']

        self.assertEqual(len(pica), 0)
        self.failIf('dummy' in pica)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ProcessInstanceTests),
        unittest.makeSuite(ProcessInstanceContainerAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main()
