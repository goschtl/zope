##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Test that the Zope appserver configuration schema can be loaded.

$Id$
"""

import os
import doctest

import ZConfig

def test_schema(self):
    """Test the ZConfig schema.

    Test that it loads:

        >>> dir = os.path.dirname(os.path.dirname(__file__))
        >>> filename = os.path.join(dir, "schema.xml")
        >>> ZConfig.loadSchema(filename)
        <ZConfig.info.SchemaType instance at ...>
    """

def test_suite():
    return doctest.DocTestSuite(
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        )

if __name__ == "__main__":
    try:
        __file__
    except NameError:
        import sys
        __file__ = sys.argv[0]
    unittest.main(defaultTest="test_suite")
