##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""ZCML machinery

$Id$
"""
import os
from zope.configuration import xmlconfig

_initialized = False

def load_site():
    """Load the appropriate ZCML file.

    Note that this can be called multiple times, unlike in Zope 3. This
    is needed because in Zope 2 we don't (yet) have a master ZCML file
    which can include all the others.
    """
    global _initialized
    if _initialized:
        return
    _initialized = True

    # load instance site configuration file
    site_zcml = os.path.join(INSTANCE_HOME, "etc", "site.zcml")
    if os.path.exists(site_zcml):
        file = site_zcml
    else:
        file = os.path.join(os.path.dirname(__file__), "skel", "site.zcml")
    xmlconfig.file(file)
