##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Adapter-style interface registry

See Adapter class.

$Id: implementor.py,v 1.2 2002/12/25 14:13:42 jim Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.interface.interfaces import IImplementorRegistry

class ImplementorRegistry:
    """Implementor-style interface registry
    """

    __implements__ = IImplementorRegistry

    # The implementation uses a mapping:
    #
    #  { provided_interface -> (registered_provides, component) }
    #
    # Where the registered provides is what was registered and
    # provided may be some base interface

    def __init__(self):
        self._reg = {}

    def _registerAllProvided(self, primary_provide, object, provide):
        # Registers a component using (require, provide) as a key.
        # Also registers superinterfaces of the provided interface,
        # stopping when the registry already has a component
        # that provides a more general interface or when the Base is Interface.

        reg = self._reg
        reg[provide] = (primary_provide, object)
        bases = getattr(provide, '__bases__', ())
        for base in bases:
            if base is Interface:
                # Never register the say-nothing Interface.
                continue
            existing = reg.get(base, None)
            if existing is not None:
                existing_provide = existing[0]
                if existing_provide is not primary_provide:
                    if not existing_provide.extends(primary_provide):
                        continue
                    # else we are registering a general component
                    # after a more specific component.
            self._registerAllProvided(primary_provide, object, base)


    def register(self, provide, object):
        if not IInterface.isImplementedBy(provide):
            raise TypeError(
                "The provide argument must be an interface (or None)")

        self._registerAllProvided(provide, object, provide)

    def get(self, provide, default=None):
        """
        Finds a registered component that provides the given interface.
        Returns None if not found.
        """
        c = self._reg.get(provide)
        if c is not None:
            return c[1]

        return default
