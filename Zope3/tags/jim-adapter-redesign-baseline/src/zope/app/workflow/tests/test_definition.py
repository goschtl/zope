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
"""Process Definition Tests

$Id$
"""
import unittest

from zope.interface.verify import verifyClass

from zope.app.workflow.interfaces import IProcessDefinition
from zope.app.workflow.definition import ProcessDefinition

from zope.app.workflow.interfaces import IProcessDefinitionElementContainer
from zope.app.workflow.definition import ProcessDefinitionElementContainer


class ProcessDefinitionTests(unittest.TestCase):

    def testInterface(self):
        verifyClass(IProcessDefinition, ProcessDefinition)

    def testPDCreation(self):
        pd = ProcessDefinition()
        pi = pd.createProcessInstance(None)



from zope.app.container.tests.test_icontainer import TestSampleContainer

class ProcessDefinitionElementContainerTests(TestSampleContainer):

    def testIProcessDefinitionElementContainer(self):
        verifyClass(IProcessDefinitionElementContainer,
                    ProcessDefinitionElementContainer)



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ProcessDefinitionTests),
        unittest.makeSuite(ProcessDefinitionElementContainerTests),
        ))

if __name__ == '__main__':
    unittest.main()
