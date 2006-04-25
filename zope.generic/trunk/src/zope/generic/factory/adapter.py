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

from zope.generic.informationprovider.api import queryInformation
from zope.generic.informationprovider.api import getInformationProvider
from zope.generic.keyface import IKeyfaced
from zope.generic.operation import IOperationConfiguration

from zope.generic.factory import IFactoryInformation
from zope.generic.factory import IInitializer



class Initializer(object):
    """Initialize an object."""

    implements(IInitializer)
    
    adapts(IKeyfaced)

    def __init__(self, context):
        self.context = context

    def __call__(self, *pos, **kws):

