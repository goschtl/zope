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
$Id: GadflyDAAddView.py,v 1.1 2002/11/05 17:34:39 alga Exp $
"""
from Zope.App.OFS.Services.ConnectionService.Views.Browser.AdapterAdd import \
     AdapterAdd
from Zope.App.OFS.Container.IAdding import IAdding


class GadflyDAAddView(AdapterAdd):
    """Provide a user interface for adding a Gadfly DA"""
    
    # This needs to be overridden by the actual implementation
    _adapter_factory_id = "GadflyDA"

