###############################################################################
#
# Copyright 2006 by refline (Schweiz) AG, CH-5630 Muri
#
###############################################################################
"""
$Id$
"""

import unittest

from z3c.authentication.cookie import testing


def test_suite():
    suite = unittest.TestSuite((
        testing.FunctionalDocFileSuite('BROWSER.txt'),
        ))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
