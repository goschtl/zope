##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Configuration directives

$Id: ConfigurationDirectiveInterfaces.py,v 1.2 2002/06/10 23:29:24 jim Exp $
"""
from Interface import Interface

class IEmptyDirective(Interface):

    def __call__(**kw):
        """Compute configuration actions

        Return a sequence of configuration actions. Each action is a
        tuple with:

        - A discriminator, value used to identify conflicting
          actions. Actions conflict if they have the same values
          for their discriminators.

        - callable object

        - argument tuple

        - and, optionally, a keyword argument dictionary.

        The callable object will be called with the argument tuple and
        keyword arguments to perform the action.
        """

class INonEmptyDirective(Interface):

    def __call__(**kw):
        """Compute complex directive handler

        Return an IComplexDirectiveHandler
        """

class ISubdirectiveHandler(Interface):
    """Handle subdirectives

    Provide mehods for registered subdirectives.

    Also provide a call that can provide additional configuration actions.
    """

    def __call__():
        """Return a sequence of configuration actions."""
