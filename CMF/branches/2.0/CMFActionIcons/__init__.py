##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
""" Product: CMFActionIcons

Define tool for mapping CMF actions onto icons.

$Id$
"""

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import ToolInit
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry

import ActionIconsTool

actionicons_globals = globals()

registerDirectory( 'skins', actionicons_globals )

def initialize( context ):

    ToolInit( meta_type='CMF Action Icons Tool'
            , tools=( ActionIconsTool.ActionIconsTool, )
            , icon="tool.gif"
            ).initialize( context )

    profile_registry.registerProfile('actionicons',
                                     'CMFActionIcons',
                                     'Adds action icon tool / settings.',
                                     'profiles/actionicons',
                                     'CMFActionIcons',
                                     EXTENSION,
                                     for_=ISiteRoot,
                                     )
