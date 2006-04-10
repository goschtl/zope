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
from zope.generic.configuration.base import ConfigurationData
from zope.generic.configuration.interfaces import *
from zope.generic.configuration.helper import deleteConfigurationData
from zope.generic.configuration.helper import provideConfigurationData
from zope.generic.configuration.helper import queryConfigurationData
from zope.generic.configuration.helper import queryConfigurationHandler
from zope.generic.configuration.helper import queryConfigurationInformation
