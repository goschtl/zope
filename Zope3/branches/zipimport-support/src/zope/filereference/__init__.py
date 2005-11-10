##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""References to file-like things, including files inside zipped packages.

This supports referencing files within Python eggs.

"""
__docformat__ = "reStructuredText"

import zope.interface


from reference import open, new, exists, isdir, isfile, getmtime


from interfaces import IFileReferenceAPI
zope.interface.moduleProvides(IFileReferenceAPI)
