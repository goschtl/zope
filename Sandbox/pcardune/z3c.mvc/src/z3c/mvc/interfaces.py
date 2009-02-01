##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""model, view, controller interfaces.

$Id$
"""
__docformat__ = 'restructuredtext'


from zope.interface import Interface
from zope.pagetemplate.interfaces import IPageTemplate

class IModelProvider(Interface):

    def getModel():
        """returns a model to be used by a view template."""


class IModelTemplate(IPageTemplate):
    """Template for use by a controller."""
