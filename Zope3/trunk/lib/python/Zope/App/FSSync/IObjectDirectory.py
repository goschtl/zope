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
$Id: IObjectDirectory.py,v 1.2 2002/10/11 06:28:05 jim Exp $
"""

from IObjectEntry import IObjectEntry

class IObjectDirectory(IObjectEntry):
    """File-system object representation for directory-like objects
    """

    def contents():
        """Return the contents

        A sequence of name, value object are returned. The value in each
        pair will be syncronized.
        """

__doc__ = IObjectDirectory.__doc__ + __doc__
