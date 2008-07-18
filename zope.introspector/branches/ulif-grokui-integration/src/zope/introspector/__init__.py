##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Initialize zope.introspector package.

$Id$
"""
from objectinfo import ObjectInfo, ModuleInfo, PackageInfo, TypeInfo
from meta import priority
from descriptionprovider import DescriptionProvider

from zope.introspector.interfaces import IIntrospectorAPI
from zope.interface import moduleProvides
moduleProvides(IIntrospectorAPI)
__all__ = list(IIntrospectorAPI)
