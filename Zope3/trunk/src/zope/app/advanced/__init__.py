##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Advanced package

Perform important XML import checks.

$Id: __init__.py,v 1.2 2004/04/01 17:40:49 philikon Exp $
"""
_MAXIMUM_XMLMINUS_VERSION = (0, 6, 1)

try:
    import _xmlminus
except ImportError:
    pass
else:
    try:
        v = _xmlminus.version_info
    except AttributeError:
        # _xmlminus is too young; ignore it
        pass
    else:
        if v >= _MAXIMUM_XMLMINUS_VERSION:
            import sys
            sys.modules[__name__] = _xmlminus
        else:
            del v
