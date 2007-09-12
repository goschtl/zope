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
"""Tests of gateway_fs.params

$Id$
"""

import unittest

from apelib.fs.params import string_to_params, params_to_string


class ParamsTests(unittest.TestCase):

    def test_string_to_params(self):
        s = 'abc def="123 456\\n \\"done\\" " ghi=4 j567 \n'
        params = string_to_params(s)
        self.assertEqual(tuple(params), (
            ('abc', ''),
            ('def', '123 456\n "done" '),
            ('ghi', '4'),
            ('j567', ''),
            ))

    def test_params_to_string(self):
        params = (
            ('abc', ''),
            ('def', '123 456\n "done" '),
            ('ghi', '4'),
            ('j567', ''),
            )
        s = params_to_string(params)
        self.assertEqual(s, 'abc def="123 456\\n \\"done\\" " ghi="4" j567')

    def test_invalid_keys(self):
        params_to_string((('abc_-09ABC', ''),))
        self.assertRaises(ValueError, params_to_string, (('a bc', ''),))
        self.assertRaises(ValueError, params_to_string, (('a\nbc', ''),))
        self.assertRaises(ValueError, params_to_string, (('', ''),))
        self.assertRaises(ValueError, params_to_string, ((' abc', ''),))
        self.assertRaises(ValueError, params_to_string, (('abc ', ''),))
        self.assertRaises(ValueError, params_to_string, (('a\tbc', ''),))
        self.assertRaises(ValueError, params_to_string, (('a\rbc', ''),))
        self.assertRaises(ValueError, params_to_string, (('a"bc', ''),))
        self.assertRaises(ValueError, params_to_string, (('0abc', ''),))


if __name__ == '__main__':
    unittest.main()

