##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

# usage see README.txt
from zope.generic.type.interfaces import *
from zope.generic.type.base import Object
from zope.generic.type.base import Contained
from zope.generic.type.base import Container
from zope.generic.type.base import Folder

from zope.generic.type.helper import acquireObjectConfiguration
from zope.generic.type.helper import createObject
from zope.generic.type.helper import createParameter
from zope.generic.type.helper import queryObjectConfiguration
from zope.generic.type.helper import queryTypeConfiguration
from zope.generic.type.helper import queryTypeInformation
