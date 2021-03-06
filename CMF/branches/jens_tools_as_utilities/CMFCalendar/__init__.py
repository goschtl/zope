##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMF Calendar product.

$Id$
"""

from Products.CMFCore.utils import ContentInit
from Products.CMFCore.utils import ToolInit
from Products.CMFCore.DirectoryView import registerDirectory

import Event
import CalendarTool
from permissions import AddPortalContent


# Make sure security is initialized
import utils

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())

def initialize(context):

    ToolInit( 'CMF Calendar Tool'
            , tools=(CalendarTool.CalendarTool,)
            , icon='tool.gif'
            ).initialize( context )

    # BBB: register oldstyle constructors
    ContentInit( 'CMF Calendar Content'
               , content_types=()
               , permission=AddPortalContent
               , extra_constructors=(Event.addEvent,)
               ).initialize( context )
