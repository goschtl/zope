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
import os

import Acquisition
from Globals import INSTANCE_HOME

import monkey
import zcml

# trigger monkey patches
monkey.monkeyPatch()

def initialize(context):
    # load instance site configuration file
    site_zcml = os.path.join(INSTANCE_HOME, "etc", "site.zcml")
    zcml.process(site_zcml)
