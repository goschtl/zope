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
"""

$Id: testFileEdit.py,v 1.3 2002/11/04 22:11:00 jim Exp $
"""

import unittest

from Zope.App.OFS.Content.File.Views.Browser.FileEdit import FileEdit
from Zope.App.OFS.Content.File.File import File


class Test( unittest.TestCase ):

    def testEdit(self):
        """ """
        file = File()

        fe = FileEdit(file, None) 

        fe.context.edit('Data', 'text/plain')
        self.assertEqual(fe.context.getContentType(), 'text/plain')
        self.assertEqual(fe.context.getData(), 'Data')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.main()
