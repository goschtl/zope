##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Convenience package for short imports

$Id$
"""

import warnings

warnings.warn('The use of the Products.Five.api module has been deprecated. '
              'Import directly from Products.Five instead for public API.',
              DeprecationWarning)

from browser import BrowserView, StandardMacros
from traversable import Traversable
from viewable import Viewable
