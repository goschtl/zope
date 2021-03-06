##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
""" Z2 -> Z3 bridge utilities.

$Id$
"""

from Interface._InterfaceClass import Interface as Z2_InterfaceClass
from Interface import Interface as Z2_Interface
from Interface import Attribute as Z2_Attribute

from zope.interface.interface import InterfaceClass as Z3_InterfaceClass
from zope.interface.interface import Interface as Z3_Interface
from zope.interface.interface import Attribute as Z3_Attribute

def fromZ2Interface(z2i):

    """ Return a Zope 3 interface corresponding to 'z2i'.

    o 'z2i' must be a Zope 2 interface.
    """
    if not isinstance(z2i, Z2_InterfaceClass):
        raise ValueError, 'Not a Zope 2 interface!'

    if z2i is Z2_Interface:  # special case; root in new hierarchy!
        return Z3_Interface

    name = z2i.getName()

    bases = [ fromZ2Interface(x) for x in z2i.getBases() ]

    attrs = {}

    for k, v in z2i.namesAndDescriptions():

        if isinstance(v, Z2_Attribute):
            v = fromZ2Attribute(v)

        attrs[k] = v

    # XXX: Note that we pass the original interface's __module__;
    #      we may live to regret that.
    return Z3_InterfaceClass(name=name,
                             bases=bases,
                             attrs=attrs,
                             __doc__=z2i.getDoc(),
                             __module__=z2i.__module__,
                            )

def fromZ2Attribute(z2a):

    """ Return a Zope 3 interface attribute corresponding to 'z2a'.

    o 'z2a' must be a Zope 2 interface attribute.
    """
    if not isinstance(z2a, Z2_Attribute):
        raise ValueError, 'Not a Zope 2 interface attribute!'

    return Z3_Attribute(z2a.getName(), z2a.getDoc())
