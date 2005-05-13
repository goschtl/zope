##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Form macros

$Id$
"""
from Products.Five.skin.standardmacros import StandardMacros

# copy of zope.app.form.browser.macros.FormMacros
class FormMacros(StandardMacros):    
    macro_pages = ('widget_macros', 'addform_macros')
