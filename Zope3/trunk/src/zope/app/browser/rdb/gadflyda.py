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
$Id: gadflyda.py,v 1.1 2003/02/07 15:48:39 jim Exp $
"""
from zope.app.browser.rdb.rdb import AdapterAdd
from zope.app.interfaces.container import IAdding


class GadflyDAAddView(AdapterAdd):
    """Provide a user interface for adding a Gadfly DA"""

    # This needs to be overridden by the actual implementation
    _adapter_factory_id = "GadflyDA"
