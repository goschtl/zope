##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Zope packaging utilities.

:organization: Zope Corporation
:license: `Zope Public License, Version 2.0 (ZPL)`__
:status: Prototype implementation

The Zope packaging utilities are the actual implementation of the
**zpkg** command line utility.

.. __: http://www.zope.org/Resources/ZPL

"""


class Error(Exception):
    """Base class for exceptions raised by zpkgtools."""
