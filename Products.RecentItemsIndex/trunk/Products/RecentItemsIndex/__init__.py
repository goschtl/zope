##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""RecentItemsIndex Zope product

A ZCatalog plug-in-index for indexing recent items matching a specific field
value.

$Id: __init__.py,v 1.1.1.1 2004/07/19 17:46:21 caseman Exp $"""

import index

def initialize(context):

    context.registerClass(
        index.RecentItemsIndex,
        meta_type='RecentItemsIndex',
        permission='Add Pluggable Index',
        constructors=(index.addIndexForm,),
        icon='www/index.gif',
        visibility=None
    )
