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
from Globals import INSTANCE_HOME

import monkey
import zcml

# trigger monkey patches
monkey.monkeyPatch()

# public API provided by Five
# usage: from Products.Five import <something>
from browser import BrowserView, StandardMacros

def initialize(context):
    zcml.load_site()
