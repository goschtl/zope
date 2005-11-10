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

# This is used by a script (external method) that can be run
# to set up Events in an existing CMF Site instance.
cmfcalendar_globals = globals()

def initialize( context ):
    from Products.CMFCore.utils import ContentInit
    from Products.CMFCore.utils import ToolInit
    from Products.CMFCore.DirectoryView import registerDirectory
    from Products.GenericSetup import EXTENSION
    from Products.GenericSetup import profile_registry

    import Event
    import CalendarTool
    from permissions import AddPortalContent


    tools = ( CalendarTool.CalendarTool, )
    ToolInit( 'CMF Calendar Tool'
            , tools=tools, icon='tool.gif'
            ).initialize( context )

    contentConstructors = (Event.addEvent,)
    contentClasses = (Event.Event,)
    ContentInit( 'CMF Event'
               , content_types = contentClasses
               , permission = AddPortalContent
               , extra_constructors = contentConstructors
               ).initialize( context )

    profile_registry.registerProfile('default',
                                     'CMFCalendar',
                                     'Adds calendar support.',
                                     'profiles/default',
                                     'CMFCalendar',
                                     EXTENSION)
    registerDirectory('skins', cmfcalendar_globals)

    context.registerHelpTitle('CMF Calendar Help')
    context.registerHelp(directory='help')
