##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Initialize the Five product

$Id$
"""
import Acquisition
import monkey

# trigger monkey patches
monkey.monkeyPatch()
