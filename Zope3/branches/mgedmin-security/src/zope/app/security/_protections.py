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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Register protection information for some standard low-level types

$Id: _protections.py,v 1.10 2004/02/21 12:28:55 jim Exp $
"""

def protect():
    from zope.security.checker import defineChecker, NamesChecker, NoProxy

    # Make sure the message id gets never proxied
    from zope.i18n.messageid import MessageID
    defineChecker(MessageID, NoProxy)

    # add __parent__ and __name__ to always available names
    import zope.security.checker
    for name in ['__name__', '__parent__']:
        if name not in zope.security.checker._always_available:
            zope.security.checker._always_available.append(name)
