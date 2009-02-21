##############################################################################
#
# Copyright (c) 2005-2009 Zope Foundation and Contributors.
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
"""
$Id$
"""

import zope.deferredimport

zope.deferredimport.initialize()
zope.deferredimport.deprecated(
    "z3c.viewlet is deprecated, all its functionality moved to zope.viewlet.",
    getWeight = 'zope.viewlet.manager:getWeight',
    WeightOrderedViewletManager = 'zope.viewlet.manager:WeightOrderedViewletManager')
