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

$Id: IChecker.py,v 1.2 2002/06/10 23:29:34 jim Exp $
"""

from Interface import Interface

class IChecker(Interface):
    """Security-proxy plugin objects that implement low-level checks

    The checker is responsible for creating proxies for
    operation return values, via the proxy method.

    There are check_getattr() and check_setattr() methods for checking
    getattr and setattr, and a check() method for all other operations.

    The check methods may raise errors.  They return no value.

    Example (for __getitem__):

           checker.check(ob, "__getitem__")
           return checker.proxy(ob[key])
    """

    def check_getattr(ob, name):
        """Check whether attribute access is allowed.
        """

    def check_setattr(ob, name):
        """Check whether attribute assignment is allowed.
        """

    def check(ob, operation):
        """Check whether operation is allowed.

        The operation name is the Python special method name,
        e.g. "__getitem__".
        """

    def proxy(value):
        """Return a security proxy for the value.
        """
