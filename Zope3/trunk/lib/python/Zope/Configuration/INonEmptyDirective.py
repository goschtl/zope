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
"""Configuration directives that have subdirectives

$Id: INonEmptyDirective.py,v 1.4 2002/09/18 17:02:22 rdmurray Exp $
"""
from Interface import Interface

class INonEmptyDirective(Interface):

    def __call__(context,**kw):
        """Compute subdirective handler

        context -- an execution context that the directive may use for
          things like resolving names

        kw -- a dictionary containing the values of any attributes
          that were specified on the directive

        Return an ISubdirectiveHandler.
        """
