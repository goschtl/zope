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
$Id: IZopeDublinCore.py,v 1.2 2002/10/04 19:05:50 jim Exp $
"""

from Zope.App.DublinCore.General \
     import IGeneralDublinCore, IWritableGeneralDublinCore
from Zope.App.DublinCore.ICMFDublinCore import ICMFDublinCore
from Zope.App.DublinCore.PropertySchemas \
     import IDCDescriptiveProperties, IDCTimes, IDCPublishing, IDCExtended


class IZopeDublinCore(
    IGeneralDublinCore,
    IWritableGeneralDublinCore,
    ICMFDublinCore,
    IDCDescriptiveProperties,
    IDCTimes,
    IDCPublishing,
    IDCExtended,
    ):
    """Zope Dublin Core properties
    """

__doc__ = IZopeDublinCore.__doc__ + __doc__
