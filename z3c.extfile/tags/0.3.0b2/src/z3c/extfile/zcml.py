##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id$
"""
__docformat__ = "reStructuredText"

import os

from zope import interface
from zope import schema
from zope.component import zcml
from zope.configuration.fields import Path, Tokens
from interfaces import IHashDir
from z3c.extfile import hashdir

class IHashDirDirective(interface.Interface):
    """Parameters for the cache settings directive."""

    path = Path(title = u'Path',
                required=True)

    fallbacks = Tokens(title = u'Fallbacks',
                       value_type=path,
                       required=False)

def hashDirDirective(_context, path, fallbacks=(), permission=None):
    """Function to create hashdir utility"""

    util = hashdir.HashDir(path, fallbacks=fallbacks)
    zcml.utility(_context,
                 provides=IHashDir,
                 component=util,
                 permission=permission,
                 name='')


