##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: IZopeDublinCoreAnnotatable.py,v 1.2 2002/10/04 19:05:50 jim Exp $
"""

from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable

class IZopeDublinCoreAnnotatable(IAnnotatable):
    """Objects that can be annotated with Zope Dublin-Core meta data

    This is a marker interface that indicates the intent to have
    Zope Dublin-Core meta data associated with an object.

    """

__doc__ = IZopeDublinCoreAnnotatable.__doc__ + __doc__
