##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

"""Stateful content workflow utility.

$Id: test_contentworkflow.py,v 1.1 2003/05/08 17:27:20 jack-e Exp $
"""
import unittest

from zope.interface import Interface
from zope.interface.verify import verifyClass

from zope.app.interfaces.workflow.stateful import IContentWorkflowsUtility
from zope.app.workflow.stateful.contentworkflow import ContentWorkflowsUtility



# XXX How to test this without fake a hole zope3-server ?????
class ContentWorkflowsUtilityTests(unittest.TestCase):

    def testInterface(self):
        verifyClass(IContentWorkflowsUtility,
                    ContentWorkflowsUtility)




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
        ContentWorkflowsUtilityTests))
    return suite

if __name__ == '__main__':
    unittest.main()
