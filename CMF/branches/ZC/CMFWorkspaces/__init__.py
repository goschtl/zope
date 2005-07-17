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
__doc__='''CMFWorkspaces Product Initialization
$Id$'''
__version__='$Revision$'[11:-2]

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

import Workspace


registerDirectory('skins', globals())


def initialize(context):

    context.registerBaseClass(Workspace.Workspace)

    ADD_FOLDERS_PERMISSION = 'Add portal folders'

    utils.ContentInit(
        'CMF Workspace',
        content_types=(Workspace.Workspace,),
        permission=ADD_FOLDERS_PERMISSION,
        extra_constructors=(Workspace.addWorkspace,),
        fti=Workspace.factory_type_information
        ).initialize( context )


