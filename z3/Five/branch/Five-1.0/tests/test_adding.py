##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Test adding views

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_suite():
    from Testing.ZopeTestCase import installProduct, ZopeDocFileSuite
    installProduct('Five')
    return ZopeDocFileSuite('adding.txt',
                            package="Products.Five.tests")

if __name__ == '__main__':
    framework()
