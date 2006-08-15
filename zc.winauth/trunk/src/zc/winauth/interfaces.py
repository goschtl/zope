##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Additional interfaces for zc.winauth.

"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema


class IUserInfo(zope.interface.Interface):

    """Additional user information provided by the zc.winauth plugin."""

    name = zope.schema.TextLine(
        title=u"Short name for the login account",
        description=u"This is usually the login name for the user.",
        )
