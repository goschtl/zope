##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

$Id: request.py,v 1.2 2002/12/25 14:13:32 jim Exp $
"""

class Request:

    def __init__(self, iface, skin=''):
        self._iface     = iface
        self._skin      = skin

    def getPresentationSkin(self):
        '''See interface IPresentationRequest'''

        return self._skin

    def getPresentationType(self):
        '''See interface IPresentationRequest'''

        return self._iface
