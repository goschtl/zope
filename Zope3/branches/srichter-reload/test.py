#!/usr/bin/env python2.4
##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Test script

$Id$
"""
import sys, os

here = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(here, 'src'))

# remove the current directory from the path, otherwise if we try to
# import the standard library package "test", we get this file instead
sys.path[:] = [p for p in sys.path if p != here]

import zope.app.testing.test

if __name__ == '__main__':
    zope.app.testing.test.process_args()
