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
"""Configuration directives that do not have subdirectives

$Id: IEmptyDirective.py,v 1.1 2002/09/01 18:29:58 rdmurray Exp $
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
