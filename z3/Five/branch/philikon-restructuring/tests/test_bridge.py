##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
""" Unit tests for Z2 -> Z3 bridge utilities.

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeDocFileSuite

def test_suite():
    return ZopeDocFileSuite('bridge.txt', package="Products.Five.tests")

if __name__ == '__main__':
    framework()
