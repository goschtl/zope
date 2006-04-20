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

from zope.component import adapts
from zope.interface import implements

from zope.generic.informationprovider.api import provideInformation

from zope.generic.type import IInitializer
from zope.generic.type import IInitializerConfiguration
from zope.generic.type import ITypeable
from zope.generic.type.api import queryTypeConfiguration



class Initializer(object):
    """Initialize an object."""

    implements(IInitializer)
    
    adapts(ITypeable)

    def __init__(self, context):
        self.context = context

    def __call__(self, *pos, **kws):
        config = queryTypeConfiguration(self.context, IInitializerConfiguration)
        if config:
            # store initialization data
            if config.keyface:
                provideInformation(self.context, config.keyface, kws)

            # invoke initialization handler

            if config.handler:
                config.handler(self.context, *pos, **kws)
