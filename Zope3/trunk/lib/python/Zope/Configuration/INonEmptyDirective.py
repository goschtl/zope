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
"""Configuration directives that have subdirectives

$Id: INonEmptyDirective.py,v 1.2 2002/09/03 16:02:30 jim Exp $
"""
from Interface import Interface

class INonEmptyDirective(Interface):

    def __call__(**kw):
        """Compute complex directive handler

        Return an ISubdirectiveHandler.
        """
