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
"""Test Token Eater

$Id: test_tokeneater.py,v 1.1 2003/08/20 16:29:55 srichter Exp $
"""
import unittest
import tokenize
from StringIO import StringIO
from zope.app.translation_files.extract import TokenEater
from zope.app.translation_files.pygettext import make_escapes

class TokenEaterTest(unittest.TestCase):

    def setUp(self):
        self.eater = TokenEater()
        make_escapes(0)
        
    def test_msgid_and_default(self):
        file = StringIO("_('msgid', 'default')")
        tokenize.tokenize(file.readline, self.eater)
        msgid = self.eater._TokenEater__messages.keys()[0]
        self.assertEqual(msgid, 'msgid')
        self.assertEqual(msgid.default, 'default')


def test_suite():
    return unittest.makeSuite(TokenEaterTest)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
