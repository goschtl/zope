##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
from browser import BrowserView
from skin.standardmacros import StandardMacros

def initialize(context):
    zcml.load_site()
