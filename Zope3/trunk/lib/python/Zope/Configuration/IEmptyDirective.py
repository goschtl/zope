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

$Id: IEmptyDirective.py,v 1.2 2002/09/18 17:02:22 rdmurray Exp $
"""
from Interface import Interface

class IEmptyDirective(Interface):

    def __call__(context,**kw):
        """Compute configuration actions

        context -- an execution context that the directive may use for
          things like resolving names

        kw -- a dictionary containing the values of any attributes
          that were specified on the directive

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
