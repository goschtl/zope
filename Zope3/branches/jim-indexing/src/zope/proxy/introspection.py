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

# XXX this module should bnecome unnecessary

"""Temporary hack module until there is a generic way to deal with proxies

This module provides some standard machinery to recognize and remove
proxies. It is hoped that it will be replaced by a cleaner implementation
based on a common proxy base class.

This module requires that proxy implementations register themselves with the
module, by calling defineProxyType, however, it short-circuits the definitions
for two types, which, hopefully will be the only two types that need to get
registered. ;)

$Id$
"""

import warnings
from zope.proxy._zope_proxy_proxy import removeAllProxies, isProxy

warnings.warn("The zope.proxy.introspection module is deprecated. "
              "Use zope.proxy instead.",
              DeprecationWarning, 2)
