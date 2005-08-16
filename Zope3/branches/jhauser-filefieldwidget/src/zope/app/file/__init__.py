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
"""File content components

$Id$
"""
__docformat__ = 'restructuredtext'

from file import File
try:
    # TODO: solve recursion and add real BBB
    # I see no way for doing this right now, perhaps we have to move the 
    # zope.app.image package back to zope.app.file
    from zope.app.image import Image, getImageInfo
except:
    pass
