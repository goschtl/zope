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
"""A registration for a cache.

$Id: cache.py,v 1.3 2003/06/21 21:22:10 jim Exp $
"""

from zope.app.interfaces.services.registration \
     import INamedComponentRegistration

class ICacheRegistration(INamedComponentRegistration):
    """Cache registration

    Cache registrations are dependent on the caches that they configure. They
    register themselves as component dependents.
    """
