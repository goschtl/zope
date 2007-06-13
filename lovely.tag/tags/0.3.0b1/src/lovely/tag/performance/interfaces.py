##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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

from zope import interface
from zope import schema

from zope.app.container import constraints
from zope.app.container.interfaces import IContainer


class IUrl(interface.Interface):
    constraints.containers('.IUrlContainer')

    url = schema.TextLine(
            title = u'URL',
            required = True,
            )


class IUrlContainer(IContainer):
    constraints.contains(IUrl)


class IPerformanceTestSite(interface.Interface):
    """A site for the perfomance test"""

