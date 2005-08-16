##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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

"""Compatibility module for gettext.py

gettext.py is a standard library module in Python, however we want the version
in Python 2.3.  But since Zope3's minimum requirement is currently Python
2.2.x, we need this compatibility layer.

$Id: gettext.py,v 1.1 2003/04/11 19:13:27 bwarsaw Exp $
"""

from pythonlib import load_compat
load_compat('gettext', globals())
