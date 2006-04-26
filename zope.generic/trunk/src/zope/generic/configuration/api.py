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

__docformat__ = 'restructuredtext'

from zope.generic.configuration import *
from zope.generic.configuration.adapter import AttributeConfigurations
from zope.generic.configuration.base import ConfigurationData
from zope.generic.configuration.helper import parameterToConfiguration
from zope.generic.configuration.helper import configuratonToDict
from zope.generic.configuration.helper import requiredInOrder



def getConfiguration(context, configuration):
    """Evaluate a configuration."""
    return configuration(IConfigurations(context))



def queryConfiguration(context, configuration, default=None):
    """Evaluate a configuration or return default."""
    try:
        return getConfiguration(context, configuration)
    
    except:
        return default
