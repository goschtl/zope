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
"""Provide a standard cleanup registry

Unit tests that change global data should include the CleanUp base
class, which provides simpler setUp and tearDown methods that call
global-data cleanup routines::

  class Test(CleanUp, unittest.TestCase):

      ....

If custom setUp or tearDown are needed, then the base reoutines should
be called, as in::

  def tearDown(self):
      CleanUp.tearDown(self)
      ....

Cleanup routines for global data should be registered by passing them to
addCleanup::


  addCleanUp(roleRegistry._clear)


Revision information:
$Id: cleanup.py,v 1.3 2004/01/10 11:01:15 philikon Exp $
"""

__metaclass__ = type

_cleanups = []

def addCleanUp(func, args=(), kw={}):
    """Register a cleanup routines

    Pass a function to be called to cleanup global data.
    Optional argument tuple and keyword arguments may be passed.
    """
    _cleanups.append((func, args, kw))

class CleanUp:
    """Mix-in class providing clean-up setUp and tearDown routines."""

    def cleanUp(self):
        """Clean up global data."""
        for func, args, kw in _cleanups:
            func(*args, **kw)

    setUp = tearDown = cleanUp
