##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Demo StandardMacros

$Id$
"""
from Products.Five import StandardMacros as BaseMacros

class StandardMacros(BaseMacros):

    macro_pages = ('bird_macros', 'dog_macros')
    aliases = {'flying':'birdmacro',
               'walking':'dogmacro'}
