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
"""Zope configuration support

Software that wants to provide new config directives calls
zope.configuration.meta.register.
"""

def namespace(suffix):
    return 'http://namespaces.zope.org/'+suffix

import sys, os
from zope.configuration.xmlconfig import XMLConfig

def config(dir):
    try:
        XMLConfig(os.path.join(dir, 'site.zcml'))()
    except:
        # Use the ExceptionFormatter to provide XMLconfig debug info
        from zope.exceptions.exceptionformatter import format_exception
        exc_info = ['='*72, '\nZope Configuration Error\n', '='*72, '\n'] \
                   + apply(format_exception, sys.exc_info())
        sys.stderr.write(''.join(exc_info))
        sys.exit(0) # Fatal config error

__all__ = ["namespace", "config"]
