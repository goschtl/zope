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
from zope.configuration import xmlconfig
import Products

_initialized = False
_global_context = None
def initialize(execute=True):
    """This gets called once to initialize ZCML enough.
    """
    global _initialized, _global_context
    if _initialized:
        return _global_context
    _initialized = True
    return _global_context

def reset():
    global _initialized, _global_context
    _initialized = False
    _global_context = None

def process(file, execute=True, package=None):
    """Process a ZCML file.

    Note that this can be called multiple times, unlike in Zope 3. This
    is needed because in Zope 2 we don't (yet) have a master ZCML file
    which can include all the others.
    """
    context = initialize()
    return xmlconfig.file(file, context=context, execute=execute,
                          package=package)

def string(s, execute=True):
    """Process a ZCML string.

    Note that this can be called multiple times, unlike in Zope 3. This
    is needed because in Zope 2 we don't (yet) have a master ZCML file
    which can include all the others.
    """
    context = initialize()
    return xmlconfig.string(s, context=context, execute=execute)

import os

def load_site():
    # load instance site configuration file
    site_zcml = os.path.join(INSTANCE_HOME, "etc", "site.zcml")
    if os.path.exists(site_zcml):
        process(site_zcml)
    else:
        fallback = os.path.join(os.path.dirname(__file__), "skel", "site.zcml")
        process(fallback)
