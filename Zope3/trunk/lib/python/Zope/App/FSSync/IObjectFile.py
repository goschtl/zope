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
$Id: IObjectFile.py,v 1.2 2002/10/11 06:28:05 jim Exp $
"""

from IObjectEntry import IObjectEntry

class IObjectFile(IObjectEntry):
    """File-system object representation for file-like objects
    """

    def getBody():
        """Return the file body"""

    def setBody():
        """Change the file body"""

__doc__ = IObjectFile.__doc__ + __doc__
