##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
__doc__='''External Method Product Initialization
$Id: __init__.py,v 1.14 2001/11/28 15:50:59 matt Exp $'''
__version__='$Revision: 1.14 $'[11:-2]

import ExternalMethod

# This is the new way to initialize products.  It is hoped
# that this more direct mechanism will be more understandable.
def initialize(context):

    context.registerClass(
        ExternalMethod.ExternalMethod,
        constructors=(ExternalMethod.manage_addExternalMethodForm,
                       ExternalMethod.manage_addExternalMethod),
        icon='extmethod.gif',
        )

    context.registerHelp()
    context.registerHelpTitle('Zope Help')
