##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""DT_SQLVar Tests

$Id: testArguments.py,v 1.1 2002/07/11 00:03:19 srichter Exp $
"""

import unittest
from Zope.App.OFS.Content.SQLScript.Arguments import \
     Arguments, parseArguments, InvalidParameter 


class TestDT_SQLVar(unittest.TestCase):

    def _compareArgumentObjects(self, result, args):
        self.assertEqual(args.items(), result.items())


    def testSimpleParseArgument(self):
        args = parseArguments('arg1')
        result = Arguments({'arg1': {}})
        self._compareArgumentObjects(result, args)


    def testParseArgumentWithType(self):
        args = parseArguments('arg1:int')
        result = Arguments({'arg1': {'type': 'int'}})
        self._compareArgumentObjects(result, args)


    def testParseArgumentWithDefault(self):
        args1 = parseArguments('arg1=value')
        result1 = Arguments({'arg1': {'default': 'value'}})
        self._compareArgumentObjects(result1, args1)

        args2 = parseArguments('arg1="value"')
        result2 = Arguments({'arg1': {'default': 'value'}})
        self._compareArgumentObjects(result2, args2)


    def testParseArgumentWithTypeAndDefault(self):
        args1 = parseArguments('arg1:string=value')
        result1 = Arguments({'arg1': {'default': 'value', 'type': 'string'}})
        self._compareArgumentObjects(result1, args1)

        args2 = parseArguments('arg1:string="value"')
        result2 = Arguments({'arg1': {'default': 'value', 'type': 'string'}})
        self._compareArgumentObjects(result2, args2)


    def testParseMultipleArguments(self):
        args1 = parseArguments('arg1:string=value arg2')
        result1 = Arguments({'arg1': {'default': 'value', 'type': 'string'},
                             'arg2': {}})
        self._compareArgumentObjects(result1, args1)

        args2 = parseArguments('arg1:string=value\narg2')
        result2 = Arguments({'arg1': {'default': 'value', 'type': 'string'},
                             'arg2': {}})
        self._compareArgumentObjects(result2, args2)


    def testParseErrors(self):
        self.assertRaises(InvalidParameter, parseArguments, 'arg1:""')  
        self.assertRaises(InvalidParameter, parseArguments, 'arg1 = value')  
        self.assertRaises(InvalidParameter, parseArguments, 'arg1="value\' ')  
        self.assertRaises(InvalidParameter, parseArguments, 'arg1:=value')



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(TestDT_SQLVar) )
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
