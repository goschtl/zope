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
$Id: gadflyda.py,v 1.2 2003/04/30 23:37:53 faassen Exp $
"""
from zope.app.browser.rdb.rdb import AdapterAdd

class GadflyDAAddView(AdapterAdd):
    """Provide a user interface for adding a Gadfly DA"""

    # This needs to be overridden by the actual implementation
    _adapter_factory_id = "GadflyDA"
