##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Stub to make old imports work.
"""

import pkg_resources

_dist_name = "zope.app.publisher"
_extra = 'zope_3_4_compat'
if _extra not in pkg_resources.get_distribution(_dist_name).extras:
    raise ImportError("The module '%s' is not available unless "
        "the %s egg is installed with the '%s' extra option."
        % (__name__, _dist_name, _extra))

from zope.deferredimport import deprecated

deprecated("This function has moved to zope.httpformdate.",
    field2date_via_datetimeutils=
        "zope.httpformdate:field2date_via_datetimeutils",
    registerZopeConverters=
        "zope.httpformdate:register",
    )
